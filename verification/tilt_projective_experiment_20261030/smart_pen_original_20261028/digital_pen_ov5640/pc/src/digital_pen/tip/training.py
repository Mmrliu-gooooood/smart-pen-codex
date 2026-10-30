"""Training of the tip patch model from labeled frames (NumPy only).

Samples are rotation-normalised patches (see ``detector.patch_features``):

- around each labeled tip: centres scattered along and across the pen axis
  (direction = best wedge orientation at the label, jittered), with the
  offset to the tip as regression target and "tip" as class when the centre
  is within ``positive_radius_px``;
- the same tip seen in a wrong direction (reversed, sideways) as negatives;
- the wedge candidates of every frame (negatives in frames without a tip,
  labeled by distance in frames with one);
- augmented copies of each frame (rotation, mirror, sensor noise);
- a second round adds hard negatives: refined candidates that scored as a
  tip but lie away from the label.

The network is a ReLU MLP trained with Adam on a logistic loss plus a Huber
loss on the offsets.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from digital_pen.tip.detector import (
    FEATURES,
    OFFSET_UNIT_PX,
    PatchModel,
    TipDetector,
    patch_features,
)


@dataclass(frozen=True)
class TrainingConfig:
    hidden: tuple[int, ...] = (128, 48)
    epochs: int = 25
    batch: int = 256
    learning_rate: float = 2e-3
    weight_decay: float = 1e-4
    offset_weight: float = 0.5
    positive_radius_px: float = 3.0
    augmented_copies: int = 2
    samples_per_tip: int = 20
    angle_jitter_deg: float = 8.0
    hard_threshold: float = -1.0
    hard_min_distance_px: float = 6.0
    seed: int = 0


@dataclass
class LabeledFrame:
    """One labeled frame: ``tip`` is the (x, y) tip in frame pixels or None."""

    image: np.ndarray
    tip: tuple[float, float] | None
    key: object = None


def label_direction(detector: TipDetector, scores: np.ndarray, x: float, y: float):
    """Pen direction at a labeled tip: best wedge orientation, interpolated."""
    scale = detector.config.coarse_scale
    h, w = scores.shape[1:]
    xi = int(np.clip(round((x + 0.5) * scale - 0.5), 0, w - 1))
    yi = int(np.clip(round((y + 0.5) * scale - 0.5), 0, h - 1))
    window = scores[:, max(0, yi - 1) : yi + 2, max(0, xi - 1) : xi + 2].max(
        axis=(1, 2)
    )
    k = int(np.argmax(window))
    n = len(window)
    a, b, c = window[(k - 1) % n], window[k], window[(k + 1) % n]
    curvature = a - 2 * b + c
    delta = 0.5 * (a - c) / curvature if curvature < 0 else 0.0
    return float(detector.thetas[k] + delta * 2 * np.pi / n)


def augment(image, tip, rng):
    """Random rotation about the centre, mirror and sensor noise."""
    h, w = image.shape
    matrix = cv2.getRotationMatrix2D(((w - 1) / 2, (h - 1) / 2), rng.uniform(0, 360), 1)
    out = cv2.warpAffine(
        image, matrix, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT
    )
    moved = None if tip is None else matrix @ np.array((tip[0], tip[1], 1.0))
    if rng.random() < 0.5:
        out = out[:, ::-1].copy()
        if moved is not None:
            moved = np.array((w - 1 - moved[0], moved[1]))
    if rng.random() < 0.5:
        noise = rng.normal(0, rng.uniform(0, 5), out.shape)
        out = np.clip(out + noise, 0, 255).astype(np.uint8)
    return out, moved


class _Samples:
    def __init__(self, radius):
        self.radius = radius
        self.x, self.cls, self.offset, self.mask = [], [], [], []

    def add(self, maps, centre, theta, tip):
        centre = np.asarray(centre, float)
        self.x.append(patch_features(maps, centre, theta))
        if tip is None:
            self.cls.append(0.0)
            self.offset.append((0.0, 0.0))
            self.mask.append(0.0)
            return
        u = np.array((np.cos(theta), np.sin(theta)))
        n = np.array((-u[1], u[0]))
        d = np.asarray(tip, float) - centre
        along, across = float(d @ u), float(d @ n)
        self.cls.append(1.0 if np.hypot(along, across) <= self.radius else 0.0)
        self.offset.append(
            (
                np.clip(along, -20, 20) / OFFSET_UNIT_PX,
                np.clip(across, -8, 8) / OFFSET_UNIT_PX,
            )
        )
        self.mask.append(1.0 if abs(along) <= 20 and abs(across) <= 8 else 0.0)

    def arrays(self):
        return (
            np.asarray(self.x, np.float32).reshape(-1, FEATURES),
            np.asarray(self.cls, np.float32),
            np.asarray(self.offset, np.float32).reshape(-1, 2),
            np.asarray(self.mask, np.float32),
        )


def build_samples(
    detector: TipDetector,
    frames: list[LabeledFrame],
    config: TrainingConfig,
    *,
    seed: int,
    copies: int | None = None,
    per_tip: int | None = None,
    hard: dict | None = None,
):
    rng = np.random.default_rng(seed)
    out = _Samples(config.positive_radius_px)
    copies = config.augmented_copies if copies is None else copies
    per_tip = config.samples_per_tip if per_tip is None else per_tip
    jitter = np.radians(config.angle_jitter_deg)
    for index, frame in enumerate(frames):
        for copy in range(copies + 1):
            if copy == 0:
                image, tip = frame.image, frame.tip
            else:
                image, tip = augment(frame.image, frame.tip, rng)
            h, w = image.shape
            if tip is not None and not (0 <= tip[0] < w and 0 <= tip[1] < h):
                continue
            maps = detector.prepare(image)
            if tip is not None:
                tip = np.asarray(tip, float)
                direction = label_direction(detector, maps.wedge_scores, *tip)
                for _ in range(per_tip):
                    theta = direction + rng.normal(0, jitter)
                    u = np.array((np.cos(theta), np.sin(theta)))
                    n = np.array((-u[1], u[0]))
                    if rng.random() < 0.35:
                        along, across = rng.normal(0, 1.5, 2)
                    else:
                        along, across = rng.uniform(-10, 18), rng.uniform(-6, 6)
                    out.add(maps, tip + along * u + across * n, theta, tip)
                for turn in (np.pi, np.pi / 2, -np.pi / 2):
                    out.add(maps, tip, direction + turn + rng.normal(0, 0.2), None)
                for p, theta, _ in maps.candidates:
                    out.add(maps, p, theta, tip)
            else:
                for p, theta, _ in maps.candidates:
                    out.add(maps, p, theta, None)
                for _ in range(3):
                    out.add(
                        maps, rng.uniform(0, (w, h)), rng.uniform(0, 2 * np.pi), None
                    )
            if copy == 0 and hard:
                for p, theta in hard.get(index, ()):
                    out.add(maps, p, theta, tip)
    return out.arrays()


def mine_hard(
    detector: TipDetector, frames: list[LabeledFrame], config: TrainingConfig
):
    """Refined candidates scoring as a tip away from the label, per frame index."""
    hard = {}
    for index, frame in enumerate(frames):
        maps = detector.prepare(frame.image)
        for p, theta, _ in maps.candidates:
            point, logit = detector.refine(maps, p, theta)
            far = frame.tip is None or (
                np.hypot(*(point - np.asarray(frame.tip))) > config.hard_min_distance_px
            )
            if logit > config.hard_threshold and far:
                hard.setdefault(index, []).append((tuple(point), theta))
    return hard


def fit_mlp(x, cls, offset, mask, config: TrainingConfig, seed: int) -> PatchModel:
    """Adam on logistic + masked Huber loss; returns a PatchModel."""
    rng = np.random.default_rng(seed)
    sizes = [x.shape[1], *config.hidden, 3]
    weights = [
        rng.normal(0, np.sqrt(2 / a), (a, b)).astype(np.float32)
        for a, b in zip(sizes[:-1], sizes[1:], strict=True)
    ]
    biases = [np.zeros(b, np.float32) for b in sizes[1:]]
    mean = x.mean(0)
    scale = x.std(0) + 1e-3
    z = (x - mean) / scale
    params = weights + biases
    m1 = [np.zeros_like(p) for p in params]
    m2 = [np.zeros_like(p) for p in params]
    step = 0
    for epoch in range(config.epochs):
        rate = config.learning_rate * 0.5 * (1 + np.cos(np.pi * epoch / config.epochs))
        order = rng.permutation(len(z))
        for start in range(0, len(z), config.batch):
            j = order[start : start + config.batch]
            acts = [z[j]]
            h = acts[0]
            for i, (w, b) in enumerate(zip(weights, biases, strict=True)):
                h = h @ w + b
                if i < len(weights) - 1:
                    h = np.maximum(h, 0)
                acts.append(h)
            p = 1 / (1 + np.exp(-np.clip(h[:, 0], -30, 30)))
            grad = np.zeros_like(h)
            grad[:, 0] = (p - cls[j]) / len(j)
            residual = np.clip(h[:, 1:3] - offset[j], -1, 1)
            grad[:, 1:3] = (
                config.offset_weight
                * residual
                * mask[j][:, None]
                / max(1.0, mask[j].sum())
            )
            grads_w, grads_b = [None] * len(weights), [None] * len(biases)
            for i in range(len(weights) - 1, -1, -1):
                grads_w[i] = acts[i].T @ grad + config.weight_decay * weights[i]
                grads_b[i] = grad.sum(0)
                if i:
                    grad = (grad @ weights[i].T) * (acts[i] > 0)
            step += 1
            for k, (param, g) in enumerate(zip(params, grads_w + grads_b, strict=True)):
                m1[k] = 0.9 * m1[k] + 0.1 * g
                m2[k] = 0.999 * m2[k] + 0.001 * g * g
                param -= (
                    rate
                    * (m1[k] / (1 - 0.9**step))
                    / (np.sqrt(m2[k] / (1 - 0.999**step)) + 1e-8)
                )
    return PatchModel(weights, biases, mean, scale)


def train_model(
    frames: list[LabeledFrame],
    config: TrainingConfig | None = None,
    detector_config=None,
) -> tuple[PatchModel, dict]:
    """Two rounds (plain, then with hard negatives); returns model and stats."""
    config = config or TrainingConfig()
    detector = TipDetector(detector_config, model=_placeholder_model(config))
    x, cls, offset, mask = build_samples(detector, frames, config, seed=config.seed)
    model = fit_mlp(x, cls, offset, mask, config, config.seed)
    detector.model = model
    hard = mine_hard(detector, frames, config)
    extra = build_samples(
        detector, frames, config, seed=config.seed + 100, copies=0, per_tip=4, hard=hard
    )
    x, cls, offset, mask = (
        np.concatenate(pair) for pair in zip((x, cls, offset, mask), extra, strict=True)
    )
    model = fit_mlp(x, cls, offset, mask, config, config.seed)
    stats = {
        "samples": int(len(x)),
        "positives": int(cls.sum()),
        "hard_negatives": int(sum(len(v) for v in hard.values())),
        "frames": len(frames),
        "tip_frames": sum(f.tip is not None for f in frames),
    }
    return model, stats


def _placeholder_model(config: TrainingConfig) -> PatchModel:
    """An untrained model so a detector can be built before training."""
    sizes = [FEATURES, *config.hidden, 3]
    return PatchModel(
        [
            np.zeros((a, b), np.float32)
            for a, b in zip(sizes[:-1], sizes[1:], strict=True)
        ],
        [np.zeros(b, np.float32) for b in sizes[1:]],
        np.zeros(FEATURES, np.float32),
        np.ones(FEATURES, np.float32),
    )
