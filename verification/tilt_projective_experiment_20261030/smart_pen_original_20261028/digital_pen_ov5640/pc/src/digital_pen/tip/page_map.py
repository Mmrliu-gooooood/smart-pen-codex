"""Tip pixels -> page millimetres, with paper-movement checks (Task 10).

``locate_page`` gives a page->image model for one frame. The camera is fixed,
so the model stays valid until the paper moves. Each page snapshot of the
TRACK stream is checked against the current model:

1. Dots are detected on bright paper only (hand and pen are darker; their
   texture would otherwise produce spurious "dots", worst at high gain).
2. The share of those dots lying on printed positions predicted by the model
   is compared with the share measured when the page was located (noisy,
   high-gain frames never reach the share of clean ones).
3. A low share only raises a suspicion: the page is located again on the
   snapshot, and "moved" is reported only if the new model differs from the
   old one by more than ``moved_px`` over the visible paper. Otherwise the
   old model is kept.

Snapshots are crops of the sensor frame; ``origin`` is the crop's top-left in
sensor pixels, and every position here is in sensor pixels.

``page_mask`` gives the printed page area (plus a small margin) in sensor
pixels: tips are only accepted there, so dark corners of objects beside the
sheet are never taken for a pen. The margin is kept small (1.5 mm) because
the sheet ends only a few mm beyond the print: in the first live run the
background at a sheet corner, 3.2 mm outside the print, held a false track.
The model, its origin and its baseline are replaced as one
tuple, so a check running in a worker thread never exposes a half-updated
state to readers.

``track`` follows small paper slips between snapshot checks: the hand pushes
the paper while writing, often by a few tenths of a millimetre at a time.
The printed dots seen in each ROI frame are matched to where the current
model predicts them, and the median offset shifts the model's origin (a pure
translation; anything larger is left to the next snapshot check).
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, replace

import cv2
import numpy as np

from digital_pen.anoto import AnotoDecodeError
from digital_pen.pose import (
    PageLayout,
    PageLocation,
    PageLocatorConfig,
    detect_dots_fast,
    locate_page,
)


@dataclass(frozen=True)
class PageCheck:
    status: str  # "same" | "moved" | "pending" | "unknown"
    matched: float  # share of paper dots on predicted printed positions
    dots: int  # dots detected on paper
    relocated: bool = False  # the model was replaced
    shift_px: float | None = None  # model change when a move was suspected
    error: str = ""


class PageMapper:
    def __init__(
        self,
        layout: PageLayout,
        config: PageLocatorConfig | None = None,
        *,
        match_radius_ratio: float = 0.25,
        suspect_ratio: float = 0.7,
        min_dots: int = 150,
        moved_px: float = 1.0,
        confirm_jump_px: float | None = 12.0,
    ):
        self.layout = layout
        self.config = config or PageLocatorConfig()
        self.match_radius_ratio = match_radius_ratio
        self.suspect_ratio = suspect_ratio
        self.min_dots = min_dots
        self.moved_px = moved_px
        # Consistency check: a relocation that jumps more than this is only
        # accepted once a second snapshot gives the same new pose (a wrong
        # decode on one snapshot must not move every stroke). None: off.
        self.confirm_jump_px = confirm_jump_px
        self._candidate = None  # (location, origin) waiting for confirmation
        # (location, origin, baseline), replaced as a whole.
        self._state: tuple[PageLocation | None, np.ndarray, float] = (
            None,
            np.zeros(2),
            1.0,
        )
        self.relocations = 0
        self._mask_key = None
        self._mask = None
        self._lock = threading.Lock()
        self._printed = None
        self.slip_px = np.zeros(2)  # translation followed since the last locate

    @property
    def location(self) -> PageLocation | None:
        return self._state[0]

    @property
    def origin(self) -> np.ndarray:
        return self._state[1]

    @property
    def baseline(self) -> float:
        return self._state[2]

    def locate(
        self, gray: np.ndarray, origin=(0, 0), seed_hint_px=None
    ) -> PageLocation:
        """Locate the page in ``gray`` (a frame or crop); raises AnotoDecodeError."""
        hint = None
        if seed_hint_px is not None:
            hint = tuple(np.asarray(seed_hint_px, float) - np.asarray(origin, float))
        location = locate_page(gray, self.layout, self.config, seed_hint_px=hint)
        origin = np.asarray(origin, float)
        share = self._share(gray, origin, (location, origin))
        with self._lock:
            self._state = (location, origin, share[0] if share is not None else 1.0)
            self.slip_px = np.zeros(2)
            self.relocations += 1
        return location

    def track(
        self,
        gray: np.ndarray,
        frame_origin=(0, 0),
        max_step_px: float = 2.5,
        min_matches: int = 25,
    ) -> np.ndarray | None:
        """Follow a small paper slip from the dots in one frame.

        ``frame_origin`` is the frame's top-left in sensor pixels. Returns the
        correction applied (sensor px) or None when the frame cannot tell
        (too few dots on uncovered paper, or no consistent offset).
        """
        location, origin, _ = self._state
        if location is None:
            return None
        h, w = gray.shape
        dots = detect_dots_fast(gray, self.config)
        if len(dots) < min_matches:
            return None
        paper = paper_mask(gray)
        dots = dots[paper[_rows(dots, h), _cols(dots, w)] > 0]
        if len(dots) < min_matches:
            return None
        if self._printed is None:
            self._printed = self.layout.printed_positions()[1]
        frame_origin = np.asarray(frame_origin, float)
        corners = np.array(((0, 0), (w, 0), (0, h), (w, h)), float)
        page = location.pixel_to_page(corners + frame_origin - origin)
        lo, hi = page.min(0) - 1.0, page.max(0) + 1.0
        near = self._printed[
            np.all((self._printed >= lo) & (self._printed <= hi), axis=1)
        ]
        if len(near) < min_matches:
            return None
        predicted = location.page_to_pixel(near) + origin - frame_origin
        diff = dots[:, None, :] - predicted[None, :, :]
        dist = np.linalg.norm(diff, axis=2)
        nearest = dist.argmin(1)
        ok = dist[np.arange(len(dots)), nearest] < max_step_px
        if ok.sum() < min_matches:
            return None
        residual = diff[np.flatnonzero(ok), nearest[ok]]
        delta = np.median(residual, axis=0)
        spread = np.median(np.linalg.norm(residual - delta, axis=1))
        if spread > 0.8:
            return None
        with self._lock:
            if self._state[0] is not location:
                return None  # replaced meanwhile by a snapshot check
            current = self._state
            self._state = (current[0], current[1] + delta, current[2])
            self.slip_px = self.slip_px + delta
        return delta

    def to_page(self, xy) -> np.ndarray:
        """Sensor pixels -> page grid units (u right, v up)."""
        location, origin, _ = self._state
        if location is None:
            raise RuntimeError("page not located yet")
        return location.pixel_to_page(np.asarray(xy, float).reshape(-1, 2) - origin)

    def to_mm(self, xy) -> np.ndarray:
        return self.to_page(xy) * self.layout.spacing_mm

    def mm_per_px(self, xy) -> float:
        """Local scale at ``xy`` (mean of the two pixel axes)."""
        p = np.asarray(xy, float).reshape(2)
        base = self.to_mm(p)[0]
        steps = self.to_mm(np.array((p + (1, 0), p + (0, 1))))
        return float(np.mean(np.linalg.norm(steps - base, axis=1)))

    def page_mask(self, shape, margin_mm: float = 1.5) -> np.ndarray | None:
        """Bool mask (sensor pixels) of the page plus ``margin_mm``; cached."""
        location, origin, _ = self._state
        if location is None:
            return None
        # Slips change the origin by fractions of a pixel: not worth a redraw.
        key = (id(location), tuple(np.round(origin / 2)), tuple(shape), margin_mm)
        if key != self._mask_key:
            rows, cols = self.layout.shape
            m = margin_mm / self.layout.spacing_mm
            u = np.linspace(-m, cols - 1 + m, 40)
            v = np.linspace(-m, rows - 1 + m, 40)
            edge = np.concatenate(
                (
                    np.column_stack((u, np.full_like(u, -m))),
                    np.column_stack((np.full_like(v, cols - 1 + m), v)),
                    np.column_stack((u[::-1], np.full_like(u, rows - 1 + m))),
                    np.column_stack((np.full_like(v, -m), v[::-1])),
                )
            )
            polygon = location.page_to_pixel(edge) + origin
            mask = np.zeros(shape, np.uint8)
            cv2.fillPoly(mask, [np.rint(polygon).astype(np.int32)], 1)
            self._mask, self._mask_key = mask.astype(bool), key
        return self._mask

    def _printed_in(self, location, location_origin, origin):
        """All printed dot positions in the pixels of a crop at ``origin``."""
        _, printed = self.layout.printed_positions()
        return location.page_to_pixel(printed) + location_origin - np.asarray(origin)

    def _share(self, snapshot, origin, state=None):
        """(matched share, paper dots, paper mask), or None when undecidable."""
        location, location_origin = state or self._state[:2]
        paper = paper_mask(snapshot)
        h, w = snapshot.shape
        dots = detect_dots_fast(snapshot, self.config)
        dots = dots[paper[_rows(dots, h), _cols(dots, w)] > 0]
        predicted = self._printed_in(location, location_origin, origin)
        predicted = predicted[_inside(predicted, h, w)]
        if len(dots) < self.min_dots or len(predicted) < self.min_dots:
            return None
        radius = self.match_radius_ratio * location.model.spacing_px
        return _matched_share(predicted, dots, radius, (h, w)), len(dots), paper

    def check(
        self, snapshot: np.ndarray, origin=(0, 0), relocate: bool = True
    ) -> PageCheck:
        """Compare a page snapshot with the current model; relocate if moved."""
        if self.location is None:
            return self._relocate(snapshot, origin, PageCheck("moved", 0.0, 0), None)
        share = self._share(snapshot, origin)
        if share is None:
            return PageCheck("unknown", 0.0, 0)
        matched, count, paper = share
        check = PageCheck("same", matched, count)
        if matched >= self.suspect_ratio * self.baseline or not relocate:
            return check
        return self._relocate(snapshot, origin, check, paper)

    def _relocate(self, snapshot, origin, check: PageCheck, paper) -> PageCheck:
        previous, relocations, slip = self._state, self.relocations, self.slip_px
        try:
            self.locate(snapshot, origin)
        except (
            AnotoDecodeError,
            ValueError,
            np.linalg.LinAlgError,
            cv2.error,
        ) as error:
            with self._lock:
                self._state, self.relocations, self.slip_px = (
                    previous,
                    relocations,
                    slip,
                )
            return replace(check, status="unknown", error=str(error))
        if previous[0] is None:
            return replace(check, status="moved", relocated=True)
        # How far the model moved, over the visible paper of the snapshot.
        h, w = snapshot.shape
        old = self._printed_in(previous[0], previous[1], origin)
        new = self._printed_in(self.location, self.origin, origin)
        keep = _inside(new, h, w)
        if paper is not None:
            keep &= paper[_rows(new, h), _cols(new, w)] > 0
        shift = (
            float(np.median(np.linalg.norm(new[keep] - old[keep], axis=1)))
            if keep.any()
            else float("inf")
        )
        if shift <= self.moved_px:
            # False alarm (hand, noise): keep the model the track was using.
            with self._lock:
                self._state, self.relocations, self.slip_px = (
                    previous,
                    relocations,
                    slip,
                )
            self._candidate = None
            return replace(check, shift_px=shift)
        if self.confirm_jump_px is not None and shift > self.confirm_jump_px:
            candidate = (self.location, self.origin)
            confirmed = False
            if self._candidate is not None:
                prev_loc, prev_origin = self._candidate
                a = self._printed_in(prev_loc, prev_origin, origin)[keep]
                b = new[keep]
                confirmed = bool(
                    len(a)
                    and np.median(np.linalg.norm(a - b, axis=1)) <= 2 * self.moved_px
                )
            if not confirmed:
                # Hold the jump until a second snapshot agrees.
                with self._lock:
                    self._state, self.relocations, self.slip_px = (
                        previous,
                        relocations,
                        slip,
                    )
                self._candidate = candidate
                return replace(check, status="pending", shift_px=shift)
        self._candidate = None
        return replace(check, status="moved", relocated=True, shift_px=shift)


def paper_mask(gray: np.ndarray) -> np.ndarray:
    """Bright paper (not hand, pen or background), eroded away from its edges."""
    closed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    level = float(np.percentile(closed, 90))
    mask = (closed > 0.82 * level).astype(np.uint8)
    return cv2.erode(mask, np.ones((9, 9), np.uint8))


def _inside(points, h, w):
    return (
        (points[:, 0] >= 0)
        & (points[:, 1] >= 0)
        & (points[:, 0] < w)
        & (points[:, 1] < h)
    )


def _rows(points, h):
    return np.clip(np.rint(points[:, 1]).astype(int), 0, h - 1)


def _cols(points, w):
    return np.clip(np.rint(points[:, 0]).astype(int), 0, w - 1)


def _matched_share(predicted, dots, radius, shape) -> float:
    """Share of detected dots with a predicted printed dot within ``radius``."""
    h, w = shape
    mask = np.zeros((h, w), np.uint8)
    for x, y in np.rint(predicted).astype(int):
        cv2.circle(mask, (int(x), int(y)), max(1, int(round(radius))), 1, -1)
    return float(mask[_rows(dots, h), _cols(dots, w)].mean())
