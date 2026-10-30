"""Grid-guided photometric repair of merged, split and missing dots.

The blind detector resolves most dots, but two Anoto dots displaced toward one
another (0.4 grid apart) can blur into one elongated blob, one blob can be split
into three detections, and a weak dot can be missed. Once a lattice is known,
every in-page cell holds exactly one dot at one of four printed offsets. Cells
without exactly one consistent detection are grouped with their inconsistent
neighbours and re-fitted against the raw pixels:

* offset hypotheses for the group are ranked with a fast linear fit (positions
  fixed at the lattice prediction, amplitudes and a sloping background free);
* the best combinations are then fitted by Levenberg-Marquardt with free
  sub-pixel positions and amplitudes for the group *and* every other detection
  overlapping the window, using the PSF measured on nearby isolated dots.

The lattice only enumerates hypotheses and starts the optimizer; reported
centers are the photometric optimum. A group is kept unchanged unless the fit
converged, every source has normal contrast, each source ends on one of its
own cell's four printed positions and no two sources share a dot. Passes repeat
so groups next to repaired cells are retried with clean context.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import pi

import cv2
import numpy as np

from digital_pen.types import DotObservation
from digital_pen.vision.grid_fitter import GridFitResult
from digital_pen.vision.perspective import inverse_project_lattice, project_lattice


@dataclass(frozen=True)
class GridRefinementConfig:
    residual_tolerance_grid: float = 0.12
    max_group_cells: int = 4
    window_margin_sigma: float = 3.0
    min_amplitude_ratio: float = 0.35
    max_amplitude_ratio: float = 1.6
    max_shift_grid: float = 0.12
    min_separation_grid: float = 0.25
    image_margin_px: float = 5.0
    psf_samples: int = 400
    psf_neighbors: int = 9
    candidates_per_group: int = 3
    passes: int = 3

    def __post_init__(self) -> None:
        if self.max_group_cells < 1 or self.passes < 1 or self.candidates_per_group < 1:
            raise ValueError("group size, passes and candidates must be positive")


@dataclass(frozen=True)
class _Psf:
    precision: np.ndarray
    amplitude: float


def _ideal_offsets(offset: float) -> np.ndarray:
    # DotDirection order: UP, LEFT, RIGHT, DOWN in lattice (col, row) units.
    return np.array(((0, -offset), (-offset, 0), (offset, 0), (0, offset)))


class _Window:
    """Pixels of one rectangular fit window with a fixed PSF."""

    def __init__(self, gray, bounds, precision):
        x0, y0, x1, y1 = bounds
        self.origin = np.array([(x0 + x1 - 1) / 2, (y0 + y1 - 1) / 2])
        yy, xx = np.indices((y1 - y0, x1 - x0), dtype=float)
        self.x = xx.ravel() + x0 - self.origin[0]
        self.y = yy.ravel() + y0 - self.origin[1]
        self.z = gray[y0:y1, x0:x1].astype(float).ravel()
        self.q = precision

    def shapes(self, centers):
        dx = self.x[:, None] - centers[:, 0]
        dy = self.y[:, None] - centers[:, 1]
        q = self.q
        exponent = -0.5 * (
            q[0, 0] * dx * dx + 2 * q[0, 1] * dx * dy + q[1, 1] * dy * dy
        )
        return np.exp(np.maximum(exponent, -60)), dx, dy

    def linear_error(self, image_centers):
        shape, _, _ = self.shapes(np.asarray(image_centers) - self.origin)
        design = np.column_stack((np.ones_like(self.x), self.x, self.y, -shape))
        coefficients, *_ = np.linalg.lstsq(design, self.z, rcond=None)
        residual = self.z - design @ coefficients
        return float(residual @ residual)

    def fit(self, image_centers, free, watched, iterations=100):
        """Levenberg-Marquardt over plane, amplitudes and the free centers.

        ``free`` marks sources whose position is optimized (others keep their
        start position but a free amplitude); convergence is judged on the
        ``watched`` sources, whose centers are reported.
        """
        count = len(image_centers)
        free = np.flatnonzero(free)
        position = np.asarray(image_centers, float) - self.origin
        shape, _, _ = self.shapes(position)
        design = np.column_stack((np.ones_like(self.x), self.x, self.y, -shape))
        linear, *_ = np.linalg.lstsq(design, self.z, rcond=None)
        parameters = np.concatenate((linear, position[free].ravel()))
        q = self.q
        watch = np.isin(free, watched)

        def evaluate(values):
            centers = position.copy()
            centers[free] = values[3 + count :].reshape(-1, 2)
            shape, dx, dy = self.shapes(centers)
            model = (
                values[0]
                + values[1] * self.x
                + values[2] * self.y
                - shape @ values[3 : 3 + count]
            )
            return self.z - model, shape, dx, dy

        residual, shape, dx, dy = evaluate(parameters)
        error = float(residual @ residual)
        jacobian = np.empty((len(self.z), 3 + count + 2 * len(free)))
        jacobian[:, 0], jacobian[:, 1], jacobian[:, 2] = 1.0, self.x, self.y
        damping, converged = 1e-3, False
        for _ in range(iterations):
            signal = (parameters[3 : 3 + count] * shape)[:, free]
            jacobian[:, 3 : 3 + count] = -shape
            jacobian[:, 3 + count :: 2] = -signal * (
                q[0, 0] * dx[:, free] + q[0, 1] * dy[:, free]
            )
            jacobian[:, 4 + count :: 2] = -signal * (
                q[0, 1] * dx[:, free] + q[1, 1] * dy[:, free]
            )
            curvature = jacobian.T @ jacobian
            try:
                step = np.linalg.solve(
                    curvature + damping * np.diag(np.diag(curvature) + 1e-9),
                    jacobian.T @ residual,
                )
            except np.linalg.LinAlgError:
                return None
            trial = evaluate(parameters + step)
            trial_error = float(trial[0] @ trial[0])
            if trial_error <= error:
                gain = error - trial_error
                parameters, error = parameters + step, trial_error
                residual, shape, dx, dy = trial
                damping = max(damping / 4, 1e-7)
                moved = np.abs(step[3 + count :].reshape(-1, 2)[watch])
                if (moved.size == 0 or moved.max() < 1e-2) and gain <= 1e-5 * error:
                    converged = True
                    break
            else:
                damping *= 6
                if damping > 1e7:
                    converged = True  # no descent direction remains
                    break
        centers = position.copy()
        centers[free] = parameters[3 + count :].reshape(-1, 2)
        return centers + self.origin, parameters[3 : 3 + count], error, converged


def _psf_samples(gray, points, isolated, samples):
    from digital_pen.vision.dot_detector import _gaussian_center

    candidates = np.flatnonzero(isolated)
    if len(candidates) > samples:
        candidates = candidates[
            np.linspace(0, len(candidates) - 1, samples).astype(int)
        ]
    positions, psfs = [], []
    for index in candidates:
        _, fitted = _gaussian_center(gray, tuple(points[index]))
        if fitted is None:
            continue
        precision = np.array([[fitted[6], fitted[7]], [fitted[7], fitted[8]]])
        if np.linalg.eigvalsh(precision).min() <= 0.02:
            continue
        positions.append(points[index])
        psfs.append(_Psf(precision, float(fitted[3])))
    return np.asarray(positions).reshape(-1, 2), psfs


def _nearby_psf(position, positions, psfs, neighbors):
    if len(psfs) < 3:
        return None
    order = np.argsort(np.linalg.norm(positions - position, axis=1))[:neighbors]
    covariance = np.median([np.linalg.inv(psfs[i].precision) for i in order], axis=0)
    if np.linalg.eigvalsh(covariance).min() <= 0:
        return None
    amplitude = float(np.median([psfs[i].amplitude for i in order]))
    return _Psf(np.linalg.inv(covariance), amplitude)


def _components(cells: set, limit: int) -> list[list[tuple[int, int]]]:
    """4-connected components, split into compact chunks of at most ``limit``."""
    chunks = []
    remaining = set(cells)
    while remaining:
        component = {remaining.pop()}
        queue = list(component)
        while queue:
            col, row = queue.pop()
            for neighbor in (
                (col - 1, row),
                (col + 1, row),
                (col, row - 1),
                (col, row + 1),
            ):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    component.add(neighbor)
                    queue.append(neighbor)
        while component:
            # Start from an extremity and grow breadth-first.
            seed = min(
                sorted(component),
                key=lambda c: sum(
                    n in component
                    for n in (
                        (c[0] - 1, c[1]),
                        (c[0] + 1, c[1]),
                        (c[0], c[1] - 1),
                        (c[0], c[1] + 1),
                    )
                ),
            )
            chunk, frontier = [seed], [seed]
            component.remove(seed)
            while frontier and len(chunk) < limit:
                col, row = frontier.pop(0)
                for neighbor in (
                    (col - 1, row),
                    (col + 1, row),
                    (col, row - 1),
                    (col, row + 1),
                ):
                    if neighbor in component and len(chunk) < limit:
                        component.remove(neighbor)
                        chunk.append(neighbor)
                        frontier.append(neighbor)
            chunks.append(sorted(chunk))
    return chunks


def _repair_pass(gray, observations, fit, settings, psf_positions, psfs, stats, trace):
    model, spacing = fit.model, fit.model.spacing_px
    height, width = gray.shape
    points = np.asarray([item.center_px for item in observations], float)
    normalized = inverse_project_lattice(points, model)
    indices = np.rint(normalized).astype(int)
    cells: dict[tuple[int, int], list[int]] = {}
    for index, (col, row) in enumerate(indices):
        cells.setdefault((int(col), int(row)), []).append(index)
    ideals = _ideal_offsets(fit.offset_ratio)
    deviation = np.min(
        np.linalg.norm((normalized - indices)[:, None, :] - ideals[None], axis=2),
        axis=1,
    )
    good = {
        cell
        for cell, members in cells.items()
        if len(members) == 1
        and deviation[members[0]] < settings.residual_tolerance_grid
    }
    assigned = np.array([[a.col, a.row] for a in fit.assignments])
    low, high = assigned.min(axis=0), assigned.max(axis=0)
    margin = settings.image_margin_px + fit.offset_ratio * spacing
    grid = np.stack(
        np.meshgrid(np.arange(low[0], high[0] + 1), np.arange(low[1], high[1] + 1)), -1
    ).reshape(-1, 2)
    centers = project_lattice(grid.astype(float), model)
    inside = (
        (centers[:, 0] >= margin)
        & (centers[:, 0] < width - margin)
        & (centers[:, 1] >= margin)
        & (centers[:, 1] < height - margin)
    )
    # Every in-page cell carries exactly one printed dot, so a cell without a
    # single consistent detection is always worth a fit.
    problems = {tuple(map(int, cell)) for cell in grid[inside]} - good
    replaced: set[int] = set()
    alive = np.ones(len(points), bool)
    added: list[DotObservation] = []
    accepted = 0
    for group in _components(problems, settings.max_group_cells):
        stats["groups"] += 1
        hypotheses = project_lattice(
            (np.asarray(group, float)[:, None, :] + ideals[None]).reshape(-1, 2), model
        ).reshape(len(group), 4, 2)
        psf = _nearby_psf(
            hypotheses.mean(axis=(0, 1)), psf_positions, psfs, settings.psf_neighbors
        )
        if psf is None:
            stats["rejected_no_psf"] = stats.get("rejected_no_psf", 0) + 1
            continue
        sigma = float(np.sqrt(np.linalg.eigvalsh(np.linalg.inv(psf.precision)).max()))
        pad = settings.window_margin_sigma * sigma
        bounds = (
            int(np.floor(hypotheses[..., 0].min() - pad)),
            int(np.floor(hypotheses[..., 1].min() - pad)),
            int(np.ceil(hypotheses[..., 0].max() + pad)) + 1,
            int(np.ceil(hypotheses[..., 1].max() + pad)) + 1,
        )
        if bounds[0] < 0 or bounds[1] < 0 or bounds[2] > width or bounds[3] > height:
            stats["rejected_border"] = stats.get("rejected_border", 0) + 1
            continue
        members = {i for cell in group for i in cells.get(cell, [])}
        reach = 2 * sigma
        # Context: every other current detection near the window, including
        # dots already repaired earlier in this pass.
        keep = alive.copy()
        keep[list(members)] = False
        current = np.vstack(
            [points[keep]]
            + ([np.asarray([a.center_px for a in added])] if added else [])
        )
        context_points = current[
            (current[:, 0] > bounds[0] - reach)
            & (current[:, 0] < bounds[2] + reach)
            & (current[:, 1] > bounds[1] - reach)
            & (current[:, 1] < bounds[3] + reach)
        ]
        context = range(len(context_points))
        window = _Window(gray, bounds, psf.precision)

        def starts(choice, context_points=context_points, hypotheses=hypotheses):
            group_points = hypotheses[np.arange(len(choice)), list(choice)]
            return np.vstack((group_points, context_points))

        # Rank offset combinations cheaply, then optimize only the best few.
        if len(group) <= 2:
            ranked = sorted(
                (window.linear_error(starts(choice)), choice)
                for choice in product(range(4), repeat=len(group))
            )
        else:
            current = [0] * len(group)
            for _ in range(3):
                for k in range(len(group)):
                    current[k] = min(
                        range(4),
                        key=lambda d, k=k: window.linear_error(
                            starts((*current[:k], d, *current[k + 1 :]))
                        ),
                    )
            ranked = [(window.linear_error(starts(current)), tuple(current))]
            for k in range(len(group)):
                for d in range(4):
                    if d != current[k]:
                        alternative = (*current[:k], d, *current[k + 1 :])
                        ranked.append(
                            (window.linear_error(starts(alternative)), alternative)
                        )
            ranked.sort()
        # Context sources centred outside the window are poorly constrained:
        # their positions stay fixed (amplitude still free).
        free = np.ones(len(group) + len(context), bool)
        free[len(group) :] = (
            (context_points[:, 0] >= bounds[0])
            & (context_points[:, 0] < bounds[2])
            & (context_points[:, 1] >= bounds[1])
            & (context_points[:, 1] < bounds[3])
        )
        best = None
        for _, choice in ranked[: settings.candidates_per_group]:
            result = window.fit(starts(choice), free, np.arange(len(group)))
            if result is not None and (best is None or result[2] < best[1][2]):
                best = (choice, result)
        if best is None:
            stats["rejected_singular"] = stats.get("rejected_singular", 0) + 1
            continue
        choice, (fitted, amplitudes, _, converged) = best
        group_centers = fitted[: len(group)]
        group_amplitudes = amplitudes[: len(group)]
        # A source may settle on its cell's true offset rather than the one it
        # started from; it must end on one of its own cell's printed positions.
        shifts = np.min(
            np.linalg.norm(group_centers[:, None, :] - hypotheses, axis=2), axis=1
        )
        separation = np.linalg.norm(fitted[:, None] - group_centers[None], axis=2)
        separation[np.arange(len(group)), np.arange(len(group))] = np.inf
        failures = {
            "weak": group_amplitudes < settings.min_amplitude_ratio * psf.amplitude,
            # One source absorbing two dots is darker than any single dot.
            "too_dark": group_amplitudes > settings.max_amplitude_ratio * psf.amplitude,
            "moved": shifts > settings.max_shift_grid * spacing,
            "collapsed": separation.min(axis=0)
            < settings.min_separation_grid * spacing,
        }
        valid = np.ones(len(group), bool) if converged else np.zeros(len(group), bool)
        for failed in failures.values():
            valid &= ~failed
        if trace is not None:
            trace.append(
                dict(
                    group=group,
                    choice=choice,
                    centers=group_centers.tolist(),
                    shifts=shifts.tolist(),
                    amplitudes=group_amplitudes.tolist(),
                    reference_amplitude=psf.amplitude,
                    converged=converged,
                    valid=valid.tolist(),
                    failures={k: v.tolist() for k, v in failures.items()},
                )
            )
        if not converged:
            stats["rejected_not_converged"] = stats.get("rejected_not_converged", 0) + 1
        for name, failed in failures.items():
            if converged and failed.any():
                stats[f"rejected_{name}"] = stats.get(f"rejected_{name}", 0) + int(
                    failed.sum()
                )
        if not valid.any():
            continue
        # Individually validated sources are kept; failing cells keep their
        # detections and are retried next pass with the repaired context.
        accepted += 1
        cell_members = [
            i for k, cell in enumerate(group) if valid[k] for i in cells.get(cell, [])
        ]
        replaced.update(cell_members)
        alive[cell_members] = False
        axes = np.sqrt(2 * np.log(2) / np.linalg.eigvalsh(psf.precision))
        area = float(pi * axes.prod())
        perimeter = pi * (
            3 * axes.sum() - np.sqrt((3 * axes[0] + axes[1]) * (axes[0] + 3 * axes[1]))
        )
        circularity = min(1.0, float(4 * pi * area / (perimeter * perimeter)))
        added.extend(
            DotObservation(
                center_px=(float(x), float(y)), area_px=area, circularity=circularity
            )
            for x, y in group_centers[valid]
        )
    stats["accepted"] += accepted
    stats["replaced"] += len(replaced)
    stats["added"] += len(added)
    refined = [item for i, item in enumerate(observations) if i not in replaced] + added
    refined.sort(key=lambda item: (item.center_px[1], item.center_px[0]))
    return refined, accepted


def refine_with_grid(
    gray: np.ndarray,
    observations: list[DotObservation],
    fit: GridFitResult,
    config: GridRefinementConfig | None = None,
    *,
    trace: list | None = None,
) -> tuple[list[DotObservation], dict[str, int]]:
    """Return observations with inconsistent lattice cells photometrically re-fitted."""
    settings = config or GridRefinementConfig()
    stats = dict(passes=0, groups=0, accepted=0, replaced=0, added=0)
    if len(observations) < 16 or fit.offset_ratio <= 0 or not fit.assignments:
        return observations, stats
    points = np.asarray([item.center_px for item in observations], float)
    spacing = fit.model.spacing_px
    source = points.astype(np.float32)
    index = cv2.flann_Index(source, {"algorithm": 1, "trees": 4})
    _, distances = index.knnSearch(source, 2, params={})
    isolated = np.zeros(len(points), bool)
    isolated[[a.observation_index for a in fit.assignments]] = True
    isolated &= np.sqrt(distances[:, 1]) > 0.6 * spacing
    psf_positions, psfs = _psf_samples(gray, points, isolated, settings.psf_samples)
    refined = observations
    for _ in range(settings.passes):
        stats["passes"] += 1
        refined, accepted = _repair_pass(
            gray, refined, fit, settings, psf_positions, psfs, stats, trace
        )
        if not accepted:
            break
    return refined, stats
