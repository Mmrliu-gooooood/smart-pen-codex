"""Ink evidence at tip points (Task 11).

For every tip position the pen visits, compare the paper darkness there just
before the tip arrived with the darkness after it has left, pixel by pixel
over a small window: evidence = largest darkening. New ink makes it darker;
a hovering pen leaves nothing. Printed dots and older ink are in both views,
so they cancel exactly (a per-window maximum before vs after would let a dot
hide fresh ink beside it).

Shadows: the hand casts a soft shadow that moves with it. The canvas
therefore stores ``ink_darkness`` (brightness relative to the local paper
level, which a slow shadow shares), and the "after" view of a point is the
lightest reading per pixel over ``min_views`` uncovered views: ink stays,
a passing shadow does not.

A point already sitting on ink written earlier in the session (``old_ink``)
cannot show new ink on top of it: a crossing looks like "no ink" there. The
segmenter treats such points as undecided rather than as pen-up.

The camera only sees the paper where the pen, the hand and their shadows do
not cover it (``cover_mask``): wide dark regions (pen body, fingers) survive
a morphological opening that removes thin ink lines and dots, the cone of the
pen behind the tip is masked from the detected tip and direction, and so is a
disk around the tip. A point's "after" view is taken once the tip is
``leave_mm`` away and most of the probe window was seen uncovered since.
Points still covered after ``max_wait_s`` (e.g. a stroke drawn towards the
hand, which stays under the pen) are given up as unknown; the segmenter
fills them from their neighbours.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from digital_pen.strokes.canvas import PaperCanvas


@dataclass(frozen=True)
class InkConfig:
    open_px: int = 9
    wide_dark: float = 0.12
    dilate_px: int = 4
    tip_radius_px: float = 5.0
    cone_length_px: float = 70.0
    cone_half_width_px: float = 12.0
    probe_radius_mm: float = 0.6
    settle_s: float = 0.03
    leave_mm: float = 1.5
    max_wait_s: float = 1.5
    min_views: int = 3
    min_delay_s: float = 0.25
    shadow_sigma_px: float = 6.0


def cover_mask(
    darkness: np.ndarray,
    tip=None,
    theta: float | None = None,
    config: InkConfig | None = None,
) -> np.ndarray:
    """True where pen, hand or shadow may cover the paper (frame pixels)."""
    c = config or InkConfig()
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (c.open_px, c.open_px))
    wide = cv2.morphologyEx(darkness, cv2.MORPH_OPEN, kernel) > c.wide_dark
    mask = wide.astype(np.uint8)
    if tip is not None and np.all(np.isfinite(tip)):
        x, y = float(tip[0]), float(tip[1])
        cv2.circle(
            mask, (int(round(x)), int(round(y))), int(round(c.tip_radius_px)), 1, -1
        )
        if theta is not None and np.isfinite(theta):
            u = np.array((np.cos(theta), np.sin(theta)))
            n = np.array((-u[1], u[0]))
            tip_pt = np.array((x, y))
            back = tip_pt - c.cone_length_px * u
            cone = np.array(
                (
                    tip_pt + 2.0 * u + 2.5 * n,
                    tip_pt + 2.0 * u - 2.5 * n,
                    back - c.cone_half_width_px * n,
                    back + c.cone_half_width_px * n,
                )
            )
            cv2.fillConvexPoly(mask, np.rint(cone).astype(np.int32), 1)
    if c.dilate_px > 0:
        size = 2 * c.dilate_px + 1
        mask = cv2.dilate(mask, np.ones((size, size), np.uint8))
    return mask.astype(bool)


def ink_darkness(gray: np.ndarray, sigma_px: float = 6.0) -> np.ndarray:
    """Darkness relative to the local paper level (shadow-free), float32.

    The paper level is a closing (removes dots and ink) blurred over
    ``sigma_px``; soft shadows darken it as much as the paper, thin ink does
    not.
    """
    closed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    level = cv2.GaussianBlur(closed.astype(np.float32), (0, 0), sigma_px)
    smooth = cv2.GaussianBlur(gray, (0, 0), 1.0).astype(np.float32)
    return np.clip((level - smooth) / np.maximum(level, 1.0), 0.0, 1.0)


@dataclass
class TrailPoint:
    t: float
    mm: tuple[float, float]
    before: float  # darkness peak just before the tip arrived
    after: float | None = None  # largest pixel darkening once it left
    expired: bool = False
    old_ink: bool = False  # on ink written earlier in the session
    before_patch: np.ndarray | None = None
    after_patch: np.ndarray | None = None  # lightest uncovered view so far
    views: int = 0
    last_view: float = -np.inf

    @property
    def evidence(self) -> float:
        """Largest darkening after the tip left (nan while unknown)."""
        if self.after is None or not np.isfinite(self.after):
            return float("nan")
        return float(self.after)

    @property
    def resolved(self) -> bool:
        return self.after is not None or self.expired


class InkWatcher:
    """Pending tip points waiting for their "after" view."""

    def __init__(self, canvas: PaperCanvas, config: InkConfig | None = None):
        self.canvas = canvas
        self.config = config or InkConfig()
        self.pending: list[TrailPoint] = []

    def add(self, t: float, mm) -> TrailPoint:
        """Register a tip point; call before the frame updates the canvas."""
        r = self.config.probe_radius_mm
        clean = self.canvas.patch(mm, r, "clean")
        first = self.canvas.patch(mm, r, "first")
        before, old_ink, patch = float("nan"), False, None
        if clean is not None:
            # Never seen uncovered: the first view is the best "before".
            patch = np.where(np.isnan(clean), first, clean)
            if not np.all(np.isnan(patch)):
                before = float(np.nanmax(patch))
                k = patch.shape[0] // 2
                centre = (patch - first)[k - 1 : k + 2, k - 1 : k + 2]
                old_ink = bool(
                    np.nanmax(np.nan_to_num(centre, nan=0.0))
                    > self.canvas.config.ink_threshold
                )
        point = TrailPoint(
            t, (float(mm[0]), float(mm[1])), before, old_ink=old_ink, before_patch=patch
        )
        self.pending.append(point)
        return point

    def _finish(self, point: TrailPoint) -> None:
        change = None
        if point.after_patch is not None and point.before_patch is not None:
            change = point.after_patch - point.before_patch
        if change is None or np.all(np.isnan(change)):
            point.after = float("nan")
        else:
            point.after = float(np.nanmax(change))
        point.before_patch = point.after_patch = None  # no longer needed

    def resolve(self, now: float, tip_mm=None) -> list[TrailPoint]:
        """Collect "after" views; returns the points resolved now."""
        c = self.config
        done, keep = [], []
        for point in self.pending:
            far = tip_mm is None or (
                np.hypot(point.mm[0] - tip_mm[0], point.mm[1] - tip_mm[1]) >= c.leave_mm
            )
            if far and self.canvas.seen_since(
                point.mm, max(point.t + c.settle_s, point.last_view), c.probe_radius_mm
            ):
                view = self.canvas.patch(point.mm, c.probe_radius_mm, "clean")
                if view is not None:
                    point.after_patch = (
                        view
                        if point.after_patch is None
                        else np.fmin(point.after_patch, view)
                    )
                    point.views += 1
                    point.last_view = now
            age = now - point.t
            if point.views >= c.min_views and age >= c.min_delay_s:
                self._finish(point)
                done.append(point)
            elif age > c.max_wait_s:
                if point.views:
                    self._finish(point)
                else:
                    point.expired = True
                    point.before_patch = point.after_patch = None
                done.append(point)
            else:
                keep.append(point)
        self.pending = keep
        return done

    def flush(self) -> list[TrailPoint]:
        """End of input: resolve with the views collected, or give up."""
        for point in self.pending:
            if point.views:
                self._finish(point)
            else:
                point.expired = True
                point.before_patch = point.after_patch = None
        done, self.pending = self.pending, []
        return done
