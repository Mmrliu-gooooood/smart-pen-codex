"""Fast page localization for a fixed overhead camera.

Maps any image pixel (e.g. the pen tip) to a page coordinate, wherever the
paper lies under the camera. Designed for live use: it is re-run only when the
paper moves, so roughly a few hundred milliseconds per full frame suffice.

1. Dots: difference-of-Gaussians maxima with sub-pixel interpolation (no
   per-dot photometric fitting).
2. Seed: the blind projective lattice fit on the dots nearest to a seed point,
   offset classification, and Anoto window consensus on a central crop. This
   fixes the page identity (origin, rotation, mirror) from the dots alone.
3. Growth: the printed position of every page dot is known from the Generator
   matrix, so detections are associated to predicted printed positions and a
   page->image model (homography + smooth spline residual) is refitted over a
   growing trust radius until it covers the visible page.
4. Check: the share of in-frame printed dots with an associated detection and
   the residual RMS are reported; a wrong identity cannot reach either.

Page coordinates are Generator grid units: ``u`` to the right, ``v`` upward,
dot (u, v) printed at (u, v) + offset in its direction. Multiply by the grid
spacing for millimetres.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

from digital_pen.anoto import (
    AnotoCodecAdapter,
    AnotoDecodeError,
    build_direction_matrices,
    decode_oriented_consensus,
    image_grid_to_page,
)
from digital_pen.types import DotObservation, LatticeModel, SplineWarp
from digital_pen.vision.direction_classifier import classify_grid_fit
from digital_pen.vision.grid_fitter import GridFitterConfig, fit_grid
from digital_pen.vision.perspective import (
    inverse_project_lattice,
    project_lattice,
    project_points,
    refine_homography,
    spline_basis,
)

# Page-axis unit offsets in DotDirection order (UP, LEFT, RIGHT, DOWN); the
# page v axis points up, so UP is +v.
PAGE_OFFSETS = np.array(((0.0, 1.0), (-1.0, 0.0), (1.0, 0.0), (0.0, -1.0)))


@dataclass(frozen=True)
class PageLayout:
    """Printed geometry of one page, from the Generator matrix."""

    page_id: str
    section: tuple[int, int]
    spacing_mm: float
    offset_ratio: float
    directions: np.ndarray  # [row=v, col=u] DotDirection values

    @classmethod
    def from_manifest(cls, path: str | Path) -> PageLayout:
        path = Path(path)
        manifest = json.loads(path.read_text(encoding="utf-8"))
        matrix_path = Path(manifest["matrix_json"])
        if not matrix_path.exists():
            matrix_path = path.with_name(matrix_path.name)
        bits = np.asarray(json.loads(matrix_path.read_text(encoding="utf-8")))
        return cls(
            page_id=str(manifest["page_id"]),
            section=(int(manifest["section_u"]), int(manifest["section_v"])),
            spacing_mm=float(manifest["grid_spacing_mm"]),
            offset_ratio=float(manifest["offset_mm"])
            / float(manifest["grid_spacing_mm"]),
            directions=(bits[:, :, 0] + 2 * bits[:, :, 1]).astype(int),
        )

    @property
    def shape(self) -> tuple[int, int]:
        return self.directions.shape

    def printed_positions(self) -> tuple[np.ndarray, np.ndarray]:
        """Integer page cells (u, v) and printed dot positions, in grid units."""
        rows, cols = np.indices(self.shape)
        cells = np.column_stack((cols.ravel(), rows.ravel())).astype(float)
        printed = cells + PAGE_OFFSETS[self.directions.ravel()] * self.offset_ratio
        return cells, printed


@dataclass(frozen=True)
class PageLocatorConfig:
    expected_spacing_px: float | None = None
    min_relative_response: float = 0.2
    min_response: float = 1.5
    seed_dots: int = 700
    seed_attempts: int = 4
    decode_cells: int = 14
    min_direction_confidence: float = 0.75
    min_supporting_windows: int = 2
    max_missing_directions: int = 1
    allow_mirror: bool = True
    # Region growing: each step only admits dots within this many cells of
    # already associated dots, so the model never extrapolates far enough to
    # slip by a whole row beside a hand or at an image edge.
    growth_step_grid: float = 3.0
    max_growth_steps: int = 40
    settle_passes: int = 2
    association_ratio: float = 0.22
    # Chosen on the ten development frames only (not the old100 set).
    spline_spacing_grid: float = 4.0
    spline_regularization: float = 0.05
    min_associated: int = 120
    min_support: float = 0.5
    max_rms_ratio: float = 0.08

    def __post_init__(self) -> None:
        if self.decode_cells < 6 or self.seed_dots < 64 or self.seed_attempts < 1:
            raise ValueError("decode crop, seed size and attempts are too small")
        if not 0 < self.association_ratio < 0.3:
            raise ValueError("association_ratio must be within (0, 0.3)")


@dataclass(frozen=True)
class PageLocation:
    """A page->image model valid over the visible page region."""

    layout: PageLayout
    model: LatticeModel  # grid coordinates are page (u, v)
    rotation_quadrants: int
    mirrored: bool
    associated: int
    expected_visible: int
    rms_px: float
    supporting_windows: int
    timings_ms: dict[str, float] = field(default_factory=dict)

    @property
    def support(self) -> float:
        return self.associated / max(1, self.expected_visible)

    def page_to_pixel(self, page_points: np.ndarray) -> np.ndarray:
        return project_lattice(
            np.asarray(page_points, float).reshape(-1, 2), self.model
        )

    def pixel_to_page(self, pixels: np.ndarray) -> np.ndarray:
        return inverse_project_lattice(
            np.asarray(pixels, float).reshape(-1, 2), self.model
        )

    def pixel_to_mm(self, pixels: np.ndarray) -> np.ndarray:
        return self.pixel_to_page(pixels) * self.layout.spacing_mm


def detect_dots_fast(
    gray: np.ndarray, config: PageLocatorConfig | None = None
) -> np.ndarray:
    """Sub-pixel DoG maxima of dark dots, as an (N, 2) pixel array."""
    settings = config or PageLocatorConfig()
    if not isinstance(gray, np.ndarray) or gray.ndim != 2 or gray.dtype != np.uint8:
        raise ValueError("gray must be a 2D uint8 NumPy array")
    if settings.expected_spacing_px is None:
        small, large, window = 1.0, 4.0, 5
    else:
        spacing = settings.expected_spacing_px
        small, large = max(0.6, 0.055 * spacing), max(1.3, 0.22 * spacing)
        window = max(3, int(round(spacing * 0.27)) | 1)
    image = gray.astype(np.float32)
    response = cv2.GaussianBlur(image, (0, 0), large) - cv2.GaussianBlur(
        image, (0, 0), small
    )
    strong = float(np.percentile(response, 99.5))
    threshold = max(settings.min_response, settings.min_relative_response * strong)
    peaks = (response == cv2.dilate(response, np.ones((window, window), np.uint8))) & (
        response > threshold
    )
    peaks[:3], peaks[-3:], peaks[:, :3], peaks[:, -3:] = False, False, False, False
    ys, xs = np.nonzero(peaks)
    centre = response[ys, xs]
    left, right = response[ys, xs - 1], response[ys, xs + 1]
    up, down = response[ys - 1, xs], response[ys + 1, xs]
    with np.errstate(divide="ignore", invalid="ignore"):
        dx = 0.5 * (left - right) / (left - 2 * centre + right)
        dy = 0.5 * (up - down) / (up - 2 * centre + down)
    dx = np.where(np.isfinite(dx), np.clip(dx, -0.5, 0.5), 0.0)
    dy = np.where(np.isfinite(dy), np.clip(dy, -0.5, 0.5), 0.0)
    return np.column_stack((xs + dx, ys + dy))


def _central_crop(directions, confidences, centre, cells):
    height, width = directions.shape
    rows, cols = min(cells, height), min(cells, width)
    col0 = int(np.clip(np.floor(centre[0] - (cols - 1) / 2 + 0.5), 0, width - cols))
    row0 = int(np.clip(np.floor(centre[1] - (rows - 1) / 2 + 0.5), 0, height - rows))
    return (
        directions[row0 : row0 + rows, col0 : col0 + cols],
        confidences[row0 : row0 + rows, col0 : col0 + cols],
        np.array([col0, row0], float),
    )


def _seed(points, anchor, layout, settings, adapter):
    """Blind lattice + decode on the dots nearest to ``anchor``.

    Returns page-coordinate / pixel correspondences of the seed dots, the
    orientation and the number of supporting windows.
    """
    order = np.argsort(np.linalg.norm(points - anchor, axis=1))[: settings.seed_dots]
    seed = points[order]
    observations = [DotObservation((float(x), float(y)), 10.0, 1.0) for x, y in seed]
    fit = fit_grid(
        observations,
        GridFitterConfig(
            local_warp_enabled=False, expected_spacing_px=settings.expected_spacing_px
        ),
    )
    classified = classify_grid_fit(observations, fit)
    directions, confidences = build_direction_matrices(classified)
    centre = inverse_project_lattice(anchor[None], fit.model)[0]
    values, weights, corner = _central_crop(
        directions, confidences, centre, settings.decode_cells
    )
    if min(values.shape) < 6:
        raise AnotoDecodeError(f"seed direction matrix {values.shape} is below 6x6")
    flipped_values, flipped_weights = np.flipud(values), np.flipud(weights)
    result = decode_oriented_consensus(
        flipped_values,
        flipped_weights,
        section=layout.section,
        page_id=layout.page_id,
        adapter=adapter,
        min_direction_confidence=settings.min_direction_confidence,
        min_supporting_windows=settings.min_supporting_windows,
        max_missing_directions=settings.max_missing_directions,
        position_bounds=(layout.shape[1], layout.shape[0]),
        allow_mirror=settings.allow_mirror,
        geometry_confidence=fit.geometry_confidence,
    )
    # Crop-local lattice coordinates -> page grid coordinates is affine.
    basis = np.array(
        [
            image_grid_to_page(tuple(p), values.shape, result)
            for p in ((0, 0), (1, 0), (0, 1))
        ]
    )
    linear = np.column_stack((basis[1] - basis[0], basis[2] - basis[0]))
    inliers = fit.inlier_mask
    lattice = inverse_project_lattice(seed[inliers], fit.model) - corner
    page = lattice @ linear.T + basis[0]
    return page, seed[inliers], result


class _PageSpline:
    """Cubic B-spline residual over the whole page, with cached matrices."""

    def __init__(self, layout: PageLayout, spacing: float, regularization: float):
        _, printed = layout.printed_positions()
        self.printed = printed
        self.spacing = spacing
        self.origin = np.floor(printed.min(axis=0) / spacing) * spacing - 2 * spacing
        self.shape = tuple(
            (
                np.ceil((printed.max(axis=0) - self.origin) / spacing).astype(int)[::-1]
                + 3
            ).tolist()
        )
        self.basis = spline_basis(printed, self.origin, spacing, self.shape)
        # Each dot touches 16 coefficients: keep them for sparse normal equations.
        order = np.argsort(-self.basis, axis=1)[:, :16]
        self.columns = order
        self.weights = np.take_along_axis(self.basis, order, axis=1)
        rows, cols = self.shape
        penalties = []
        for row in range(rows):
            for col in range(cols):
                for dy, dx in ((0, 1), (1, 0)):
                    if row + 2 * dy < rows and col + 2 * dx < cols:
                        penalty = np.zeros(rows * cols)
                        penalty[row * cols + col] = 1
                        penalty[(row + dy) * cols + col + dx] = -2
                        penalty[(row + 2 * dy) * cols + col + 2 * dx] = 1
                        penalties.append(penalty)
        penalty = np.asarray(penalties)
        self.prior = regularization * penalty.T @ penalty + 1e-8 * np.eye(rows * cols)

    def fit(self, indices, target, spacing_px):
        """Model from printed dots ``indices`` to image ``target`` pixels."""
        source = self.printed[indices]
        homography = refine_homography(source, target)
        warp = None
        if len(indices) >= 200:
            residual = target - project_points(source, homography)
            columns, weights = self.columns[indices], self.weights[indices]
            size = self.prior.shape[0]
            normal = np.bincount(
                (columns[:, :, None] * size + columns[:, None, :]).ravel(),
                (weights[:, :, None] * weights[:, None, :]).ravel(),
                minlength=size * size,
            ).reshape(size, size)
            right = np.column_stack(
                [
                    np.bincount(
                        columns.ravel(),
                        (weights * residual[:, k : k + 1]).ravel(),
                        minlength=size,
                    )
                    for k in range(2)
                ]
            )
            coefficients = np.linalg.solve(normal + self.prior, right).reshape(
                *self.shape, 2
            )
            warp = SplineWarp(tuple(self.origin), self.spacing, coefficients)
        return LatticeModel(homography, spacing_px, 0.0, warp)

    def predict(self, model):
        """Image positions of every printed dot."""
        projected = project_points(self.printed, model.grid_to_image)
        if model.warp is not None:
            projected += self.basis @ model.warp.coefficients.reshape(-1, 2)
        return projected


_SPLINES: dict[tuple[str, float, float], _PageSpline] = {}


def _page_spline(layout, settings):
    key = (layout.page_id, settings.spline_spacing_grid, settings.spline_regularization)
    if key not in _SPLINES:
        _SPLINES[key] = _PageSpline(
            layout, settings.spline_spacing_grid, settings.spline_regularization
        )
    return _SPLINES[key]


def _associate(predicted, points, radius):
    """Mutually nearest pairs within ``radius`` (pixel units)."""
    if len(predicted) == 0 or len(points) == 0:
        return np.empty(0, int), np.empty(0, int)
    source = points.astype(np.float32)
    index = cv2.flann_Index(source, {"algorithm": 1, "trees": 1})
    nearest, distance = index.knnSearch(
        predicted.astype(np.float32), 1, params={"checks": 32}
    )
    nearest, distance = nearest[:, 0], np.sqrt(distance[:, 0])
    keep = distance <= radius
    candidates = np.flatnonzero(keep)
    # A detection may serve only its closest prediction.
    best: dict[int, tuple[float, int]] = {}
    for p in candidates:
        d = int(nearest[p])
        if d not in best or distance[p] < best[d][0]:
            best[d] = (distance[p], p)
    pairs = np.array([(p, d) for d, (_, p) in best.items()], int).reshape(-1, 2)
    return pairs[:, 0], pairs[:, 1]


def locate_page(
    gray: np.ndarray,
    layout: PageLayout,
    config: PageLocatorConfig | None = None,
    *,
    adapter: AnotoCodecAdapter | None = None,
    seed_hint_px: tuple[float, float] | None = None,
) -> PageLocation:
    """Localize the page in one grayscale frame; raises AnotoDecodeError on failure."""
    settings = config or PageLocatorConfig()
    timings: dict[str, float] = {}
    start = time.perf_counter()
    points = detect_dots_fast(gray, settings)
    timings["detect"] = (time.perf_counter() - start) * 1e3
    if len(points) < 64:
        raise AnotoDecodeError(f"only {len(points)} dots detected")
    height, width = gray.shape
    mark = time.perf_counter()
    # Seed anchors: the hint (e.g. previous pen area), then the dot median,
    # then the medians of the four image quadrants.
    anchors = [] if seed_hint_px is None else [np.asarray(seed_hint_px, float)]
    anchors.append(np.median(points, axis=0))
    for qx in (0, 1):
        for qy in (0, 1):
            quadrant = points[
                ((points[:, 0] >= width / 2) == bool(qx))
                & ((points[:, 1] >= height / 2) == bool(qy))
            ]
            if len(quadrant) >= settings.seed_dots // 2:
                anchors.append(np.median(quadrant, axis=0))
    seed = None
    errors = []
    for anchor in anchors[: settings.seed_attempts]:
        try:
            seed = _seed(
                points, anchor, layout, settings, adapter or AnotoCodecAdapter()
            )
            break
        except (
            AnotoDecodeError,
            ValueError,
            np.linalg.LinAlgError,
            cv2.error,
        ) as error:
            errors.append(f"{type(error).__name__}: {error}")
    if seed is None:
        raise AnotoDecodeError("no seed region decoded: " + "; ".join(errors))
    seed_page, seed_pixels, decoded = seed
    timings["seed"] = (time.perf_counter() - mark) * 1e3

    mark = time.perf_counter()
    cells, printed = layout.printed_positions()
    # Facing dots (printed < 0.65 grid apart) blur into one peak in the fast
    # detector; they never anchor the model.
    reliable = np.ones(len(printed), bool)
    index = {(int(u), int(v)): i for i, (u, v) in enumerate(cells)}
    for i, (u, v) in enumerate(cells.astype(int)):
        for du, dv in ((1, 0), (0, 1)):
            j = index.get((u + du, v + dv))
            if j is not None and np.linalg.norm(printed[i] - printed[j]) < 0.65:
                reliable[i] = reliable[j] = False
    # Seed correspondences: snap each seed dot to its cell's printed position.
    # Printed offsets are below half a cell, so rounding recovers the cell.
    nearest_cell = np.rint(seed_page).astype(int)
    valid = (
        (nearest_cell[:, 0] >= 0)
        & (nearest_cell[:, 1] >= 0)
        & (nearest_cell[:, 0] < layout.shape[1])
        & (nearest_cell[:, 1] < layout.shape[0])
    )
    flat = nearest_cell[valid, 1] * layout.shape[1] + nearest_cell[valid, 0]
    close = np.linalg.norm(printed[flat] - seed_page[valid], axis=1) < 0.15
    if close.sum() < 16:
        raise AnotoDecodeError("decoded seed does not match the printed layout")
    spline = _page_spline(layout, settings)
    seed_indices = flat[close]
    model = LatticeModel(
        refine_homography(printed[seed_indices], seed_pixels[valid][close]), 1.0, 0.0
    )
    step_u = project_lattice(printed[seed_indices] + (1, 0), model) - project_lattice(
        printed[seed_indices], model
    )
    spacing_px = float(np.median(np.linalg.norm(step_u, axis=1)))
    radius = settings.association_ratio * spacing_px
    rows, cols = layout.shape
    flat_cells = (cells[:, 1] * cols + cells[:, 0]).astype(int)
    associated = np.zeros(len(printed), bool)
    associated[seed_indices] = True
    inside = np.zeros(len(printed), bool)
    pairs = (np.empty(0, int), np.empty(0, int))
    fitted = seed_indices
    settled = 0
    for _ in range(settings.max_growth_steps + settings.settle_passes):
        predicted = spline.predict(model)
        inside = (
            (predicted[:, 0] >= 3)
            & (predicted[:, 1] >= 3)
            & (predicted[:, 0] < width - 3)
            & (predicted[:, 1] < height - 3)
        )
        unreached = np.ones(rows * cols, np.uint8)
        unreached[flat_cells[associated]] = 0
        distance = cv2.distanceTransform(
            unreached.reshape(rows, cols), cv2.DIST_L2, 5
        ).ravel()[flat_cells]
        candidates = np.flatnonzero(inside & (distance <= settings.growth_step_grid))
        p_idx, d_idx = _associate(predicted[candidates], points, radius)
        pairs = (candidates[p_idx], d_idx)
        anchor = reliable[pairs[0]]
        if anchor.sum() < 16:
            raise AnotoDecodeError(
                "too few associated dots while growing the page model"
            )
        fitted, target = pairs[0][anchor], points[pairs[1][anchor]]
        for _ in range(2):
            model = spline.fit(fitted, target, spacing_px)
            # Robust refit: drop gross outliers (spurious peaks, specks).
            error = np.linalg.norm(spline.predict(model)[fitted] - target, axis=1)
            keep = error <= max(3.0 * np.median(error), 0.08 * spacing_px)
            if keep.all() or keep.sum() < 16:
                break
            fitted, target = fitted[keep], target[keep]
        grown = np.zeros(len(printed), bool)
        grown[pairs[0]] = True
        # A dot sitting exactly at the association radius may flip in and out;
        # such a negligible change counts as settled.
        changed = np.count_nonzero(grown ^ associated)
        associated = grown
        if changed <= max(2, 0.001 * np.count_nonzero(grown)):
            settled += 1
            if settled > settings.settle_passes:
                break
        else:
            settled = 0
    residual = spline.predict(model)[fitted] - target
    rms = float(np.sqrt(np.mean(np.sum(residual**2, axis=1))))
    model = LatticeModel(model.grid_to_image, spacing_px, rms, model.warp)
    timings["grow"] = (time.perf_counter() - mark) * 1e3
    timings["total"] = (time.perf_counter() - start) * 1e3
    location = PageLocation(
        layout=layout,
        model=model,
        rotation_quadrants=decoded.pose.rotation_quadrants,
        mirrored=decoded.mirrored,
        associated=len(pairs[0]),
        expected_visible=int(inside.sum()),
        rms_px=rms,
        supporting_windows=decoded.supporting_windows,
        timings_ms=timings,
    )
    if (
        location.associated < settings.min_associated
        or location.support < settings.min_support
        or rms > settings.max_rms_ratio * spacing_px
    ):
        raise AnotoDecodeError(
            f"page model not supported: {location.associated} dots, "
            f"support {location.support:.2f}, rms {rms:.2f} px"
        )
    return location
