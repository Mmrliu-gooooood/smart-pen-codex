"""Offline draw-and-guess (Task 18): a small CNN trained on Quick, Draw!
28x28 bitmaps (345 classes, CC BY 4.0), run with numpy only.

The pen strokes are drawn like the dataset's bitmaps: the drawing's longer
side fills 26 of the 28 pixels, centred, white lines about 2 px wide on
black. Training: artifacts/quickdraw-2026-10/train.py (PyTorch, separate
environment); the weights ship as model.npz next to this file."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np

from digital_pen.guess.labels import ZH

MODEL = Path(__file__).with_name("model.npz")
CANVAS = 256
FILL = CANVAS * 26 / 28  # the longer side, as in the dataset
LINE_PX = 18  # at 256 px: ~2 px at 28


def render(polylines: list[np.ndarray]) -> np.ndarray:
    """28x28 uint8, white strokes on black, from polylines in mm (y up)."""
    lines = [np.asarray(p, float).reshape(-1, 2) for p in polylines if len(p)]
    image = np.zeros((CANVAS, CANVAS), np.uint8)
    if not lines:
        return cv2.resize(image, (28, 28), interpolation=cv2.INTER_AREA)
    pts = np.concatenate(lines)
    lo, hi = pts.min(0), pts.max(0)
    scale = FILL / max(float(max(hi - lo)), 1e-6)
    centre = (lo + hi) / 2
    for p in lines:
        q = np.column_stack(
            (
                CANVAS / 2 + (p[:, 0] - centre[0]) * scale,
                CANVAS / 2 - (p[:, 1] - centre[1]) * scale,  # y up -> rows down
            )
        )
        q = np.rint(q * 16).astype(np.int32)
        if len(q) == 1:
            q = np.vstack([q, q])
        cv2.polylines(image, [q], False, 255, LINE_PX, cv2.LINE_AA, shift=4)
    return cv2.resize(image, (28, 28), interpolation=cv2.INTER_AREA)


def _conv(x: np.ndarray, w: np.ndarray, b: np.ndarray) -> np.ndarray:
    """3x3 convolution, padding 1, ReLU. x (C, H, W), w (O, C, 3, 3)."""
    c, h, wd = x.shape
    padded = np.pad(x, ((0, 0), (1, 1), (1, 1)))
    windows = np.lib.stride_tricks.sliding_window_view(padded, (3, 3), axis=(1, 2))
    cols = windows.transpose(1, 2, 0, 3, 4).reshape(h * wd, c * 9)
    out = cols @ w.reshape(len(w), -1).T + b
    return np.maximum(out, 0).T.reshape(len(w), h, wd)


def _pool(x: np.ndarray) -> np.ndarray:
    c, h, w = x.shape
    return x.reshape(c, h // 2, 2, w // 2, 2).max(axis=(2, 4))


class Classifier:
    """``guess(polylines)`` -> top-k ``{"key", "label", "p"}``."""

    def __init__(self, path: Path = MODEL):
        data = np.load(path, allow_pickle=False)
        self.w = {k: data[k].astype(np.float32) for k in data.files if k != "classes"}
        self.classes = [str(c) for c in data["classes"]]

    def probabilities(self, bitmap: np.ndarray) -> np.ndarray:
        w = self.w
        x = bitmap.astype(np.float32)[None] / 255.0
        x = _conv(x, w["c1.weight"], w["c1.bias"])
        x = _pool(_conv(x, w["c2.weight"], w["c2.bias"]))
        x = _conv(x, w["c3.weight"], w["c3.bias"])
        x = _pool(_conv(x, w["c4.weight"], w["c4.bias"]))
        x = np.maximum(w["f1.weight"] @ x.reshape(-1) + w["f1.bias"], 0)
        z = w["f2.weight"] @ x + w["f2.bias"]
        e = np.exp(z - z.max())
        return e / e.sum()

    def guess(self, polylines: list[np.ndarray], k: int = 3) -> list[dict]:
        p = self.probabilities(render(polylines))
        top = np.argsort(p)[::-1][:k]
        return [
            {
                "key": self.classes[i],
                "label": ZH.get(self.classes[i], self.classes[i]),
                "p": round(float(p[i]), 3),
            }
            for i in top
        ]


@lru_cache(maxsize=1)
def default() -> Classifier | None:
    """The shipped model, or None when it is missing (guessing is optional)."""
    return Classifier() if MODEL.exists() else None
