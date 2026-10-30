"""Robust lattice indexing with perspective and optional smooth pixel geometry."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

import cv2
import numpy as np

from digital_pen.types import DotObservation, LatticeModel, SplineWarp
from digital_pen.vision.perspective import (
    estimate_homography,
    fit_spline_warp,
    inverse_project_lattice,
    inverse_project_points,
    median_grid_spacing,
    project_lattice,
    project_points,
    refine_homography,
    validate_lattice_region,
)


@dataclass(frozen=True)
class GridFitterConfig:
    neighbor_count: int = 8
    angle_bins: int = 180
    max_offset_ratio: float = 0.42
    axis_tolerance_ratio: float = 0.16
    phase_tolerance_ratio: float = 0.09
    max_iterations: int = 8
    local_warp_enabled: bool = True
    local_tile_cells: float = 13.0
    spline_spacing_grid: float = 6.0
    spline_regularization: float = 0.01
    # Optional known dot pitch (fixed pen optics). When set, the lattice axes
    # come from the 4-fold symmetry of near-pitch neighbour vectors instead of
    # the blind angle histogram, which can lock onto a wrong basis in a view
    # of only ~100 dots.
    expected_spacing_px: float | None = None

    def __post_init__(self) -> None:
        if self.neighbor_count < 4:
            raise ValueError("neighbor_count must be at least four")
        if self.angle_bins < 36:
            raise ValueError("angle_bins must be at least 36")
        if not 0 < self.max_offset_ratio < 0.5:
            raise ValueError("max_offset_ratio must be between zero and 0.5")
        if not 0 < self.axis_tolerance_ratio < 0.5:
            raise ValueError("axis_tolerance_ratio must be between zero and 0.5")
        if not 0 < self.phase_tolerance_ratio < 0.25:
            raise ValueError("phase_tolerance_ratio must be between zero and 0.25")
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be positive")
        if (
            not np.isfinite(self.local_tile_cells)
            or not np.isfinite(self.spline_spacing_grid)
            or self.local_tile_cells < 8
            or self.spline_spacing_grid < 4
        ):
            raise ValueError(
                "local tiles and spline spacing must retain spatial support"
            )
        if (
            not np.isfinite(self.spline_regularization)
            or self.spline_regularization <= 0
        ):
            raise ValueError("spline regularization must be positive")
        if self.expected_spacing_px is not None and (
            not np.isfinite(self.expected_spacing_px) or self.expected_spacing_px <= 0
        ):
            raise ValueError("expected_spacing_px must be positive and finite")


@dataclass(frozen=True)
class GridAssignment:
    observation_index: int
    row: int
    col: int
    residual_grid: tuple[float, float]
    reprojection_error_px: float


@dataclass(frozen=True)
class GridFitResult:
    model: LatticeModel
    assignments: list[GridAssignment]
    inlier_mask: np.ndarray
    inlier_ratio: float
    offset_ratio: float

    @property
    def geometry_confidence(self) -> float:
        """A fit-support score, not a calibrated probability of correctness."""
        return self.inlier_ratio / (1 + self.model.rms_error_px / self.model.spacing_px)


def _circular_distance(values: np.ndarray, phase: float) -> np.ndarray:
    return np.abs((values - phase + 0.5) % 1.0 - 0.5)


def _estimate_phase(values: np.ndarray, tolerance: float) -> float:
    residues = np.mod(values, 1.0)
    # Unshifted dots make the largest of the three Anoto residual clusters.
    scores = np.array(
        [
            np.sum(
                np.maximum(
                    0.0,
                    1.0 - _circular_distance(residues, item) / tolerance,
                )
            )
            for item in residues
        ]
    )
    phase = float(residues[int(np.argmax(scores))])
    close = _circular_distance(residues, phase) < tolerance
    signed = (residues[close] - phase + 0.5) % 1.0 - 0.5
    return float((phase + np.median(signed)) % 1.0)


def _neighbor_vectors(points: np.ndarray, count: int) -> np.ndarray:
    neighbor_count = min(count, len(points) - 1)
    if len(points) <= 512:
        delta = points[None, :, :] - points[:, None, :]
        distance_sq = np.sum(delta * delta, axis=2)
        np.fill_diagonal(distance_sq, np.inf)
        neighbors = np.argpartition(distance_sq, neighbor_count, axis=1)[
            :, :neighbor_count
        ]
    else:
        # Keep full-page (typically 3025-dot) fitting bounded in memory.
        source = points.astype(np.float32)
        index = cv2.flann_Index(source, {"algorithm": 1, "trees": 4})
        candidates, _ = index.knnSearch(
            source, neighbor_count + 1, params={"checks": 64}
        )
        neighbors = np.empty((len(points), neighbor_count), dtype=np.int32)
        for row, candidate_indices in enumerate(candidates):
            without_self = candidate_indices[candidate_indices != row]
            if len(without_self) < neighbor_count:
                raise ValueError("could not find enough distinct neighboring points")
            neighbors[row] = without_self[:neighbor_count]
    vectors = points[neighbors] - points[:, None, :]
    return vectors.reshape(-1, 2)


def _estimate_basis(points: np.ndarray, config: GridFitterConfig) -> np.ndarray:
    vectors = _neighbor_vectors(points, config.neighbor_count)
    lengths = np.linalg.norm(vectors, axis=1)
    usable = np.isfinite(lengths) & (lengths > 1e-6)
    vectors = vectors[usable]
    lengths = lengths[usable]
    if len(vectors) < 8:
        raise ValueError("not enough distinct neighboring points to estimate a grid")

    angles = np.mod(np.arctan2(vectors[:, 1], vectors[:, 0]), np.pi)
    bins = config.angle_bins
    indices = np.floor(angles * bins / np.pi).astype(int) % bins
    typical = float(np.percentile(lengths, 15))
    weights = 1.0 / np.maximum(lengths, typical * 0.35)
    histogram = np.bincount(indices, weights=weights, minlength=bins)
    # Smooth circularly, then score orthogonal angle pairs together.
    histogram = sum(np.roll(histogram, shift) for shift in range(-3, 4))
    quarter_turn = bins // 2
    pair_score = histogram + np.roll(histogram, -quarter_turn)
    peak = int(np.argmax(pair_score))
    angle = (peak + 0.5) * np.pi / bins

    units = np.array(
        [
            [np.cos(angle), np.sin(angle)],
            [-np.sin(angle), np.cos(angle)],
        ]
    )
    basis_vectors: list[np.ndarray] = []
    angular_tolerance = np.deg2rad(13.0)
    for unit in units:
        projections = vectors @ unit
        perpendicular = np.abs(vectors[:, 0] * unit[1] - vectors[:, 1] * unit[0])
        aligned = (np.abs(projections) > 1e-6) & (
            np.arctan2(perpendicular, np.abs(projections)) < angular_tolerance
        )
        candidates = vectors[aligned].copy()
        projected = projections[aligned]
        candidates[projected < 0] *= -1.0
        projected = np.abs(projected)
        if len(candidates) < 4:
            raise ValueError("could not find two supported lattice directions")
        # Direction offsets split adjacent lengths into several clusters. The
        # true basis is the densest *vector* cluster (equal offsets cancel),
        # while a 1-D length mode can confuse it with a shifted neighbor.
        bandwidth = max(0.6, float(np.percentile(projected, 20)) * 0.10)
        sample_count = min(len(candidates), 2048)
        sample_indices = np.linspace(
            0, len(candidates) - 1, sample_count, dtype=np.int32
        )
        sample = candidates[sample_indices]
        cluster_distance = np.linalg.norm(
            sample[:, None, :] - sample[None, :, :], axis=2
        )
        density = np.count_nonzero(cluster_distance < bandwidth, axis=1)
        mode = sample[int(np.argmax(density))]
        local = np.linalg.norm(candidates - mode, axis=1) < bandwidth * 1.5
        basis_vectors.append(np.median(candidates[local], axis=0))

    first, second = basis_vectors
    if abs(first[0]) >= abs(second[0]):
        horizontal, vertical = first, second
    else:
        horizontal, vertical = second, first
    if horizontal[0] < 0:
        horizontal = -horizontal
    if vertical[1] < 0:
        vertical = -vertical
    basis = np.column_stack((horizontal, vertical))
    if abs(float(np.linalg.det(basis))) < 1e-6:
        raise ValueError("estimated lattice basis is degenerate")
    return basis


def _estimate_basis_known_spacing(
    points: np.ndarray, config: GridFitterConfig
) -> np.ndarray:
    spacing = float(config.expected_spacing_px)
    vectors = _neighbor_vectors(points, config.neighbor_count)
    lengths = np.linalg.norm(vectors, axis=1)
    # Neighbours with equal offset directions differ by exactly one lattice
    # vector, so the lattice is the densest (angle mod 90, length) cluster;
    # offset-perturbed vectors spread out. Allow +-25 % apparent scale (tilt).
    near = (lengths > 0.75 * spacing) & (lengths < 1.25 * spacing)
    if np.count_nonzero(near) < 8:
        raise ValueError("not enough near-pitch neighbors to estimate a grid")
    angles = np.degrees(np.arctan2(vectors[near, 1], vectors[near, 0])) % 90.0
    histogram, _, _ = np.histogram2d(
        angles, lengths[near] / spacing, bins=(90, 25), range=((0, 90), (0.75, 1.25))
    )
    padded = np.pad(histogram, ((1, 1), (1, 1)), mode="wrap")
    padded[:, 0] = padded[:, -1] = 0  # length does not wrap
    smoothed = sum(
        padded[1 + da : 91 + da, 1 + dl : 26 + dl]
        for da in (-1, 0, 1)
        for dl in (-1, 0, 1)
    )
    angle_bin, length_bin = np.unravel_index(int(np.argmax(smoothed)), smoothed.shape)
    angle = np.radians(angle_bin + 0.5)
    length = spacing * (0.75 + (length_bin + 0.5) * 0.02)
    basis_vectors = []
    for unit in (
        np.array([np.cos(angle), np.sin(angle)]),
        np.array([-np.sin(angle), np.cos(angle)]),
    ):
        candidates = np.concatenate((vectors, -vectors))
        close = np.linalg.norm(candidates - unit * length, axis=1) < 0.12 * length
        basis_vectors.append(
            np.median(candidates[close], axis=0) if close.sum() >= 4 else unit * length
        )
    first, second = basis_vectors
    if abs(first[0]) >= abs(second[0]):
        horizontal, vertical = first, second
    else:
        horizontal, vertical = second, first
    if horizontal[0] < 0:
        horizontal = -horizontal
    if vertical[1] < 0:
        vertical = -vertical
    basis = np.column_stack((horizontal, vertical))
    if abs(float(np.linalg.det(basis))) < 1e-6:
        raise ValueError("estimated lattice basis is degenerate")
    return basis


def _axis_offsets(residuals: np.ndarray, offset_ratio: float) -> np.ndarray:
    offsets = np.zeros_like(residuals)
    if offset_ratio <= 0:
        return offsets
    dominant = np.argmax(np.abs(residuals), axis=1)
    rows = np.arange(len(residuals))
    offsets[rows, dominant] = np.sign(residuals[rows, dominant]) * offset_ratio
    return offsets


def _estimate_offset_ratio(residuals: np.ndarray, axis_tolerance: float) -> float:
    absolute = np.abs(residuals)
    minor = np.min(absolute, axis=1)
    major = np.max(absolute, axis=1)
    cross_like = (minor < axis_tolerance) & (major < 0.45)
    values = major[cross_like]
    if len(values) == 0 or float(np.median(values)) < 0.055:
        return 0.0
    return float(np.median(values))


def _fit_projective_grid(
    observations: list[DotObservation],
    config: GridFitterConfig | None = None,
) -> GridFitResult:
    """Fit a perspective lattice, retaining robust index assignments."""
    settings = config or GridFitterConfig()
    if len(observations) < 16:
        raise ValueError("at least 16 dot observations are required")
    points = np.asarray([item.center_px for item in observations], dtype=np.float64)
    if not np.all(np.isfinite(points)) or len(np.unique(points, axis=0)) < 8:
        raise ValueError("dot centers must contain finite, distinct points")

    basis = (
        _estimate_basis(points, settings)
        if settings.expected_spacing_px is None
        else _estimate_basis_known_spacing(points, settings)
    )
    anchor = np.median(points, axis=0)
    approximate = (points - anchor) @ np.linalg.inv(basis).T
    phase = np.array(
        [
            _estimate_phase(approximate[:, axis], settings.phase_tolerance_ratio)
            for axis in range(2)
        ]
    )
    indices = np.rint(approximate - phase).astype(np.int32)
    initial_spacing = float(np.mean(np.linalg.norm(basis, axis=0)))
    homography, inliers = estimate_homography(
        indices,
        points,
        ransac_threshold_px=initial_spacing * 0.46,
    )

    offset_ratio = 0.0
    for _ in range(settings.max_iterations):
        normalized = inverse_project_points(points, homography)
        new_indices = np.rint(normalized).astype(np.int32)
        residuals = normalized - new_indices
        candidate_offset = min(
            settings.max_offset_ratio,
            _estimate_offset_ratio(residuals[inliers], settings.axis_tolerance_ratio),
        )
        corrected = new_indices + _axis_offsets(residuals, candidate_offset)
        spacing = median_grid_spacing(homography, new_indices[inliers])
        new_homography, ransac_mask = estimate_homography(
            corrected,
            points,
            ransac_threshold_px=max(0.65, spacing * 0.085),
        )
        projected = project_points(corrected, new_homography)
        errors = np.linalg.norm(projected - points, axis=1)
        pattern_mask = (
            np.min(np.abs(residuals), axis=1) < settings.axis_tolerance_ratio
        ) & (np.max(np.abs(residuals), axis=1) <= settings.max_offset_ratio + 0.03)
        new_inliers = ransac_mask & pattern_mask
        if np.count_nonzero(new_inliers) < 8:
            raise ValueError("too few lattice inliers after robust fitting")
        movement = np.max(
            np.linalg.norm(
                project_points(corrected, new_homography)
                - project_points(corrected, homography),
                axis=1,
            )
        )
        converged = (
            np.array_equal(new_indices, indices)
            and np.array_equal(new_inliers, inliers)
            and movement < 1e-4
        )
        indices = new_indices
        inliers = new_inliers
        homography = new_homography
        offset_ratio = candidate_offset
        if converged:
            break

    normalized = inverse_project_points(points, homography)
    indices = np.rint(normalized).astype(np.int32)
    residuals = normalized - indices
    corrected = indices + _axis_offsets(residuals, offset_ratio)
    projected = project_points(corrected, homography)
    errors = np.linalg.norm(projected - points, axis=1)
    spacing = median_grid_spacing(homography, indices[inliers])
    final_mask = inliers & (errors < max(0.75, spacing * 0.09))
    if np.count_nonzero(final_mask) < 8:
        raise ValueError("too few final lattice inliers")

    # RANSAC selects the robust support; refit all selected correspondences so
    # the public model and RMS describe the final least-squares optimum.
    homography = refine_homography(
        corrected[final_mask],
        points[final_mask],
    )
    normalized = inverse_project_points(points, homography)
    indices = np.rint(normalized).astype(np.int32)
    residuals = normalized - indices
    offset_ratio = min(
        settings.max_offset_ratio,
        _estimate_offset_ratio(residuals[final_mask], settings.axis_tolerance_ratio),
    )
    corrected = indices + _axis_offsets(residuals, offset_ratio)
    homography = refine_homography(corrected[final_mask], points[final_mask])
    projected = project_points(corrected, homography)
    errors = np.linalg.norm(projected - points, axis=1)

    minimum = np.min(indices[final_mask], axis=0)
    normalized_indices = indices - minimum
    translation = np.array(
        [[1.0, 0.0, minimum[0]], [0.0, 1.0, minimum[1]], [0.0, 0.0, 1.0]]
    )
    homography = homography @ translation
    spacing = median_grid_spacing(homography, normalized_indices[final_mask])
    rms = float(np.sqrt(np.mean(np.square(errors[final_mask]))))
    model = LatticeModel(
        grid_to_image=homography.astype(np.float64),
        spacing_px=spacing,
        rms_error_px=rms,
    )
    assignments = [
        GridAssignment(
            observation_index=index,
            row=int(normalized_indices[index, 1]),
            col=int(normalized_indices[index, 0]),
            residual_grid=(float(residuals[index, 0]), float(residuals[index, 1])),
            reprojection_error_px=float(errors[index]),
        )
        for index in np.flatnonzero(final_mask)
    ]
    return GridFitResult(
        model=model,
        assignments=assignments,
        inlier_mask=final_mask,
        inlier_ratio=float(np.count_nonzero(final_mask) / len(points)),
        offset_ratio=offset_ratio,
    )


def _local_correspondences(
    observations: list[DotObservation],
    settings: GridFitterConfig,
    spacing: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """Join overlapping local lattices through shared observation identities."""
    points = np.array([item.center_px for item in observations])
    low, high = points.min(axis=0), points.max(axis=0)
    tiles = []
    windows = (
        (x, y, size)
        for size in (spacing * settings.local_tile_cells,)
        for y in np.arange(low[1], high[1], size * 0.6)
        for x in np.arange(low[0], high[0], size * 0.6)
    )
    for x, y, tile_size in windows:
        selected = np.flatnonzero(
            (points[:, 0] >= x)
            & (points[:, 0] < x + tile_size)
            & (points[:, 1] >= y)
            & (points[:, 1] < y + tile_size)
        )
        if len(selected) < 36:
            continue
        try:
            local = _fit_projective_grid([observations[i] for i in selected], settings)
        except (ValueError, np.linalg.LinAlgError):
            continue
        cells = {
            int(selected[item.observation_index]): (item.col, item.row)
            for item in local.assignments
        }
        extent = np.ptp(np.array(list(cells.values())), axis=0) + 1
        occupancy = len(set(cells.values())) / float(np.prod(extent))
        if len(cells) < max(36, 0.45 * len(selected)) or occupancy < 0.5:
            continue
        directions = {}
        for item in local.assignments:
            vector = np.zeros(2)
            axis = int(np.argmax(np.abs(item.residual_grid)))
            vector[axis] = np.sign(item.residual_grid[axis])
            directions[int(selected[item.observation_index])] = tuple(vector)
        tiles.append((cells, local.offset_ratio, directions))
    if not tiles:
        raise ValueError("no supported local lattice seeds")

    edges: list[list[tuple[int, np.ndarray]]] = [[] for _ in tiles]
    for first in range(len(tiles)):
        for second in range(first + 1, len(tiles)):
            overlap = tiles[first][0].keys() & tiles[second][0].keys()
            if len(overlap) < 12:
                continue
            differences = Counter(
                tuple(np.subtract(tiles[first][0][i], tiles[second][0][i]))
                for i in overlap
            )
            shift, support = differences.most_common(1)[0]
            if support / len(overlap) < 0.8:
                continue
            translation = np.array(shift)
            edges[first].append((second, translation))
            edges[second].append((first, -translation))

    components = []
    unseen = set(range(len(tiles)))
    while unseen:
        anchor = max(unseen, key=lambda i: len(tiles[i][0]))
        offsets = {anchor: np.zeros(2, dtype=int)}
        queue = [anchor]
        while queue:
            current = queue.pop()
            for neighbor, translation in edges[current]:
                proposed = offsets[current] + translation
                if neighbor not in offsets:
                    offsets[neighbor] = proposed
                    queue.append(neighbor)
        unseen.difference_update(offsets)
        support = set().union(*(tiles[i][0].keys() for i in offsets))
        components.append((len(support), offsets))
    _, offsets = max(components, key=lambda item: item[0])
    votes: dict[int, Counter] = {}
    direction_votes: dict[int, Counter] = {}
    for tile, translation in offsets.items():
        for index, cell in tiles[tile][0].items():
            votes.setdefault(index, Counter())[tuple(np.array(cell) + translation)] += 1
            direction_votes.setdefault(index, Counter())[tiles[tile][2][index]] += 1
    kept, grid, directions = [], [], []
    for index, candidates in sorted(votes.items()):
        cell, count = candidates.most_common(1)[0]
        if count / candidates.total() >= 0.8:
            kept.append(index)
            grid.append(cell)
            directions.append(direction_votes[index].most_common(1)[0][0])
    if len(kept) < 100:
        raise ValueError("too few mutually consistent local lattice assignments")
    offset = float(np.median([tiles[i][1] for i in offsets]))
    return (
        np.array(kept),
        np.array(grid, dtype=float),
        np.array(directions) * offset,
        offset,
    )


def _connected_field_mask(indices: np.ndarray, mask: np.ndarray) -> np.ndarray:
    cells = {tuple(cell) for cell in indices[mask]}
    largest: set[tuple[int, int]] = set()
    while cells:
        component = {cells.pop()}
        queue = list(component)
        while queue:
            col, row = queue.pop()
            for neighbor in (
                (col - 1, row),
                (col + 1, row),
                (col, row - 1),
                (col, row + 1),
            ):
                if neighbor in cells:
                    cells.remove(neighbor)
                    component.add(neighbor)
                    queue.append(neighbor)
        if len(component) > len(largest):
            largest = component
    return mask & np.array([tuple(cell) in largest for cell in indices])


def _fit_smooth_grid(
    observations: list[DotObservation],
    settings: GridFitterConfig,
    spacing: float,
) -> GridFitResult:
    points = np.array([item.center_px for item in observations])
    seed_indices, seed_grid, seed_offsets, offset = _local_correspondences(
        observations, settings, spacing
    )
    corrected = seed_grid + seed_offsets
    homography = refine_homography(corrected, points[seed_indices])
    # Local correspondences fix integer phase before a smooth global residual
    # is fitted. Direction identities come from each local homography below.
    # The first global H may be several pixels from curved paper at the edges.
    warp = fit_spline_warp(
        corrected,
        points[seed_indices],
        homography,
        spacing_grid=settings.spline_spacing_grid,
        regularization=settings.spline_regularization,
    )
    lattice = LatticeModel(homography, spacing, 0.0, warp)
    support_cells = {tuple(cell.astype(int)) for cell in seed_grid}
    minimum, maximum = seed_grid.min(axis=0), seed_grid.max(axis=0)
    previous_mask = np.zeros(len(points), dtype=bool)
    for _ in range(settings.max_iterations):
        normalized = inverse_project_lattice(points, lattice)
        indices = np.rint(normalized).astype(int)
        residual = normalized - indices
        offset = min(
            settings.max_offset_ratio,
            _estimate_offset_ratio(
                residual[seed_indices], settings.axis_tolerance_ratio
            ),
        )
        corrected = indices + _axis_offsets(residual, offset)
        errors = np.linalg.norm(project_lattice(corrected, lattice) - points, axis=1)
        supported = np.array(
            [
                sum(
                    (col + dx, row + dy) in support_cells
                    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))
                )
                >= 2
                for col, row in indices
            ]
        )
        # Overlapping local fits already supply spatial support for their
        # agreed cells. A camera edge or missing neighbor must not erase that
        # evidence while the current mapping still agrees with the seed.
        supported[seed_indices] |= np.all(
            indices[seed_indices] == seed_grid, axis=1
        )
        mask = (
            supported
            & np.all((indices >= minimum) & (indices <= maximum), axis=1)
            & (np.min(np.abs(residual), axis=1) < settings.axis_tolerance_ratio)
            & (np.max(np.abs(residual), axis=1) <= settings.max_offset_ratio + 0.03)
            & (errors < max(0.75, spacing * 0.09))
        )
        mask = _connected_field_mask(indices, mask)
        if mask.sum() < 100:
            raise ValueError("too few supported observations for smooth fitting")
        support_cells.update(tuple(cell) for cell in indices[mask])
        homography = refine_homography(corrected[mask], points[mask])
        warp = fit_spline_warp(
            corrected[mask],
            points[mask],
            homography,
            spacing_grid=settings.spline_spacing_grid,
            regularization=settings.spline_regularization,
        )
        updated = LatticeModel(homography, spacing, 0.0, warp)
        movement = np.max(
            np.linalg.norm(
                project_lattice(corrected[mask], updated)
                - project_lattice(corrected[mask], lattice),
                axis=1,
            )
        )
        lattice = updated
        converged = np.array_equal(mask, previous_mask) and movement < 1e-4
        previous_mask = mask
        if converged:
            break
    normalized = inverse_project_lattice(points, lattice)
    indices = np.rint(normalized).astype(int)
    residual = normalized - indices
    corrected = indices + _axis_offsets(residual, offset)
    errors = np.linalg.norm(project_lattice(corrected, lattice) - points, axis=1)
    origin = indices[mask].min(axis=0)
    indices -= origin
    translation = np.array(
        [[1.0, 0.0, origin[0]], [0.0, 1.0, origin[1]], [0.0, 0.0, 1.0]]
    )
    warp = SplineWarp(
        tuple(np.array(warp.origin_grid) - origin), warp.spacing_grid, warp.coefficients
    )
    lattice = LatticeModel(
        homography @ translation,
        spacing,
        float(np.sqrt(np.mean(errors[mask] ** 2))),
        warp,
    )
    validate_lattice_region(
        lattice,
        tuple(indices[mask].min(axis=0) - 0.4),
        tuple(indices[mask].max(axis=0) + 0.4),
    )
    assignments = [
        GridAssignment(
            int(i),
            int(indices[i, 1]),
            int(indices[i, 0]),
            tuple(residual[i]),
            float(errors[i]),
        )
        for i in np.flatnonzero(mask)
    ]
    return GridFitResult(lattice, assignments, mask, float(mask.mean()), offset)


def fit_grid(
    observations: list[DotObservation],
    config: GridFitterConfig | None = None,
) -> GridFitResult:
    """Fit a perspective grid, adding a smooth field for larger curved scenes."""
    settings = config or GridFitterConfig()
    projective = _fit_projective_grid(observations, settings)
    if (
        not settings.local_warp_enabled
        or len(observations) < 600
    ):
        return projective
    try:
        smooth = _fit_smooth_grid(observations, settings, projective.model.spacing_px)
    except (ValueError, np.linalg.LinAlgError):
        return projective
    return (
        smooth if len(smooth.assignments) > len(projective.assignments) else projective
    )


def fit_lattice(
    observations: list[DotObservation],
    config: GridFitterConfig | None = None,
) -> LatticeModel:
    """Fit and return only the public lattice model."""
    return fit_grid(observations, config).model
