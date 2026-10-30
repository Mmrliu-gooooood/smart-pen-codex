"""Numerically checked homography helpers for the lattice pipeline."""

from __future__ import annotations

import cv2
import numpy as np

from digital_pen.types import LatticeModel, SplineWarp


def validate_homography(homography: np.ndarray) -> np.ndarray:
    """Return a normalized float64 homography or raise ``ValueError``."""
    matrix = np.asarray(homography, dtype=np.float64)
    if matrix.shape != (3, 3) or not np.all(np.isfinite(matrix)):
        raise ValueError("homography must be a finite 3x3 matrix")
    magnitude = float(np.max(np.abs(matrix)))
    if magnitude == 0:
        raise ValueError("homography must be non-zero")
    matrix = matrix / magnitude
    if (
        abs(float(np.linalg.det(matrix))) < 1e-12
        or float(np.linalg.cond(matrix)) > 1e12
    ):
        raise ValueError("homography must be invertible")
    scale = float(matrix[2, 2])
    if abs(scale) < 1e-12:
        return matrix
    return matrix / scale


def project_points(points: np.ndarray, homography: np.ndarray) -> np.ndarray:
    """Project an ``(N, 2)`` array through a homography."""
    coordinates = np.asarray(points, dtype=np.float64)
    if coordinates.ndim != 2 or coordinates.shape[1] != 2:
        raise ValueError("points must have shape (N, 2)")
    matrix = validate_homography(homography)
    homogeneous = np.column_stack((coordinates, np.ones(len(coordinates))))
    projected = homogeneous @ matrix.T
    denominator = projected[:, 2]
    if np.any(np.abs(denominator) < 1e-12):
        raise ValueError("homography maps a point to infinity")
    result = projected[:, :2] / denominator[:, None]
    if not np.all(np.isfinite(result)):
        raise ValueError("homography produced non-finite coordinates")
    return result


def inverse_project_points(points: np.ndarray, homography: np.ndarray) -> np.ndarray:
    """Map image points back into normalized grid coordinates."""
    matrix = validate_homography(homography)
    return project_points(points, np.linalg.inv(matrix))


def spline_basis(
    points: np.ndarray,
    origin: tuple[float, float] | np.ndarray,
    spacing: float,
    shape: tuple[int, int],
) -> np.ndarray:
    """Tensor cubic B-spline basis, with zero correction outside its domain."""
    source = np.asarray(points, dtype=np.float64)
    if source.ndim != 2 or source.shape[1] != 2 or not np.all(np.isfinite(source)):
        raise ValueError("spline points must have finite shape (N, 2)")
    if not np.isfinite(spacing) or spacing <= 0:
        raise ValueError("spline spacing must be positive and finite")
    if (
        len(shape) != 2
        or any(not isinstance(size, (int, np.integer)) or size < 4 for size in shape)
        or np.prod(shape) > 4096
    ):
        raise ValueError(
            "spline shape must contain at most 4096 finite-support coefficients"
        )
    if np.asarray(origin).shape != (2,) or not np.all(np.isfinite(origin)):
        raise ValueError("spline origin must contain two finite coordinates")
    coordinates = (source - origin) / spacing
    integer = np.floor(coordinates)
    left = integer.astype(int) - 1
    fraction = coordinates - integer
    weights = (
        np.stack(
            (
                (1 - fraction) ** 3,
                3 * fraction**3 - 6 * fraction**2 + 4,
                -3 * fraction**3 + 3 * fraction**2 + 3 * fraction + 1,
                fraction**3,
            ),
            axis=2,
        )
        / 6
    )
    matrix = np.zeros((len(points), shape[0] * shape[1]))
    for row in range(4):
        for col in range(4):
            ix, iy = left[:, 0] + col, left[:, 1] + row
            valid = (ix >= 0) & (iy >= 0) & (ix < shape[1]) & (iy < shape[0])
            matrix[np.flatnonzero(valid), iy[valid] * shape[1] + ix[valid]] += (
                weights[valid, 0, col] * weights[valid, 1, row]
            )
    return matrix


def project_lattice(points: np.ndarray, lattice: LatticeModel) -> np.ndarray:
    """Map grid coordinates to original pixels, including a fitted correction."""
    projected = project_points(points, lattice.grid_to_image)
    if lattice.warp is not None:
        warp = lattice.warp
        matrix = spline_basis(
            points, warp.origin_grid, warp.spacing_grid, warp.coefficients.shape[:2]
        )
        projected += matrix @ warp.coefficients.reshape(-1, 2)
    return projected


def inverse_project_lattice(points: np.ndarray, lattice: LatticeModel) -> np.ndarray:
    """Invert the complete mapping with a checked numerical Newton solve."""
    target = np.asarray(points, dtype=np.float64)
    current = inverse_project_points(target, lattice.grid_to_image)
    if lattice.warp is None:
        return current
    for _ in range(12):
        projected = project_lattice(current, lattice)
        error = projected - target
        if np.max(np.linalg.norm(error, axis=1), initial=0) < 1e-7:
            break
        epsilon = 1e-4
        along_x = (
            project_lattice(current + (epsilon, 0), lattice) - projected
        ) / epsilon
        along_y = (
            project_lattice(current + (0, epsilon), lattice) - projected
        ) / epsilon
        determinant = along_x[:, 0] * along_y[:, 1] - along_y[:, 0] * along_x[:, 1]
        if np.any(np.abs(determinant) < 1e-10):
            raise ValueError("smooth lattice mapping has a singular local Jacobian")
        step = np.column_stack(
            (
                (along_y[:, 1] * error[:, 0] - along_y[:, 0] * error[:, 1])
                / determinant,
                (-along_x[:, 1] * error[:, 0] + along_x[:, 0] * error[:, 1])
                / determinant,
            )
        )
        current -= step
    if (
        np.max(
            np.linalg.norm(project_lattice(current, lattice) - target, axis=1),
            initial=0,
        )
        > 1e-3
    ):
        raise ValueError("smooth lattice inverse did not converge")
    return current


def fit_spline_warp(
    grid_points: np.ndarray,
    image_points: np.ndarray,
    homography: np.ndarray,
    *,
    spacing_grid: float = 6.0,
    regularization: float = 0.01,
) -> SplineWarp:
    """Fit a curvature-regularized pixel residual; no image is rescaled."""
    source = np.asarray(grid_points, dtype=np.float64)
    target = np.asarray(image_points, dtype=np.float64)
    if (
        source.shape != target.shape
        or source.ndim != 2
        or source.shape[1] != 2
        or len(source) < 16
    ):
        raise ValueError("smooth correspondences must share shape (N, 2), N >= 16")
    if not np.all(np.isfinite(source)) or not np.all(np.isfinite(target)):
        raise ValueError("smooth correspondences must be finite")
    if not np.isfinite(spacing_grid) or spacing_grid <= 0:
        raise ValueError("spline spacing must be positive and finite")
    if not np.isfinite(regularization) or regularization < 0:
        raise ValueError("spline regularization must be finite and non-negative")
    origin = (
        np.floor(source.min(axis=0) / spacing_grid) * spacing_grid - 2 * spacing_grid
    )
    shape = tuple(
        (
            np.ceil((source.max(axis=0) - origin) / spacing_grid).astype(int)[::-1] + 3
        ).tolist()
    )
    matrix = spline_basis(source, origin, spacing_grid, shape)
    penalties = []
    for row in range(shape[0]):
        for col in range(shape[1]):
            for dy, dx in ((0, 1), (1, 0)):
                if row + 2 * dy < shape[0] and col + 2 * dx < shape[1]:
                    penalty = np.zeros(matrix.shape[1])
                    penalty[row * shape[1] + col] = 1
                    penalty[(row + dy) * shape[1] + col + dx] = -2
                    penalty[(row + 2 * dy) * shape[1] + col + 2 * dx] = 1
                    penalties.append(penalty)
    penalty = np.asarray(penalties)
    normal = matrix.T @ matrix + regularization * penalty.T @ penalty
    normal += np.eye(matrix.shape[1]) * 1e-8
    residual = target - project_points(source, homography)
    coefficients = np.linalg.solve(normal, matrix.T @ residual).reshape(*shape, 2)
    return SplineWarp(tuple(origin), spacing_grid, coefficients)


def validate_lattice_region(
    lattice: LatticeModel,
    minimum: tuple[float, float],
    maximum: tuple[float, float],
    *,
    samples: int = 17,
) -> dict[str, float]:
    """Check edges and inter-dot points for folds and inverse consistency."""
    low, high = np.asarray(minimum), np.asarray(maximum)
    if (
        low.shape != (2,)
        or high.shape != (2,)
        or not np.all(np.isfinite([low, high]))
        or np.any(low >= high)
    ):
        raise ValueError("lattice validation bounds must be finite and increasing")
    if not isinstance(samples, int) or not 3 <= samples <= 100:
        raise ValueError("lattice validation samples must be between 3 and 100")
    yy, xx = np.meshgrid(
        np.linspace(low[1], high[1], samples), np.linspace(low[0], high[0], samples)
    )
    grid = np.column_stack((xx.ravel(), yy.ravel()))
    pixels = project_lattice(grid, lattice)
    epsilon = 1e-3
    jacobians = []
    for projection in (
        lambda p: project_points(p, lattice.grid_to_image),
        lambda p: project_lattice(p, lattice),
    ):
        centers = projection(grid)
        along_x = (projection(grid + (epsilon, 0)) - centers) / epsilon
        along_y = (projection(grid + (0, epsilon)) - centers) / epsilon
        jacobians.append(along_x[:, 0] * along_y[:, 1] - along_x[:, 1] * along_y[:, 0])
    ratio = jacobians[1] / jacobians[0]
    if not np.all(np.isfinite(ratio)) or np.any(ratio <= 0):
        raise ValueError("smooth lattice contains a local fold")
    recovered = inverse_project_lattice(pixels, lattice)
    error = np.linalg.norm(project_lattice(recovered, lattice) - pixels, axis=1)
    return {
        "minimum_jacobian_ratio": float(ratio.min()),
        "maximum_jacobian_ratio": float(ratio.max()),
        "maximum_roundtrip_error_px": float(error.max()),
    }


def estimate_homography(
    grid_points: np.ndarray,
    image_points: np.ndarray,
    *,
    ransac_threshold_px: float,
    max_iterations: int = 4000,
    confidence: float = 0.999,
) -> tuple[np.ndarray, np.ndarray]:
    """Estimate a grid-to-image homography and its RANSAC inlier mask."""
    source = np.asarray(grid_points, dtype=np.float64)
    target = np.asarray(image_points, dtype=np.float64)
    if source.shape != target.shape or source.ndim != 2 or source.shape[1] != 2:
        raise ValueError("grid_points and image_points must share shape (N, 2)")
    if len(source) < 4:
        raise ValueError("at least four point correspondences are required")
    if ransac_threshold_px <= 0:
        raise ValueError("ransac_threshold_px must be positive")
    matrix, mask = cv2.findHomography(
        source,
        target,
        cv2.RANSAC,
        ransac_threshold_px,
        maxIters=max_iterations,
        confidence=confidence,
    )
    if matrix is None or mask is None:
        raise ValueError("could not estimate a non-degenerate homography")
    return validate_homography(matrix), mask.ravel().astype(bool)


def refine_homography(
    grid_points: np.ndarray,
    image_points: np.ndarray,
) -> np.ndarray:
    """Least-squares refine a homography after robust inlier selection."""
    source = np.asarray(grid_points, dtype=np.float64)
    target = np.asarray(image_points, dtype=np.float64)
    if source.shape != target.shape or source.ndim != 2 or source.shape[1] != 2:
        raise ValueError("grid_points and image_points must share shape (N, 2)")
    if len(source) < 4:
        raise ValueError("at least four point correspondences are required")
    matrix, _ = cv2.findHomography(source, target, 0)
    if matrix is None:
        raise ValueError("could not refine a non-degenerate homography")
    return validate_homography(matrix)


def median_grid_spacing(homography: np.ndarray, grid_points: np.ndarray) -> float:
    """Measure the median projected one-cell spacing over a fitted region."""
    points = np.asarray(grid_points, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 2 or len(points) == 0:
        raise ValueError("grid_points must be a non-empty (N, 2) array")
    centers = project_points(points, homography)
    along_x = project_points(points + (1.0, 0.0), homography)
    along_y = project_points(points + (0.0, 1.0), homography)
    distances = np.concatenate(
        (
            np.linalg.norm(along_x - centers, axis=1),
            np.linalg.norm(along_y - centers, axis=1),
        )
    )
    spacing = float(np.median(distances))
    if not np.isfinite(spacing) or spacing <= 0:
        raise ValueError("homography has no positive finite grid spacing")
    return spacing
