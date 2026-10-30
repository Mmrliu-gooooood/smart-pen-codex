from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import StrEnum
from math import pi

import cv2
import numpy as np

from digital_pen.types import DotObservation
from digital_pen.vision.preprocessing import PreprocessingConfig, preprocess_image


@dataclass(frozen=True)
class DotDetectorConfig(PreprocessingConfig):
    min_area_px: float = 3.0
    max_area_px: float = 200.0
    min_aspect_ratio: float = 0.5
    min_circularity: float = 0.5
    candidate_method: str = "contours"
    centroid_method: str = "weighted"
    scale_space_min_response: float = 3.0
    scale_space_min_sigma_px: float = 0.8
    scale_space_paper_mask: bool = True
    joint_neighbor_fit: bool = False
    grid_refinement: bool = False

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.min_area_px <= 0 or self.max_area_px < self.min_area_px:
            raise ValueError("area bounds must be positive and ordered")
        if not 0 < self.min_aspect_ratio <= 1:
            raise ValueError("min_aspect_ratio must be between 0 and 1")
        if not 0 <= self.min_circularity <= 1:
            raise ValueError("min_circularity must be between 0 and 1")
        if self.candidate_method not in {"contours", "scale_space"}:
            raise ValueError("candidate_method must be contours or scale_space")
        if self.centroid_method not in {"weighted", "gaussian"}:
            raise ValueError("centroid_method must be weighted or gaussian")
        if (
            self.candidate_method == "scale_space"
            and self.centroid_method != "gaussian"
        ):
            raise ValueError("scale_space candidates require centroid_method=gaussian")
        if (
            not np.isfinite(self.scale_space_min_response)
            or self.scale_space_min_response <= 0
        ):
            raise ValueError("scale_space_min_response must be positive and finite")
        if (
            not np.isfinite(self.scale_space_min_sigma_px)
            or self.scale_space_min_sigma_px <= 0
        ):
            raise ValueError("scale_space_min_sigma_px must be positive and finite")


class RejectionReason(StrEnum):
    AREA_TOO_SMALL = "area_too_small"
    AREA_TOO_LARGE = "area_too_large"
    ASPECT_RATIO = "aspect_ratio"
    CIRCULARITY = "circularity"
    SCALE_TOO_SMALL = "scale_too_small"
    FIT_CONTRAST = "fit_contrast"
    BACKGROUND_EDGE = "background_edge"
    DUPLICATE = "duplicate"


@dataclass(frozen=True)
class DotCandidate:
    center_px: tuple[float, float]
    area_px: float
    circularity: float
    aspect_ratio: float
    bounding_box: tuple[int, int, int, int]
    accepted: bool
    rejection_reason: RejectionReason | None


@dataclass(frozen=True)
class DotDetectionResult:
    observations: list[DotObservation]
    binary: np.ndarray
    stages: dict[str, np.ndarray]
    candidates: list[DotCandidate]
    photometric_diagnostics: dict[str, int | float] = field(default_factory=dict)


@dataclass(frozen=True)
class _PhotometricFit:
    centers_px: np.ndarray
    before_mse: float
    after_mse: float
    amplitudes: np.ndarray
    background_gradient: np.ndarray
    covariances: np.ndarray
    sample_count: int
    parameter_count: int
    stationary_step_norm: float


def _weighted_center(gray: np.ndarray, contour: np.ndarray) -> tuple[float, float]:
    x, y, width, height = cv2.boundingRect(contour)
    mask = np.zeros((height, width), dtype=np.uint8)
    shifted = contour - np.array([[[x, y]]], dtype=contour.dtype)
    cv2.drawContours(mask, [shifted], -1, 255, thickness=-1)
    weights = (255.0 - gray[y : y + height, x : x + width].astype(np.float64)) * (
        mask.astype(np.float64) / 255.0
    )
    total = float(weights.sum())
    if total <= 0:
        moments = cv2.moments(contour)
        return (
            float(moments["m10"] / moments["m00"]),
            float(moments["m01"] / moments["m00"]),
        )
    yy, xx = np.indices(weights.shape, dtype=np.float64)
    return (
        float(x + np.sum(xx * weights) / total),
        float(y + np.sum(yy * weights) / total),
    )


def _gaussian_center(
    gray: np.ndarray,
    center: tuple[float, float],
    radius: int = 5,
    *,
    bounds: tuple[int, int, int, int] | None = None,
    require_stationary: bool = False,
) -> tuple[tuple[float, float], np.ndarray | None]:
    """Fit raw dot contrast against a sloping background, without a contour mask.

    An elliptical Gaussian accommodates defocus. Affine background terms prevent
    background brightness from pulling the fitted center toward a threshold
    boundary. Invalid fits and incomplete patches retain the supplied center.
    """
    cx, cy = center
    ox, oy = int(round(cx)), int(round(cy))
    x0, y0, x1, y1 = bounds or (
        ox - radius,
        oy - radius,
        ox + radius + 1,
        oy + radius + 1,
    )
    if min(x0, y0) < 0 or x1 > gray.shape[1] or y1 > gray.shape[0]:
        return center, None
    patch = gray[y0:y1, x0:x1].astype(float)
    yy, xx = np.indices(patch.shape, dtype=float)
    border = (
        (xx == 0) | (yy == 0) | (xx == patch.shape[1] - 1) | (yy == patch.shape[0] - 1)
    ).ravel()
    xx, yy = xx.ravel() + x0 - ox, yy.ravel() + y0 - oy
    observed = patch.ravel()
    background_basis = np.stack([np.ones_like(xx), xx, yy], axis=1)
    background = np.linalg.lstsq(
        background_basis[border], observed[border], rcond=None
    )[0]
    amplitude = max(5.0, float(np.max(background_basis @ background - observed)))
    parameters = np.array([*background, amplitude, cx - ox, cy - oy, 0.4, 0.0, 0.4])

    def model_jacobian(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        b0, bx, by, contrast, xc, yc, qxx, qxy, qyy = values
        dx, dy = xx - xc, yy - yc
        exponential = np.exp(
            np.clip(-0.5 * (qxx * dx * dx + 2 * qxy * dx * dy + qyy * dy * dy), -60, 20)
        )
        signal = contrast * exponential
        model = b0 + bx * xx + by * yy - signal
        jacobian = np.stack(
            [
                np.ones_like(xx),
                xx,
                yy,
                -exponential,
                -signal * (qxx * dx + qxy * dy),
                -signal * (qxy * dx + qyy * dy),
                0.5 * signal * dx * dx,
                signal * dx * dy,
                0.5 * signal * dy * dy,
            ],
            axis=1,
        )
        return model, jacobian

    damping = 1e-3
    improved = False
    for _ in range(30):
        model, jacobian = model_jacobian(parameters)
        residual = observed - model
        curvature = jacobian.T @ jacobian
        try:
            step = np.linalg.solve(
                curvature + damping * np.diag(np.maximum(np.diag(curvature), 1e-4)),
                jacobian.T @ residual,
            )
        except np.linalg.LinAlgError:
            return center, None
        candidate = parameters + step
        eigenvalues = np.linalg.eigvalsh(
            [
                [candidate[6], candidate[7]],
                [candidate[7], candidate[8]],
            ]
        )
        valid = (
            eigenvalues.min() > 0.015
            and eigenvalues.max() < 8
            and 1 < candidate[3] < 512
            and max(abs(candidate[4]), abs(candidate[5])) < 2.5
        )
        if valid and np.sum((observed - model_jacobian(candidate)[0]) ** 2) < np.sum(
            residual**2
        ):
            parameters = candidate
            improved = True
            damping = max(damping / 3, 1e-7)
            if np.linalg.norm(step) < 1e-5:
                break
        else:
            damping *= 10
    if not improved:
        return center, None
    if require_stationary:
        predicted, jacobian = model_jacobian(parameters)
        try:
            step = np.linalg.solve(
                jacobian.T @ jacobian, jacobian.T @ (observed - predicted)
            )
        except np.linalg.LinAlgError:
            return center, None
        if not np.all(np.isfinite(step)) or np.linalg.norm(step) >= 1e-5:
            return center, None
    return (float(ox + parameters[4]), float(oy + parameters[5])), parameters


def _scale_space_dots(
    gray: np.ndarray, config: DotDetectorConfig
) -> tuple[list[DotObservation], list[DotCandidate], dict[str, int | float]]:
    image = gray.astype(np.float32)
    response = cv2.GaussianBlur(image, (0, 0), 5) - cv2.GaussianBlur(image, (0, 0), 1)
    maxima = (response == cv2.dilate(response, None)) & (
        response >= config.scale_space_min_response
    )
    if config.scale_space_paper_mask:
        background = cv2.GaussianBlur(gray, (0, 0), 8)
        _, bright = cv2.threshold(
            background, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        light = background[bright > 0]
        dark = background[bright == 0]
        # Segment only a well-separated paper/background image. Flat paper and
        # a smooth illumination gradient do not need a brightness restriction.
        if (
            min(len(light), len(dark)) >= gray.size * 0.1
            and float(light.mean() - dark.mean()) >= 40
        ):
            histogram = np.bincount(background.ravel(), minlength=256) / gray.size
            mass = np.cumsum(histogram)
            moment = np.cumsum(histogram * np.arange(256))
            best = (-1.0, 0, 0)
            for low in range(1, 254):
                high = np.arange(low + 1, 255)
                weights = (mass[low], mass[high] - mass[low], 1 - mass[high])
                moments = (
                    moment[low],
                    moment[high] - moment[low],
                    moment[-1] - moment[high],
                )
                score = sum(
                    np.divide(
                        mm * mm, ww, out=np.zeros_like(high, dtype=float), where=ww > 0
                    )
                    for mm, ww in zip(moments, weights, strict=True)
                )
                peak = int(np.argmax(score))
                if score[peak] > best[0]:
                    best = (float(score[peak]), low, int(high[peak]))
            _, low, high = best
            weights = np.array([mass[low], mass[high] - mass[low], 1 - mass[high]])
            means = np.divide(
                [moment[low], moment[high] - moment[low], moment[-1] - moment[high]],
                weights,
                out=np.zeros(3),
                where=weights > 0,
            )
            # A third well-separated illumination class can be a desk between
            # a dark object and white paper. A two-class threshold admits it.
            if np.all(weights >= 0.1) and np.all(np.diff(means) >= 25):
                bright = (background > high).astype(np.uint8) * 255
            maxima &= bright > 0
    yy, xx = np.nonzero(maxima)
    observations: list[DotObservation] = []
    candidates: list[DotCandidate] = []
    occupied: dict[tuple[int, int], list[tuple[float, float]]] = {}
    seeds: list[tuple[float, float]] = []
    raw_fits: list[np.ndarray] = []
    for offset in np.argsort(response[yy, xx])[::-1]:
        x, y = int(xx[offset]), int(yy[offset])
        if min(x, y) < 5 or x + 5 >= gray.shape[1] or y + 5 >= gray.shape[0]:
            continue
        center, fitted = _gaussian_center(gray, (float(x), float(y)))
        if fitted is None:
            continue
        precision = np.array([[fitted[6], fitted[7]], [fitted[7], fitted[8]]])
        eigenvalues = np.linalg.eigvalsh(precision)
        axes = np.sqrt(2 * np.log(2) / eigenvalues)
        area = float(pi * axes.prod())
        aspect_ratio = float(axes.min() / axes.max())
        perimeter = pi * (
            3 * axes.sum() - np.sqrt((3 * axes[0] + axes[1]) * (axes[0] + 3 * axes[1]))
        )
        circularity = min(1.0, float(4 * pi * area / (perimeter * perimeter)))
        patch_y, patch_x = np.indices((11, 11), dtype=float)
        patch_x, patch_y = patch_x - 5, patch_y - 5
        dx, dy = patch_x - fitted[4], patch_y - fitted[5]
        model = (
            fitted[0]
            + fitted[1] * patch_x
            + fitted[2] * patch_y
            - fitted[3]
            * np.exp(
                -0.5
                * (fitted[6] * dx * dx + 2 * fitted[7] * dx * dy + fitted[8] * dy * dy)
            )
        )
        fit_rms = float(
            np.sqrt(np.mean((gray[y - 5 : y + 6, x - 5 : x + 6] - model) ** 2))
        )
        reason = None
        if 1 / np.sqrt(eigenvalues.max()) < config.scale_space_min_sigma_px:
            reason = RejectionReason.SCALE_TOO_SMALL
        elif fitted[3] < 4 * fit_rms:
            reason = RejectionReason.FIT_CONTRAST
        elif np.linalg.norm(fitted[1:3]) * 10 > fitted[3]:
            reason = RejectionReason.BACKGROUND_EDGE
        elif area < config.min_area_px:
            reason = RejectionReason.AREA_TOO_SMALL
        elif area > config.max_area_px:
            reason = RejectionReason.AREA_TOO_LARGE
        elif aspect_ratio < config.min_aspect_ratio:
            reason = RejectionReason.ASPECT_RATIO
        elif circularity < config.min_circularity:
            reason = RejectionReason.CIRCULARITY
        bucket = (int(center[0] // 2), int(center[1] // 2))
        if reason is None:
            duplicate = any(
                np.hypot(center[0] - previous[0], center[1] - previous[1]) < 2
                for bx in range(bucket[0] - 1, bucket[0] + 2)
                for by in range(bucket[1] - 1, bucket[1] + 2)
                for previous in occupied.get((bx, by), [])
            )
            if duplicate:
                reason = RejectionReason.DUPLICATE
        width = int(np.ceil(axes.max()))
        if reason is None:
            observations.append(
                DotObservation(center_px=center, area_px=area, circularity=circularity)
            )
            occupied.setdefault(bucket, []).append(center)
        seeds.append((float(x), float(y)))
        raw_fits.append(fitted)
        candidates.append(
            DotCandidate(
                center_px=center,
                area_px=area,
                circularity=circularity,
                aspect_ratio=aspect_ratio,
                bounding_box=(x - width, y - width, 2 * width + 1, 2 * width + 1),
                accepted=reason is None,
                rejection_reason=reason,
            )
        )
    diagnostics: dict[str, int | float] = {}
    if config.joint_neighbor_fit:
        diagnostics = _refine_neighbors(gray, candidates, seeds, raw_fits, config)
        # Joint fits can move or revive candidates. Reapply the same uniqueness
        # rule in the original descending raw-response order before exporting.
        occupied.clear()
        for index, candidate in enumerate(candidates):
            if not candidate.accepted:
                continue
            center = candidate.center_px
            bucket = (int(center[0] // 2), int(center[1] // 2))
            duplicate = any(
                np.hypot(center[0] - previous[0], center[1] - previous[1]) < 2
                for bx in range(bucket[0] - 1, bucket[0] + 2)
                for by in range(bucket[1] - 1, bucket[1] + 2)
                for previous in occupied.get((bx, by), [])
            )
            if duplicate:
                candidates[index] = replace(
                    candidate,
                    accepted=False,
                    rejection_reason=RejectionReason.DUPLICATE,
                )
            else:
                occupied.setdefault(bucket, []).append(center)
        observations = [
            DotObservation(
                center_px=c.center_px, area_px=c.area_px, circularity=c.circularity
            )
            for c in candidates
            if c.accepted
        ]
    return observations, candidates, diagnostics


def _fit_neighbor_pair(
    gray: np.ndarray,
    seeds: np.ndarray,
    minimum_sigma: float,
    prior_covariance=None,
    *,
    require_two_source_evidence: bool = False,
    geometry_config: DotDetectorConfig | None = None,
):
    try:
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            shared = _fit_shared_neighbor_pair(
                gray,
                seeds,
                minimum_sigma,
                prior_covariance,
                require_two_source_evidence=require_two_source_evidence,
            )
    except (
        ValueError,
        IndexError,
        OverflowError,
        FloatingPointError,
        np.linalg.LinAlgError,
    ):
        shared = None
    if prior_covariance is None:
        return shared
    # A converged shared PSF can still be biased by genuinely different
    # source widths. Keep its exact result unless the larger model beats both
    # fully optimized competitors on these same pixels by the original BIC gate.
    distinct = _fit_distinct_psf_pair(
        gray,
        seeds,
        minimum_sigma,
        prior_covariance,
        require_two_source_evidence=require_two_source_evidence,
    )
    if distinct is not None and geometry_config is not None:
        if _pair_geometry(distinct, geometry_config) is None:
            distinct = None
    return shared if distinct is None else distinct


def _fit_shared_neighbor_pair(
    gray: np.ndarray,
    seeds: np.ndarray,
    minimum_sigma: float,
    prior_covariance=None,
    *,
    require_two_source_evidence: bool = False,
):
    """Fit two raw maxima with separate amplitudes and one shared optical PSF.

    No lattice geometry enters this fit, and it never invents an image peak.
    Shared covariance avoids giving the spots arbitrary separate shapes. When
    isolated nearby dots exist, their PSF also constrains the decomposition.
    """
    x0, y0 = np.floor(seeds.min(axis=0)).astype(int) - 5
    x1, y1 = np.ceil(seeds.max(axis=0)).astype(int) + 6
    if min(x0, y0) < 0 or x1 > gray.shape[1] or y1 > gray.shape[0]:
        return None
    patch = gray[y0:y1, x0:x1].astype(float)
    yy, xx = np.indices(patch.shape, dtype=float)
    xx, yy = xx.ravel(), yy.ravel()
    target = patch.ravel()
    border = (
        (xx == 0) | (yy == 0) | (xx == patch.shape[1] - 1) | (yy == patch.shape[0] - 1)
    )
    basis = np.stack([np.ones_like(xx), xx, yy], axis=1)
    background = np.linalg.lstsq(basis[border], target[border], rcond=None)[0]
    initial = seeds - [x0, y0]
    amplitudes = [
        max(5.0, background @ [1.0, cx, cy] - patch[round(cy), round(cx)])
        for cx, cy in initial
    ]
    try:
        prior_precision = (
            np.eye(2) * 0.4
            if prior_covariance is None
            else np.linalg.inv(prior_covariance)
        )
    except np.linalg.LinAlgError:
        return None
    p = np.array(
        [
            *background,
            amplitudes[0],
            *initial[0],
            amplitudes[1],
            *initial[1],
            prior_precision[0, 0],
            prior_precision[0, 1],
            prior_precision[1, 1],
        ]
    )

    def model_jac(values):
        b0, bx, by, a0, cx0, cy0, a1, cx1, cy1, qxx, qxy, qyy = values
        dx0, dy0, dx1, dy1 = xx - cx0, yy - cy0, xx - cx1, yy - cy1
        e0 = np.exp(
            np.clip(
                -0.5 * (qxx * dx0 * dx0 + 2 * qxy * dx0 * dy0 + qyy * dy0 * dy0),
                -60,
                20,
            )
        )
        e1 = np.exp(
            np.clip(
                -0.5 * (qxx * dx1 * dx1 + 2 * qxy * dx1 * dy1 + qyy * dy1 * dy1),
                -60,
                20,
            )
        )
        s0, s1 = a0 * e0, a1 * e1
        model = b0 + bx * xx + by * yy - s0 - s1
        jac = np.stack(
            [
                np.ones_like(xx),
                xx,
                yy,
                -e0,
                -s0 * (qxx * dx0 + qxy * dy0),
                -s0 * (qxy * dx0 + qyy * dy0),
                -e1,
                -s1 * (qxx * dx1 + qxy * dy1),
                -s1 * (qxy * dx1 + qyy * dy1),
                0.5 * (s0 * dx0 * dx0 + s1 * dx1 * dx1),
                s0 * dx0 * dy0 + s1 * dx1 * dy1,
                0.5 * (s0 * dy0 * dy0 + s1 * dy1 * dy1),
            ],
            axis=1,
        )
        return model, jac

    before = float(np.mean((target - model_jac(p)[0]) ** 2))
    damping = 1e-3
    improved = False
    for _ in range(80 if require_two_source_evidence else 40):
        model, jac = model_jac(p)
        residual = target - model
        curvature = jac.T @ jac
        try:
            delta = np.linalg.solve(
                curvature + damping * np.diag(np.maximum(np.diag(curvature), 1e-4)),
                jac.T @ residual,
            )
        except np.linalg.LinAlgError:
            return None
        trial = p + delta
        centers = np.array([trial[4:6], trial[7:9]])
        eigenvalues = np.linalg.eigvalsh(
            [[trial[9], trial[10]], [trial[10], trial[11]]]
        )
        valid = (
            eigenvalues.min() > 0.015
            and eigenvalues.max() < 1 / minimum_sigma**2
            and min(trial[3], trial[6]) > 1
            and max(trial[3], trial[6]) < 512
            and np.max(np.linalg.norm(centers - initial, axis=1)) < 3
            and np.linalg.norm(centers[0] - centers[1]) > 3
        )
        if valid and np.sum((target - model_jac(trial)[0]) ** 2) < np.sum(residual**2):
            p = trial
            damping = max(damping / 3, 1e-7)
            improved = True
            if np.linalg.norm(delta) < 1e-5:
                break
        else:
            damping *= 10
    after = float(np.mean((target - model_jac(p)[0]) ** 2))
    if not improved or min(p[3], p[6]) < 4 * np.sqrt(after):
        return None
    precision = np.array([[p[9], p[10]], [p[10], p[11]]])
    covariance = np.linalg.inv(precision)
    if prior_covariance is not None:
        try:
            transform = np.linalg.cholesky(prior_precision)
        except np.linalg.LinAlgError:
            return None
        relative = np.linalg.eigvalsh(transform.T @ covariance @ transform)
        minimum_separation = (1.5 if require_two_source_evidence else 2) * np.sqrt(
            np.linalg.eigvalsh(prior_covariance).max()
        )
        if (
            relative.min() < 0.5
            or relative.max() > 2
            or np.linalg.norm(p[4:6] - p[7:9]) < minimum_separation
        ):
            return None
    # A constrained trial can make damping large enough to shrink its step
    # below the stopping tolerance while the fit is still far from stationary.
    # Retain the single-dot candidates unless an undamped step also converged.
    model, jac = model_jac(p)
    try:
        stationary_step = np.linalg.solve(jac.T @ jac, jac.T @ (target - model))
    except np.linalg.LinAlgError:
        return None
    if (
        not np.all(np.isfinite(stationary_step))
        or np.linalg.norm(stationary_step) >= 1e-5
    ):
        return None
    if require_two_source_evidence:
        midpoint = tuple(np.mean(seeds, axis=0))
        _, single = _gaussian_center(
            gray, midpoint, bounds=(x0, y0, x1, y1), require_stationary=True
        )
        if single is None:
            return None
        ox, oy = np.rint(midpoint).astype(int)
        sx, sy = xx + x0 - ox, yy + y0 - oy
        dx, dy = sx - single[4], sy - single[5]
        single_model = (
            single[0]
            + single[1] * sx
            + single[2] * sy
            - single[3]
            * np.exp(
                -0.5
                * (single[6] * dx * dx + 2 * single[7] * dx * dy + single[8] * dy * dy)
            )
        )
        single_sse = float(np.sum((target - single_model) ** 2))
        pair_sse = after * len(target)
        # Both optimized models use identical raw pixels and affine background.
        # The pair adds three parameters; strong BIC evidence is required.
        bic_improvement = len(target) * np.log(
            max(single_sse, 1e-12) / max(pair_sse, 1e-12)
        ) - 3 * np.log(len(target))
        if bic_improvement <= 10:
            return None
    return _PhotometricFit(
        centers_px=np.array([p[4:6], p[7:9]]) + [x0, y0],
        before_mse=before,
        after_mse=after,
        amplitudes=p[[3, 6]],
        background_gradient=p[1:3],
        covariances=np.array([covariance, covariance]),
        sample_count=len(target),
        parameter_count=12,
        stationary_step_norm=float(np.linalg.norm(stationary_step)),
    )


def _fit_profiled_sources(gray, seeds, minimum_sigma, prior_covariance, model):
    """Optimize source shapes with exact linear background/amplitude fits.

    The residual term in the profiled Jacobian accounts for the changing
    least-squares amplitudes. The final stopping test still uses the full,
    undamped 9/12/15-parameter system, including those linear parameters.
    """
    try:
        seeds = np.asarray(seeds, dtype=float)
        prior = np.asarray(prior_covariance, dtype=float)
        if (
            seeds.shape != (2, 2)
            or prior.shape != (2, 2)
            or not np.all(np.isfinite(seeds))
            or not np.all(np.isfinite(prior))
            or not np.allclose(prior, prior.T)
            or not np.isfinite(minimum_sigma)
            or minimum_sigma <= 0
            or np.linalg.eigvalsh(prior).min() <= 0
        ):
            return None
        x0, y0 = np.floor(seeds.min(axis=0)).astype(int) - 5
        x1, y1 = np.ceil(seeds.max(axis=0)).astype(int) + 6
        if min(x0, y0) < 0 or x1 > gray.shape[1] or y1 > gray.shape[0]:
            return None
        target = gray[y0:y1, x0:x1].astype(float).ravel()
        if len(target) <= 15 or not np.all(np.isfinite(target)):
            return None
        yy, xx = np.indices((y1 - y0, x1 - x0), dtype=float)
        xx, yy = xx.ravel(), yy.ravel()
        count = 1 if model == "single" else 2
        shape_count = 2 if model == "independent" else 1
        initial = (seeds.mean(axis=0)[None] if count == 1 else seeds) - [x0, y0]
        precision = np.linalg.inv(prior)
        theta = np.r_[
            initial.ravel(),
            np.tile([precision[0, 0], precision[0, 1], precision[1, 1]], shape_count),
        ]
        background_basis = np.column_stack((np.ones_like(xx), xx, yy))

        def evaluate(values):
            if not np.all(np.isfinite(values)):
                return None
            centers = values[: 2 * count].reshape(count, 2)
            precisions = values[2 * count :].reshape(shape_count, 3)
            limit = 8 if count == 1 else 1 / minimum_sigma**2
            for qxx, qxy, qyy in precisions:
                eigenvalues = np.linalg.eigvalsh([[qxx, qxy], [qxy, qyy]])
                if eigenvalues.min() <= 0.015 or eigenvalues.max() >= limit:
                    return None
            motion = centers - initial
            if (count == 1 and np.max(np.abs(motion)) >= 2.5) or (
                count == 2
                and (
                    np.max(np.linalg.norm(motion, axis=1)) >= 3
                    or np.linalg.norm(centers[0] - centers[1]) <= 3
                )
            ):
                return None
            exponentials, derivatives = [], []
            for index in range(count):
                qxx, qxy, qyy = precisions[index if shape_count == 2 else 0]
                dx, dy = xx - centers[index, 0], yy - centers[index, 1]
                exponential = np.exp(
                    np.clip(
                        -0.5 * (qxx * dx**2 + 2 * qxy * dx * dy + qyy * dy**2), -60, 20
                    )
                )
                derivative = np.zeros((len(target), len(values)))
                derivative[:, 2 * index : 2 * index + 2] = np.column_stack(
                    (qxx * dx + qxy * dy, qxy * dx + qyy * dy)
                )
                offset = 2 * count + 3 * (index if shape_count == 2 else 0)
                derivative[:, offset : offset + 3] = np.column_stack(
                    (-0.5 * dx**2, -dx * dy, -0.5 * dy**2)
                )
                exponentials.append(exponential)
                derivatives.append(derivative)
            basis = np.column_stack((background_basis, -np.column_stack(exponentials)))
            linear, _, rank, _ = np.linalg.lstsq(basis, target, rcond=None)
            if (
                rank != count + 3
                or not np.all(np.isfinite(linear))
                or linear[3:].min() <= 1
                or linear[3:].max() >= 512
            ):
                return None
            residual = target - basis @ linear
            nonlinear_jacobian = sum(
                -linear[3 + k] * exponentials[k][:, None] * derivatives[k]
                for k in range(count)
            )
            transpose_residual = np.zeros((count + 3, len(values)))
            for index in range(count):
                transpose_residual[3 + index] = (
                    -exponentials[index][:, None] * derivatives[index]
                ).T @ residual
            orthogonal, _ = np.linalg.qr(basis, mode="reduced")
            jacobian = (
                nonlinear_jacobian
                - orthogonal @ (orthogonal.T @ nonlinear_jacobian)
                + np.linalg.pinv(basis).T @ transpose_residual
            )
            full_jacobian = np.column_stack((basis, nonlinear_jacobian))
            full_step = np.linalg.solve(
                full_jacobian.T @ full_jacobian, full_jacobian.T @ residual
            )
            if not np.all(np.isfinite(full_step)):
                return None
            return (
                float(residual @ residual),
                residual,
                jacobian,
                float(np.linalg.norm(full_step)),
                linear,
                centers,
                precisions,
            )

        with np.errstate(over="raise", invalid="raise", divide="raise"):
            state = evaluate(theta)
            if state is None:
                return None
            before = state[0] / len(target)
            damping = 1e-3
            for _ in range(80):
                if state[3] < 1e-5:
                    break
                curvature = state[2].T @ state[2]
                delta = np.linalg.solve(
                    curvature + damping * np.diag(np.maximum(np.diag(curvature), 1e-4)),
                    state[2].T @ state[1],
                )
                trial = theta + delta
                trial_state = evaluate(trial)
                if trial_state is not None and trial_state[0] < state[0]:
                    theta, state = trial, trial_state
                    damping = max(damping / 3, 1e-7)
                else:
                    damping *= 10
            if state[3] >= 1e-5:
                return None
            covariances = np.array(
                [np.linalg.inv([[qxx, qxy], [qxy, qyy]]) for qxx, qxy, qyy in state[6]]
            )
            if shape_count == 1 and count == 2:
                covariances = np.repeat(covariances, 2, axis=0)
            return _PhotometricFit(
                centers_px=state[5] + [x0, y0],
                before_mse=before,
                after_mse=state[0] / len(target),
                amplitudes=state[4][3:],
                background_gradient=state[4][1:3],
                covariances=covariances,
                sample_count=len(target),
                parameter_count=3 + 3 * count + 3 * shape_count,
                stationary_step_norm=state[3],
            )
    except (ValueError, OverflowError, FloatingPointError, np.linalg.LinAlgError):
        return None


def _fit_distinct_psf_pair(
    gray, seeds, minimum_sigma, prior_covariance, *, require_two_source_evidence=False
):
    """Require evidence for two sources and for their three extra PSF terms."""
    independent = _fit_profiled_sources(
        gray, seeds, minimum_sigma, prior_covariance, "independent"
    )
    if independent is None:
        return None
    mse = independent.after_mse
    if (
        independent.amplitudes.min() < 4 * np.sqrt(mse)
        or np.linalg.norm(independent.background_gradient) * 10
        > independent.amplitudes.min()
    ):
        return None
    transform = np.linalg.cholesky(np.linalg.inv(prior_covariance))
    for covariance in independent.covariances:
        relative = np.linalg.eigvalsh(transform.T @ covariance @ transform)
        if relative.min() < 0.5 or relative.max() > 2:
            return None
    if np.linalg.norm(independent.centers_px[0] - independent.centers_px[1]) < (
        (1.5 if require_two_source_evidence else 2)
        * np.sqrt(np.linalg.eigvalsh(prior_covariance).max())
    ):
        return None
    # The competitors are optimized on exactly the same source-seed bounds.
    # An unconverged competitor cannot be used as evidence for added parameters.
    for model in ("single", "shared"):
        competitor = _fit_profiled_sources(
            gray, seeds, minimum_sigma, prior_covariance, model
        )
        if competitor is None:
            return None
        size = independent.sample_count
        improvement = size * np.log(
            max(competitor.after_mse, 1e-12) / max(mse, 1e-12)
        ) - (independent.parameter_count - competitor.parameter_count) * np.log(size)
        if improvement <= 10:
            return None
    return independent


def _pair_geometry(fit, config):
    geometries = []
    for covariance in fit.covariances:
        axes = np.sqrt(2 * np.log(2) * np.linalg.eigvalsh(covariance))
        area = float(pi * axes.prod())
        aspect = float(axes.min() / axes.max())
        perimeter = pi * (
            3 * axes.sum() - np.sqrt((3 * axes[0] + axes[1]) * (axes[0] + 3 * axes[1]))
        )
        circularity = min(1.0, float(4 * pi * area / perimeter**2))
        if not (
            config.min_area_px <= area <= config.max_area_px
            and aspect >= config.min_aspect_ratio
            and circularity >= config.min_circularity
        ):
            return None
        geometries.append((area, aspect, circularity))
    if np.linalg.norm(fit.background_gradient) * 10 > fit.amplitudes.min():
        return None
    return geometries


def estimate_psf_covariance(covariances: list[np.ndarray]) -> np.ndarray:
    """Aggregate valid optical covariances without producing a singular PSF.

    Entrywise medians resist distorted fits but do not preserve positive
    definiteness. The mean of the valid SPD inputs provides a safe fallback.
    """
    median = np.median(covariances, axis=0)
    eigenvalues = np.linalg.eigvalsh(median)
    if eigenvalues.min() <= 1e-6 * eigenvalues.max():
        return np.mean(covariances, axis=0)
    return median


def _deblend_elongated(
    gray, candidates, seeds, raw_fits, nearest_distances, resolved, config
):
    """Test elongated single spots against a local-PSF two-source alternative."""
    reference_indices = np.array(
        [
            k
            for k in range(len(seeds))
            if nearest_distances[k] >= 9
            and candidates[k].accepted
            and np.linalg.norm(np.asarray(candidates[k].center_px) - seeds[k]) < 1.5
        ],
        dtype=int,
    )
    if len(reference_indices) < 4:
        return 0, 0
    reference_points = np.asarray(seeds)[reference_indices]
    covariances = np.linalg.inv(
        np.array([[[fit[6], fit[7]], [fit[7], fit[8]]] for fit in raw_fits])
    )
    attempted = accepted = 0
    order = sorted(
        range(len(seeds)),
        key=lambda k: np.linalg.eigvalsh(covariances[k]).max(),
        reverse=True,
    )
    for index in order:
        # A merged pair can be too long to qualify as a single dot. Its
        # single-model aspect rejection must not prevent testing a pair whose
        # own contrast, shape, PSF, stationarity and BIC still have to pass.
        if index in resolved or (
            not candidates[index].accepted
            and candidates[index].rejection_reason != RejectionReason.ASPECT_RATIO
        ):
            continue
        center = np.asarray(candidates[index].center_px)
        distances = np.linalg.norm(reference_points - center, axis=1)
        reference = reference_indices[(distances > 12) & (distances < 80)]
        if len(reference) < 4:
            continue
        prior = estimate_psf_covariance(covariances[reference])
        covariance = covariances[index]
        whitening = np.linalg.cholesky(np.linalg.inv(prior))
        relative = np.linalg.eigvalsh(whitening.T @ covariance @ whitening)
        if relative.max() <= 2 or relative.min() < 0.4:
            continue
        _, vectors = np.linalg.eigh(covariance)
        axis = vectors[:, -1]
        half_separation = 1.25 * np.sqrt(axis @ prior @ axis)
        trial_seeds = center + np.array([-1, 1])[:, None] * half_separation * axis
        attempted += 1
        result = _fit_neighbor_pair(
            gray,
            trial_seeds,
            config.scale_space_min_sigma_px,
            prior,
            require_two_source_evidence=True,
            geometry_config=config,
        )
        if result is None:
            continue
        centers = result.centers_px
        geometries = _pair_geometry(result, config)
        if geometries is None:
            continue
        if any(
            np.min(
                np.linalg.norm(
                    centers - np.asarray(candidates[other].center_px), axis=1
                )
            )
            < 2
            for other in resolved
        ):
            continue
        template = candidates[index]
        replacements = [
            replace(
                template,
                center_px=tuple(map(float, point)),
                area_px=area,
                aspect_ratio=aspect,
                circularity=circularity,
                accepted=True,
                rejection_reason=None,
            )
            for point, (area, aspect, circularity) in zip(
                centers, geometries, strict=True
            )
        ]
        candidates[index] = replacements[0]
        candidates.append(replacements[1])
        already_resolved = set(resolved)
        resolved.add(index)
        for other in range(len(seeds)):
            if other in already_resolved:
                continue
            distances_to_sources = np.linalg.norm(
                centers - np.asarray(candidates[other].center_px), axis=1
            )
            if distances_to_sources.min() >= 2:
                # A blended single can drift away from its own raw peak.
                # Preserve that peak's existing 2px link to this optical model.
                distances_to_sources = np.linalg.norm(
                    centers - np.asarray(seeds[other]), axis=1
                )
            if distances_to_sources.min() < 2:
                # A validated optical model replaces its older single modes;
                # raw-response order must not restore a biased old center.
                source = int(distances_to_sources.argmin())
                area, aspect, circularity = geometries[source]
                candidates[other] = replace(
                    candidates[other],
                    center_px=tuple(map(float, centers[source])),
                    area_px=area,
                    aspect_ratio=aspect,
                    circularity=circularity,
                )
                resolved.add(other)
        accepted += 1
    return attempted, accepted


def _refine_neighbors(gray, candidates, seeds, raw_fits, config):
    buckets: dict[tuple[int, int], list[int]] = {}
    for i, (x, y) in enumerate(seeds):
        buckets.setdefault((int(x // 9), int(y // 9)), []).append(i)
    nearest = []
    nearest_distances = []
    possible_pairs: dict[tuple[int, int], float] = {}
    for i, (x, y) in enumerate(seeds):
        bx, by = int(x // 9), int(y // 9)
        others = [
            j
            for dx in [-1, 0, 1]
            for dy in [-1, 0, 1]
            for j in buckets.get((bx + dx, by + dy), [])
            if j != i
        ]
        for j in others:
            separation = float(np.linalg.norm(np.asarray(seeds[j]) - [x, y]))
            if j > i and 3 <= separation < 9:
                possible_pairs[i, j] = separation
        neighbor = min(
            others,
            key=lambda j: np.linalg.norm(np.asarray(seeds[j]) - [x, y]),
            default=-1,
        )
        nearest_distances.append(
            np.linalg.norm(np.asarray(seeds[neighbor]) - [x, y])
            if neighbor >= 0
            else np.inf
        )
        nearest.append(
            neighbor
            if neighbor >= 0
            and 3 <= np.linalg.norm(np.asarray(seeds[neighbor]) - [x, y]) < 9
            else -1
        )
    primary_pairs = [(i, j) for i, j in enumerate(nearest) if j > i and nearest[j] == i]
    primary_set = set(primary_pairs)
    # A shoulder maximum can make two single fits collapse to the same spot.
    # Preserve the existing mutual-neighbor trials, then allow those collapsed
    # fits to separate through the same raw photometric validity checks.
    fallback_pairs = sorted(
        (
            pair
            for pair in possible_pairs
            if pair not in primary_set
            and np.linalg.norm(
                np.asarray(candidates[pair[0]].center_px)
                - candidates[pair[1]].center_px
            )
            < 2
        ),
        key=possible_pairs.__getitem__,
    )
    resolved: set[int] = set()
    attempted = accepted = prior_restricted = 0
    shifts = []
    improvements = []
    for i, j in [*primary_pairs, *fallback_pairs]:
        if i in resolved or j in resolved:
            continue
        attempted += 1
        midpoint = (np.asarray(seeds[i]) + seeds[j]) / 2
        isolated = [
            k
            for k in range(len(seeds))
            if nearest[k] < 0
            and candidates[k].accepted
            and np.linalg.norm(np.asarray(seeds[k]) - midpoint) < 80
        ]
        prior = None
        if len(isolated) >= 4:
            covariances = [
                np.linalg.inv(
                    [[raw_fits[k][6], raw_fits[k][7]], [raw_fits[k][7], raw_fits[k][8]]]
                )
                for k in isolated
            ]
            prior = estimate_psf_covariance(covariances)
            prior_restricted += 1
        result = _fit_neighbor_pair(
            gray,
            np.asarray([seeds[i], seeds[j]]),
            config.scale_space_min_sigma_px,
            prior,
            geometry_config=config,
        )
        if result is None:
            continue
        centers = result.centers_px
        geometries = _pair_geometry(result, config)
        if geometries is None:
            continue
        accepted += 1
        resolved.update((i, j))
        improvements.append(result.before_mse - result.after_mse)
        for index, center, (area, aspect, circularity) in zip(
            [i, j], centers, geometries, strict=True
        ):
            shifts.append(
                float(np.linalg.norm(np.asarray(candidates[index].center_px) - center))
            )
            candidates[index] = replace(
                candidates[index],
                center_px=tuple(map(float, center)),
                area_px=area,
                aspect_ratio=aspect,
                circularity=circularity,
                accepted=True,
                rejection_reason=None,
            )
    deblend_attempted, deblend_accepted = _deblend_elongated(
        gray, candidates, seeds, raw_fits, nearest_distances, resolved, config
    )
    return dict(
        neighbor_pairs_attempted=attempted,
        neighbor_pairs_accepted=accepted,
        neighbor_pairs_fallback=attempted - accepted,
        neighbor_pairs_with_local_psf=prior_restricted,
        neighbor_max_shift_px=max(shifts, default=0.0),
        neighbor_mean_shift_px=float(np.mean(shifts)) if shifts else 0.0,
        neighbor_mean_fit_mse_improvement=float(np.mean(improvements))
        if improvements
        else 0.0,
        elongated_deblends_attempted=deblend_attempted,
        elongated_deblends_accepted=deblend_accepted,
    )


def _analyze_dots(
    gray: np.ndarray,
    config: DotDetectorConfig,
    *,
    capture_stages: bool,
) -> DotDetectionResult:
    if not isinstance(gray, np.ndarray) or gray.ndim != 2 or gray.dtype != np.uint8:
        raise ValueError("gray must be a 2D uint8 NumPy array")
    preprocessed = preprocess_image(
        gray,
        config,
        capture_stages=capture_stages,
    )
    if config.candidate_method == "scale_space":
        observations, candidates, diagnostics = _scale_space_dots(
            preprocessed.processed_gray, config
        )
        observations.sort(key=lambda item: (item.center_px[1], item.center_px[0]))
        candidates.sort(key=lambda item: (item.center_px[1], item.center_px[0]))
        if config.grid_refinement:
            observations, refinement = _grid_refine(
                preprocessed.processed_gray, observations
            )
            diagnostics = {**diagnostics, **refinement}
        return DotDetectionResult(
            observations,
            preprocessed.binary,
            preprocessed.stages,
            candidates,
            diagnostics,
        )
    contours, _ = cv2.findContours(
        preprocessed.binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )
    observations: list[DotObservation] = []
    candidates: list[DotCandidate] = []
    for contour in contours:
        area = float(cv2.contourArea(contour))
        x, y, width, height = cv2.boundingRect(contour)
        aspect_ratio = min(width, height) / max(width, height)
        perimeter = float(cv2.arcLength(contour, True))
        circularity = (
            min(1.0, 4.0 * pi * area / (perimeter * perimeter))
            if perimeter > 0
            else 0.0
        )
        moments = cv2.moments(contour)
        if moments["m00"] > 0:
            geometric_center = (
                float(moments["m10"] / moments["m00"]),
                float(moments["m01"] / moments["m00"]),
            )
        else:
            geometric_center = (x + (width - 1) / 2.0, y + (height - 1) / 2.0)

        reason: RejectionReason | None = None
        if area < config.min_area_px:
            reason = RejectionReason.AREA_TOO_SMALL
        elif area > config.max_area_px:
            reason = RejectionReason.AREA_TOO_LARGE
        elif aspect_ratio < config.min_aspect_ratio:
            reason = RejectionReason.ASPECT_RATIO
        elif circularity < config.min_circularity:
            reason = RejectionReason.CIRCULARITY

        center = geometric_center
        if reason is None:
            # Contours are expressed in the preprocessed image coordinate
            # system, so centroid weights must come from that same image
            # (especially after distortion correction or CLAHE).
            center = _weighted_center(preprocessed.processed_gray, contour)
            if config.centroid_method == "gaussian":
                center, _ = _gaussian_center(preprocessed.processed_gray, center)
            observations.append(
                DotObservation(
                    center_px=center,
                    area_px=area,
                    circularity=circularity,
                )
            )
        candidates.append(
            DotCandidate(
                center_px=center,
                area_px=area,
                circularity=circularity,
                aspect_ratio=aspect_ratio,
                bounding_box=(x, y, width, height),
                accepted=reason is None,
                rejection_reason=reason,
            )
        )

    observations.sort(key=lambda item: (item.center_px[1], item.center_px[0]))
    candidates.sort(key=lambda item: (item.center_px[1], item.center_px[0]))
    return DotDetectionResult(
        observations=observations,
        binary=preprocessed.binary,
        stages=preprocessed.stages,
        candidates=candidates,
    )


def _grid_refine(
    gray: np.ndarray, observations: list[DotObservation]
) -> tuple[list[DotObservation], dict[str, int]]:
    """Repair merged/split/missing dots once a blind lattice fit exists."""
    from digital_pen.vision.grid_fitter import fit_grid
    from digital_pen.vision.grid_refinement import refine_with_grid

    try:
        fit = fit_grid(observations)
        refined, stats = refine_with_grid(gray, observations, fit)
    except (ValueError, np.linalg.LinAlgError, cv2.error):
        return observations, {"grid_refinement_failed": 1}
    return refined, {f"grid_refinement_{key}": value for key, value in stats.items()}


def analyze_dots(gray: np.ndarray, config: DotDetectorConfig) -> DotDetectionResult:
    """Run detection while retaining candidates and intermediate stage images."""
    return _analyze_dots(gray, config, capture_stages=True)


def detect_dots(
    gray: np.ndarray, config: DotDetectorConfig
) -> tuple[list[DotObservation], np.ndarray]:
    """Detect black dots; binary foreground pixels always have value 255."""
    result = _analyze_dots(gray, config, capture_stages=False)
    return result.observations, result.binary
