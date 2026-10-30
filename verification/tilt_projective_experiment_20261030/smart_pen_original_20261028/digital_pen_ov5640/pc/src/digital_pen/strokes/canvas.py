"""Paper canvas: how dark the paper looked, in page millimetres (Task 11).

Each ROI frame is warped into a fixed page-coordinate raster (``mm_per_px``,
page ``u`` right, ``v`` up, row 0 at the top) and written where nothing
covers the paper (pen, hand and their shadows are masked by the caller).
Kept per raster pixel:

  first   darkness when the pixel was first seen (printed dots, old ink)
  clean   darkness when it was last seen uncovered
  stamp   time of that last uncovered view (s)
  inked   time the pixel was first seen at least ``ink_threshold`` darker
          than ``first`` (inf if never): when ink appeared there
  clear   last time the pixel was seen without such new ink (-inf if never).
          Ink is only known to be written after ``clear``: ``inked`` alone
          can lag far behind the writing when the hand covered the spot.

New ink anywhere is ``clean - first``; whether ink appeared at a tip point
is decided by comparing ``clean`` just before the tip got there with
``clean`` after it left (see ink.py). Everything is in page coordinates, so
the canvas stays valid when the paper moves and the page is located again.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class CanvasConfig:
    mm_per_px: float = 0.25
    # Page extent covered (mm): u from u0, v from v0, both size_mm long.
    u0: float = -6.0
    v0: float = -6.0
    size_mm: float = 206.0
    ink_threshold: float = 0.08


class PaperCanvas:
    def __init__(self, config: CanvasConfig | None = None):
        self.config = c = config or CanvasConfig()
        n = int(round(c.size_mm / c.mm_per_px))
        self.shape = (n, n)
        # Compact types: ~11 MB per canvas (darkness to 1e-3, times to ms).
        self.first = np.full(self.shape, np.nan, np.float16)
        self.clean = np.full(self.shape, np.nan, np.float16)
        self.stamp = np.full(self.shape, -np.inf, np.float32)
        self.inked = np.full(self.shape, np.inf, np.float32)
        self.clear = np.full(self.shape, -np.inf, np.float32)

    # -- coordinates -------------------------------------------------------------

    def to_px(self, mm) -> np.ndarray:
        """Page mm (u, v) -> raster (col, row), float."""
        c = self.config
        mm = np.asarray(mm, float).reshape(-1, 2)
        return np.column_stack(
            (
                (mm[:, 0] - c.u0) / c.mm_per_px,
                (c.v0 + c.size_mm - mm[:, 1]) / c.mm_per_px,
            )
        )

    def to_mm(self, px) -> np.ndarray:
        c = self.config
        px = np.asarray(px, float).reshape(-1, 2)
        return np.column_stack(
            (c.u0 + px[:, 0] * c.mm_per_px, c.v0 + c.size_mm - px[:, 1] * c.mm_per_px)
        )

    # -- update --------------------------------------------------------------------

    def update(
        self,
        darkness: np.ndarray,
        valid: np.ndarray,
        frame_to_mm,
        t: float,
    ) -> tuple[int, int, int, int] | None:
        """Write one frame. ``frame_to_mm`` maps frame pixels (N, 2) to page mm.

        A homography fitted on a 5x5 grid of the frame stands in for the page
        model over the ROI (the spline part is smooth at this scale). Returns
        the raster box written (col0, row0, col1, row1), or None.
        """
        h, w = darkness.shape
        gx, gy = np.meshgrid(np.linspace(0, w - 1, 5), np.linspace(0, h - 1, 5))
        frame_pts = np.column_stack((gx.ravel(), gy.ravel()))
        raster = self.to_px(frame_to_mm(frame_pts))
        homography, _ = cv2.findHomography(raster, frame_pts)
        if homography is None:
            return None
        col0, row0 = np.floor(raster.min(0)).astype(int)
        col1, row1 = np.ceil(raster.max(0)).astype(int) + 1
        col0, row0 = max(col0, 0), max(row0, 0)
        col1, row1 = min(col1, self.shape[1]), min(row1, self.shape[0])
        if col1 <= col0 or row1 <= row0:
            return None
        shift = np.array(((1, 0, col0), (0, 1, row0), (0, 0, 1)), float)
        patch_to_frame = homography @ shift
        size = (col1 - col0, row1 - row0)
        flags = cv2.WARP_INVERSE_MAP
        value = cv2.warpPerspective(
            darkness.astype(np.float32),
            patch_to_frame,
            size,
            flags=flags | cv2.INTER_LINEAR,
        )
        ok = cv2.warpPerspective(
            valid.astype(np.uint8),
            patch_to_frame,
            size,
            flags=flags | cv2.INTER_NEAREST,
            borderValue=0,
        ).astype(bool)
        # Pixels next to an invalid one get a blend of both: drop them.
        ok &= cv2.erode(ok.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        box = (slice(row0, row1), slice(col0, col1))
        first, clean, stamp = self.first[box], self.clean[box], self.stamp[box]
        new = ok & np.isnan(first)
        first[new] = value[new]
        clean[ok] = value[ok]
        stamp[ok] = t
        inked = self.inked[box]
        darker = value - first > self.config.ink_threshold
        appeared = ok & np.isinf(inked) & darker
        inked[appeared] = t
        clear = self.clear[box]
        clear[ok & ~darker] = t
        return col0, row0, col1, row1

    # -- reading --------------------------------------------------------------------

    def window(self, mm, radius_mm: float):
        """Raster slices of a square window around a page point (or None)."""
        col, row = self.to_px(mm)[0]
        r = int(np.ceil(radius_mm / self.config.mm_per_px))
        ci, ri = int(round(col)), int(round(row))
        if not (r <= ci < self.shape[1] - r and r <= ri < self.shape[0] - r):
            return None
        return slice(ri - r, ri + r + 1), slice(ci - r, ci + r + 1)

    def patch(self, mm, radius_mm: float, layer: str = "clean") -> np.ndarray | None:
        """Copy of the square window around a page point (or None)."""
        box = self.window(mm, radius_mm)
        return None if box is None else getattr(self, layer)[box].copy()

    def peak(self, mm, radius_mm: float, layer: str = "clean") -> float:
        """Darkest value within ``radius_mm`` of a page point (nan if unseen)."""
        box = self.window(mm, radius_mm)
        if box is None:
            return float("nan")
        values = getattr(self, layer)[box]
        if np.all(np.isnan(values)):
            return float("nan")
        return float(np.nanmax(values))

    def seen_since(self, mm, t: float, radius_mm: float, share: float = 0.6) -> bool:
        """Was most of the window around ``mm`` seen uncovered after ``t``?"""
        box = self.window(mm, radius_mm)
        if box is None:
            return False
        return float(np.mean(self.stamp[box] > t)) >= share

    def new_ink(self) -> np.ndarray:
        """Darkness added since first seen (0 where unseen), float32."""
        out = self.clean.astype(np.float32) - self.first.astype(np.float32)
        out[np.isnan(out)] = 0
        return out
