"""Stroke post-processing (Task 11): dedupe, snap to ink, smooth, resample.

The tip trail gives order and timing; the ink on the paper gives the final
shape. ``snap_to_ink`` moves each point across the stroke (along the local
normal) onto the centre of the new ink found within ``reach_mm``, so tip
noise across the line is removed but the along-stroke timing stays.
"""

from __future__ import annotations

import cv2
import numpy as np

from digital_pen.strokes.canvas import PaperCanvas
from digital_pen.strokes.segment import Stroke


def dedupe(stroke: Stroke, min_step_mm: float = 0.1) -> Stroke:
    if len(stroke.mm) < 2:
        return stroke
    keep = [0]
    for k in range(1, len(stroke.mm)):
        if np.hypot(*(stroke.mm[k] - stroke.mm[keep[-1]])) >= min_step_mm:
            keep.append(k)
    keep = np.array(keep)
    return Stroke(
        stroke.t[keep],
        stroke.mm[keep],
        stroke.evidence[keep] if len(stroke.evidence) else stroke.evidence,
    )


def _normals(mm: np.ndarray) -> np.ndarray:
    d = np.gradient(mm, axis=0) if len(mm) > 1 else np.array([[1.0, 0.0]])
    d /= np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)
    return np.column_stack((-d[:, 1], d[:, 0]))


def snap_to_ink(
    stroke: Stroke,
    ink: np.ndarray,
    canvas: PaperCanvas,
    reach_mm: float = 1.0,
    floor: float = 0.04,
    min_mass: float = 0.15,
) -> Stroke:
    """Shift points across the stroke onto the centre of the new ink.

    ``ink`` is ``canvas.new_ink()`` (darkness added since first seen).
    """
    if len(stroke.mm) < 2:
        return stroke
    normals = _normals(stroke.mm)
    offsets = np.arange(-reach_mm, reach_mm + 1e-9, canvas.config.mm_per_px / 2)
    pts = stroke.mm[:, None, :] + offsets[None, :, None] * normals[:, None, :]
    px = canvas.to_px(pts.reshape(-1, 2)).astype(np.float32)
    values = cv2.remap(
        ink, px[:, 0].reshape(-1, 1), px[:, 1].reshape(-1, 1), cv2.INTER_LINEAR
    ).reshape(len(stroke.mm), len(offsets))
    weights = np.maximum(values - floor, 0)
    mass = weights.sum(1) * (offsets[1] - offsets[0])
    shift = (weights * offsets).sum(1) / np.maximum(weights.sum(1), 1e-9)
    shift[mass < min_mass] = 0.0
    return Stroke(stroke.t, stroke.mm + shift[:, None] * normals, stroke.evidence)


def smooth(stroke: Stroke, window: int = 3) -> Stroke:
    if len(stroke.mm) < window or window < 2:
        return stroke
    kernel = np.ones(window) / window
    pad = window // 2
    padded = np.pad(stroke.mm, ((pad, pad), (0, 0)), mode="edge")
    out = np.column_stack(
        [np.convolve(padded[:, j], kernel, mode="valid") for j in range(2)]
    )
    out[0], out[-1] = stroke.mm[0], stroke.mm[-1]
    return Stroke(stroke.t, out, stroke.evidence)


def resample(stroke: Stroke, step_mm: float = 0.5) -> Stroke:
    """Points every ``step_mm`` of arc length (times interpolated)."""
    if len(stroke.mm) < 2:
        return stroke
    seg = np.linalg.norm(np.diff(stroke.mm, axis=0), axis=1)
    s = np.concatenate(([0.0], np.cumsum(seg)))
    if s[-1] < step_mm:
        return Stroke(stroke.t[[0, -1]], stroke.mm[[0, -1]])
    grid = np.append(np.arange(0.0, s[-1], step_mm), s[-1])
    mm = np.column_stack([np.interp(grid, s, stroke.mm[:, j]) for j in range(2)])
    return Stroke(np.interp(grid, s, stroke.t), mm)


def split_on_ink(
    stroke: Stroke,
    ink: np.ndarray,
    canvas: PaperCanvas,
    radius_mm: float = 0.75,
    threshold: float = 0.03,
    gap_mm: float = 3.0,
    min_mm: float = 0.8,
) -> list[Stroke]:
    """Cut a finished stroke where it runs over paper without new ink.

    A point is off the ink when no pixel within ``radius_mm`` gained
    ``threshold`` of darkness and the paper there has been seen uncovered
    after the tip passed (otherwise the canvas may still show the paper from
    before the writing, e.g. under the hand, so it cannot tell and the point
    is kept). Runs of off-ink points spanning at
    least ``gap_mm`` are pen-up lines the segmentation missed: they are
    removed, and pieces shorter than ``min_mm`` are dropped. The page view
    then only draws where there is ink (Task 13).

    The defaults are deliberately cautious (wide window, faint threshold,
    long gaps): right after the page is located again the strokes can sit
    about 1 mm beside their ink, and cutting there would delete real writing.
    """
    if len(stroke.mm) < 2:
        return [stroke]
    r = max(1, int(round(radius_mm / canvas.config.mm_per_px)))
    near = cv2.dilate(
        ink, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1,) * 2)
    )
    px = np.rint(canvas.to_px(stroke.mm)).astype(int)
    inside = (
        (px[:, 0] >= 0)
        & (px[:, 0] < canvas.shape[1])
        & (px[:, 1] >= 0)
        & (px[:, 1] < canvas.shape[0])
    )
    off = np.zeros(len(px), bool)
    col, row = px[inside, 0], px[inside, 1]
    seen = canvas.stamp[row, col] > stroke.t[inside]
    off[np.flatnonzero(inside)] = seen & (near[row, col] < threshold)
    if not off.any():
        return [stroke]
    seg = np.linalg.norm(np.diff(stroke.mm, axis=0), axis=1)
    s = np.concatenate(([0.0], np.cumsum(seg)))
    keep = np.ones(len(px), bool)
    edges = np.flatnonzero(np.diff(np.concatenate(([0], off.astype(int), [0]))))
    for a, b in zip(edges[0::2], edges[1::2], strict=True):
        # Points a..b-1 are off the ink; the span runs from the last point
        # on ink before them to the first one after.
        lo, hi = max(a - 1, 0), min(b, len(px) - 1)
        if s[hi] - s[lo] >= gap_mm:
            keep[a:b] = False
    pieces, out = (
        np.flatnonzero(np.diff(np.concatenate(([0], keep.astype(int), [0])))),
        [],
    )
    for a, b in zip(pieces[0::2], pieces[1::2], strict=True):
        if b - a >= 2 and s[b - 1] - s[a] >= min_mm:
            out.append(Stroke(stroke.t[a:b], stroke.mm[a:b]))
    return out


def finish(
    stroke: Stroke,
    canvas: PaperCanvas | None = None,
    ink: np.ndarray | None = None,
    step_mm: float = 0.5,
) -> Stroke:
    """Dedupe, snap to ink (if a canvas is given), resample, smooth.

    Smoothing comes after resampling: before it, consecutive points can be
    millimetres apart (hidden tip frames) and averaging would cut corners.
    """
    stroke = dedupe(stroke)
    if canvas is not None:
        stroke = snap_to_ink(stroke, canvas.new_ink() if ink is None else ink, canvas)
    return smooth(resample(stroke, step_mm))
