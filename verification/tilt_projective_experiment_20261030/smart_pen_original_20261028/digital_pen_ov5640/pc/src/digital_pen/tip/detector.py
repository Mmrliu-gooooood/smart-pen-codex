"""Pen-tip detection in frames of the fixed overhead camera (Task 10).

Seen from above, the pen is a dark cone whose apex is the tip; hand, ink and
the printed dots are the clutter around it. Per frame:

1. Darkness map: ``1 - gray / paper``, where the paper level is a high
   percentile of the frame after a closing that removes dots and ink.
2. Candidates: normalised correlation with dark wedges (the cone) at
   ``orientations`` directions on a half-resolution map; the strongest local
   maxima, each with its wedge direction, are the candidates. Tracker hints
   (predicted tip and pen direction) are added as extra candidates.
3. Patch model: for each candidate a rotation-normalised patch (pen axis along
   +x, tip near the centre) is fed to a small MLP that scores "tip here" and
   regresses the offset to the tip along and across the axis. The offset is
   applied a few times, then the best-scoring candidate wins.

The wedge stage is purely geometric; the MLP was trained on the Task 9
labels (artifacts/tip-detection-2026-10/train_tip_model.py). Positions are in
pixels of the frame passed in (ROI or full frame); the caller adds the ROI
origin. ``theta`` is the pen direction from hand to tip, in image axes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

# v2: trained with precise re-labels (tip ~2 px further forward than the
# Task 9 labels). v1 (Task 9 labels only) stays the better coarse searcher on
# upsampled overview images, so tracking uses it to re-find a lost pen.
MODEL_PATH = Path(__file__).with_name("tip_model_v2.npz")
COARSE_MODEL_PATH = Path(__file__).with_name("tip_model_v1.npz")
MODEL_SCHEMA = "tip-patch-mlp-v1"

# Patch geometry (pixels, pen axis frame): a fine patch around the tip and a
# coarse context patch reaching back along the pen towards the hand.
FINE_ALONG = np.arange(-20.0, 12.0, 1.0)
FINE_ACROSS = np.arange(-7.5, 8.0, 1.0)
CONTEXT_ALONG = np.arange(-46.0, 10.0, 3.5)
CONTEXT_ACROSS = np.arange(-26.25, 27.0, 3.5)
FEATURES = FINE_ALONG.size * FINE_ACROSS.size + CONTEXT_ALONG.size * CONTEXT_ACROSS.size
# Regression outputs are in units of this many pixels.
OFFSET_UNIT_PX = 4.0


@dataclass(frozen=True)
class TipDetectorConfig:
    orientations: int = 24
    wedge_half_angle_deg: float = 9.0
    wedge_length_px: float = 36.0
    wedge_apex_width_px: float = 1.2
    template_size: int = 25  # at the coarse scale
    coarse_scale: float = 0.5
    # Wedge score = NCC x min(1, contrast / full_contrast).
    full_contrast: float = 0.25
    max_candidates: int = 8
    candidate_separation_px: float = 6.0
    min_candidate_score: float = 0.15
    refine_iterations: int = 3
    # Largest step one refinement may take (a wild regression cannot jump to
    # another object).
    max_step_px: float = 16.0
    # Detection threshold on the MLP logit.
    threshold: float = 0.0
    # Shift of the reported tip along the pen axis (towards the tip); None:
    # the value calibrated with the model (metadata "tip_offset_px", else 0).
    tip_offset_px: float | None = None

    def __post_init__(self) -> None:
        if self.orientations < 8 or not 0 < self.coarse_scale <= 1:
            raise ValueError("need >= 8 orientations and a scale in (0, 1]")
        if self.template_size % 2 == 0:
            raise ValueError("template_size must be odd")


@dataclass(frozen=True)
class TipDetection:
    found: bool
    x: float
    y: float
    theta: float
    score: float
    candidates: int = 0

    def shifted(self, dx: float, dy: float) -> TipDetection:
        """The same detection with the position moved (e.g. by the ROI origin)."""
        return TipDetection(
            self.found,
            self.x + dx,
            self.y + dy,
            self.theta,
            self.score,
            self.candidates,
        )


NOT_FOUND = TipDetection(False, float("nan"), float("nan"), float("nan"), -np.inf)


def darkness_map(gray: np.ndarray) -> np.ndarray:
    """Float32 darkness relative to the paper level, clipped to [0, 1]."""
    if not isinstance(gray, np.ndarray) or gray.ndim != 2 or gray.dtype != np.uint8:
        raise ValueError("gray must be a 2D uint8 NumPy array")
    closed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    paper = max(1.0, float(np.percentile(closed, 90)))
    smooth = cv2.GaussianBlur(gray, (0, 0), 1.0).astype(np.float32)
    return np.clip((paper - smooth) / paper, 0.0, 1.0)


def _wedge(theta, half_angle, length, size, apex_width):
    """Zero-mean wedge template (+1 inside, -1 in a band around) and its support."""
    r = size // 2
    ys, xs = np.mgrid[-r : r + 1, -r : r + 1].astype(np.float32)
    u = (np.cos(theta), np.sin(theta))
    behind = -(xs * u[0] + ys * u[1])
    across = np.abs(-xs * u[1] + ys * u[0])
    width = behind * np.tan(half_angle) + apex_width
    inside = (behind >= 0) & (behind <= length) & (across <= width)
    support = (across <= width + 4) & (behind >= -5) & (behind <= length)
    template = np.where(inside, 1.0, -1.0).astype(np.float32)
    template[~support] = 0
    template[support] -= template[support].mean()
    return template, support.astype(np.float32)


class PatchModel:
    """MLP on rotation-normalised patches: (tip logit, along, across offsets)."""

    def __init__(self, weights, biases, mean, scale, metadata=None):
        self.weights = [np.asarray(w, np.float32) for w in weights]
        self.biases = [np.asarray(b, np.float32) for b in biases]
        self.mean = np.asarray(mean, np.float32)
        self.scale = np.asarray(scale, np.float32)
        self.metadata = dict(metadata or {})
        if self.weights[0].shape[0] != FEATURES or self.weights[-1].shape[1] != 3:
            raise ValueError("model does not match the patch geometry")

    def forward(self, features: np.ndarray) -> np.ndarray:
        h = (np.asarray(features, np.float32) - self.mean) / self.scale
        for i, (w, b) in enumerate(zip(self.weights, self.biases, strict=True)):
            h = h @ w + b
            if i < len(self.weights) - 1:
                h = np.maximum(h, 0)
        return h

    def save(self, path: str | Path) -> None:
        arrays = {f"w{i}": w for i, w in enumerate(self.weights)}
        arrays.update({f"b{i}": b for i, b in enumerate(self.biases)})
        meta = {"schema": MODEL_SCHEMA, **self.metadata}
        np.savez_compressed(
            path, mean=self.mean, scale=self.scale, metadata=json.dumps(meta), **arrays
        )

    @classmethod
    def load(cls, path: str | Path = MODEL_PATH) -> PatchModel:
        with np.load(path) as data:
            meta = json.loads(str(data["metadata"]))
            if meta.get("schema") != MODEL_SCHEMA:
                raise ValueError(f"{path}: unknown model schema {meta.get('schema')!r}")
            layers = sum(1 for k in data.files if k.startswith("w"))
            return cls(
                [data[f"w{i}"] for i in range(layers)],
                [data[f"b{i}"] for i in range(layers)],
                data["mean"],
                data["scale"],
                meta,
            )


def _axis(theta):
    u = np.array((np.cos(theta), np.sin(theta)))
    return u, np.array((-u[1], u[0]))


def _grid(centre, theta, along, across):
    u, n = _axis(theta)
    points = (
        np.asarray(centre, float)[None, None]
        + along[None, :, None] * u
        + across[:, None, None] * n
    )
    return points[..., 0].astype(np.float32), points[..., 1].astype(np.float32)


@dataclass
class FrameMaps:
    """Per-frame maps shared by candidate search and patch refinement."""

    darkness: np.ndarray
    context: np.ndarray
    candidates: list[tuple[tuple[float, float], float, float]] = field(
        default_factory=list
    )
    wedge_scores: np.ndarray | None = None


def patch_features(maps: FrameMaps, centre, theta) -> np.ndarray:
    fx, fy = _grid(centre, theta, FINE_ALONG, FINE_ACROSS)
    cx, cy = _grid(centre, theta, CONTEXT_ALONG, CONTEXT_ACROSS)
    fine = cv2.remap(
        maps.darkness, fx, fy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
    )
    context = cv2.remap(
        maps.context, cx, cy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
    )
    return np.concatenate((fine.ravel(), context.ravel()))


class TipDetector:
    def __init__(
        self,
        config: TipDetectorConfig | None = None,
        model: PatchModel | str | Path | None = None,
    ):
        self.config = config or TipDetectorConfig()
        if model is None or isinstance(model, str | Path):
            model = PatchModel.load(model or MODEL_PATH)
        self.model = model
        c = self.config
        self.thetas = np.arange(c.orientations) * 2 * np.pi / c.orientations
        self._templates = []
        for theta in self.thetas:
            template, support = _wedge(
                theta,
                np.radians(c.wedge_half_angle_deg),
                c.wedge_length_px * c.coarse_scale,
                c.template_size,
                c.wedge_apex_width_px * c.coarse_scale,
            )
            self._templates.append(
                (
                    template,
                    support,
                    float(support.sum()),
                    float(np.linalg.norm(template)),
                )
            )

    # -- stage 1 and 2 ------------------------------------------------------------

    def wedge_scores(self, darkness: np.ndarray) -> np.ndarray:
        """(orientations, h, w) wedge scores on the coarse grid."""
        c = self.config
        small = cv2.resize(
            darkness,
            None,
            fx=c.coarse_scale,
            fy=c.coarse_scale,
            interpolation=cv2.INTER_AREA,
        )
        squared = small * small
        out = np.empty((len(self.thetas), *small.shape), np.float32)
        border = cv2.BORDER_REPLICATE
        for k, (template, support, count, norm) in enumerate(self._templates):
            corr = cv2.filter2D(small, -1, template, borderType=border)
            s1 = cv2.filter2D(small, -1, support, borderType=border)
            s2 = cv2.filter2D(squared, -1, support, borderType=border)
            spread = np.sqrt(np.maximum(s2 - s1 * s1 / count, 1e-4))
            contrast = 2 * corr / (norm * norm)
            out[k] = corr / (norm * spread) * np.clip(contrast / c.full_contrast, 0, 1)
        return out

    def prepare(self, gray: np.ndarray, search: bool = True) -> FrameMaps:
        darkness = darkness_map(gray)
        maps = FrameMaps(darkness, cv2.GaussianBlur(darkness, (0, 0), 1.5))
        if search:
            scores = self.wedge_scores(darkness)
            maps.wedge_scores = scores
            maps.candidates = self._peaks(scores)
        return maps

    def _peaks(self, scores):
        c = self.config
        best, arg = scores.max(0), scores.argmax(0)
        peaks = (best == cv2.dilate(best, np.ones((3, 3), np.uint8))) & (
            best > c.min_candidate_score
        )
        ys, xs = np.nonzero(peaks)
        found = []
        for j in np.argsort(-best[ys, xs]):
            x, y = xs[j], ys[j]
            p = ((x + 0.5) / c.coarse_scale - 0.5, (y + 0.5) / c.coarse_scale - 0.5)
            if any(
                np.hypot(p[0] - q[0], p[1] - q[1]) < c.candidate_separation_px
                for q, _, _ in found
            ):
                continue
            found.append((p, float(self.thetas[arg[y, x]]), float(best[y, x])))
            if len(found) >= c.max_candidates:
                break
        return found

    # -- stage 3 ---------------------------------------------------------------

    def refine(self, maps: FrameMaps, centre, theta) -> tuple[np.ndarray, float]:
        """Follow the regressed offsets from ``centre``; (tip, logit)."""
        start = np.asarray(centre, float)
        point = start.copy()
        u, n = _axis(theta)
        h, w = maps.darkness.shape
        for _ in range(self.config.refine_iterations):
            out = self.model.forward(patch_features(maps, point, theta)[None])[0]
            point = point + OFFSET_UNIT_PX * (out[1] * u + out[2] * n)
            step = point - start
            if np.hypot(*step) > self.config.max_step_px:
                point = start + step * self.config.max_step_px / np.hypot(*step)
            point = np.clip(point, (-2, -2), (w + 1, h + 1))
        logit = float(
            self.model.forward(patch_features(maps, point, theta)[None])[0, 0]
        )
        return point, logit

    def detect(
        self,
        gray: np.ndarray,
        hints=(),
        *,
        search: bool = True,
        maps: FrameMaps | None = None,
        region=None,
    ) -> TipDetection:
        """Best tip in ``gray``; ``hints`` are extra (x, y, theta) start points.

        ``region(x, y) -> bool`` (frame pixels) rejects tips outside an area,
        e.g. off the page.
        """
        maps = maps or self.prepare(gray, search)
        starts = [((x, y), theta) for x, y, theta in hints]
        starts += [(p, theta) for p, theta, _ in maps.candidates]
        best, best_theta, best_logit = None, 0.0, -np.inf
        for p, theta in starts:
            point, logit = self.refine(maps, p, theta)
            if region is not None and not region(point[0], point[1]):
                continue
            if logit > best_logit:
                best, best_theta, best_logit = point, theta, logit
        if best is None:
            return NOT_FOUND
        offset = self.config.tip_offset_px
        if offset is None:
            offset = float(self.model.metadata.get("tip_offset_px", 0.0))
        best = best + offset * _axis(best_theta)[0]
        return TipDetection(
            best_logit > self.config.threshold,
            float(best[0]),
            float(best[1]),
            float(best_theta),
            best_logit,
            len(starts),
        )
