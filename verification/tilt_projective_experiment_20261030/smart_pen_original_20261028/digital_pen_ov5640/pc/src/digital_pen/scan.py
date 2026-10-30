"""Scan of the written page from one camera still (photo finalization).

When writing ends the board takes a UXGA (1600x1200) still; a phone photo of
the sheet can be uploaded instead. This module turns either into a clean
picture of the real ink in page millimetres:

  1. locate the page from the dot pattern (the locator expects the SVGA dot
     spacing, ~9.3 px: a board still is scaled by its width; for a photo of
     unknown scale a few dot spacings are tried until the page decodes);
  2. rectify: every pixel of a page-mm raster (``mm_per_px``, u right, v up,
     row 0 at the top) is looked up in the still through the located model
     (perspective and lens bending included);
  3. lighting: the paper brightness is estimated with a grey closing larger
     than any stroke and divided out (shadows and vignetting cancel);
  4. dots: every printed dot sits at a known page position; those spots are
     inpainted from their surroundings, so dots vanish and ink crossing a
     dot stays continuous;
  5. ink: darkness mapped to a soft alpha (anti-aliased edges), specks
     removed, dark objects much wider than a pen line (the pen lying on the
     sheet, a hand) removed, optionally only ink near the pen's path.

``Scan.png()`` gives an RGBA image (ink colour + alpha) for the browser and
exports.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from digital_pen.pose import PageLayout, PageLocatorConfig, locate_page

SVGA_WIDTH = 800
SVGA_SPACING_PX = 9.3


@dataclass(frozen=True)
class ScanConfig:
    mm_per_px: float = 0.1
    margin_mm: float = 4.0  # around the writing box
    dot_radius_mm: float = 0.3  # printed dot; at least ~1 source pixel (blur)
    paper_mm: float = 1.6  # closing size for the paper level (> stroke width)
    ink_low: float = 0.05  # darkness where ink starts to show
    ink_high: float = 0.20  # darkness drawn as full ink
    ring_ink: float = 0.15  # a dot with this much darkness around is under ink
    snap_mm: float = 1.2  # predicted dots move onto a dark blob this close
    lone_area_mm2: float = 0.8  # smaller blobs need writing within lone_mm
    lone_mm: float = 4.0
    min_area_mm2: float = 0.12  # specks smaller than this are dropped
    near_mm: float = 0.0  # > 0: keep only ink this close to the pen's path
    thick_mm: float = 3.0  # dark objects wider than this are not ink
    thick_rim_mm: float = 0.6  # removed around them too


# Phone photos: sharper and higher contrast than the board camera, with JPEG
# ringing around the strokes; a higher darkness ramp keeps the paper clean.
PHOTO = ScanConfig(ink_low=0.14, ink_high=0.38, ring_ink=0.22)


@dataclass
class Scan:
    alpha: np.ndarray  # uint8, page raster (rows: v from top to bottom)
    box_mm: tuple[float, float, float, float]  # u0, v0, u1, v1
    mm_per_px: float
    rms_px: float  # page model fit of the still
    obstructed: bool = False  # something thick (pen, hand) lay on the sheet

    def png(self, color=(26, 26, 26)) -> bytes:
        rgba = np.zeros((*self.alpha.shape, 4), np.uint8)
        rgba[..., :3] = color[::-1]  # BGR for OpenCV
        rgba[..., 3] = self.alpha
        ok, data = cv2.imencode(".png", rgba)
        if not ok:
            raise RuntimeError("PNG encoding failed")
        return data.tobytes()

    def on_white(self) -> np.ndarray:
        """Grey picture (ink on white), for exports and checks."""
        return (255 - self.alpha.astype(np.float32) * (255 - 26) / 255).astype(np.uint8)


def _snap_to_blobs(
    dark: np.ndarray, xy: np.ndarray, c: ScanConfig, mpp: float
) -> np.ndarray:
    """Move each predicted dot onto the dark blob within ``snap_mm`` of it.

    Toward the edges of a photo the page model can be off by a fraction of
    a millimetre (lens, perspective, a curved sheet); the dots themselves
    show where they really are. Dots are 3.5 mm apart, so the nearest blob
    within ~1 mm is the dot's own."""
    h, w = dark.shape
    smooth = cv2.GaussianBlur(dark, (0, 0), max(1.0, 0.12 / mpp))
    k = max(3, int(round(0.8 / mpp)) | 1)
    peaks = (smooth >= cv2.dilate(smooth, np.ones((k, k), np.uint8))) & (
        smooth > c.ring_ink * 0.6
    )
    if not peaks.any():
        return xy
    # nearest peak of every pixel: distance transform with labels
    dist, labels = cv2.distanceTransformWithLabels(
        (~peaks).astype(np.uint8), cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL
    )
    rows, cols = np.nonzero(peaks)
    order = np.zeros(labels.max() + 1, int)
    # labels of DIST_LABEL_PIXEL number the zero pixels in row-major order
    order[1:] = np.arange(len(rows))
    x = np.clip(xy[:, 0], 0, w - 1)
    y = np.clip(xy[:, 1], 0, h - 1)
    near = dist[y, x] <= c.snap_mm / mpp
    idx = order[labels[y, x]]
    out = xy.copy()
    out[near, 0] = cols[idx[near]]
    out[near, 1] = rows[idx[near]]
    return out


def _dot_radius_px(dark: np.ndarray, xy: np.ndarray, c: ScanConfig, mpp: float) -> int:
    """Radius (raster px) of the printed dots as this still shows them
    (blur and focus vary): from the median darkness profile around the
    predicted dot centres, where it has fallen 80 % of the way to paper."""
    h, w = dark.shape
    radii = np.arange(0.0, 1.21, 0.1)
    angles = np.linspace(0, 2 * np.pi, 12, endpoint=False)
    profile = []
    for r in radii:
        dx = np.rint(r / mpp * np.cos(angles)).astype(int)
        dy = np.rint(r / mpp * np.sin(angles)).astype(int)
        xs = np.clip(xy[:, 0, None] + dx[None], 0, w - 1)
        ys = np.clip(xy[:, 1, None] + dy[None], 0, h - 1)
        profile.append(np.median(dark[ys, xs].mean(1)))
    profile = np.array(profile)
    peak, paper = profile[0], profile[-3:].mean()
    radius_mm = c.dot_radius_mm
    if peak - paper > 0.03:
        below = np.flatnonzero(profile <= paper + 0.2 * (peak - paper))
        if len(below):
            radius_mm = float(np.clip(radii[below[0]], 0.2, 0.9))
    return max(1, int(round(radius_mm / mpp)))


# Dot spacings (px) tried for photos of unknown scale, most likely first.
PHOTO_SPACINGS = (18.6, 15.0, 23.0, 12.0, 28.0, 35.0, 9.3, 44.0)


def _locate_at(gray: np.ndarray, layout: PageLayout, scale: float):
    small = (
        gray
        if abs(scale - 1) < 1e-6
        else cv2.resize(
            gray,
            (round(gray.shape[1] / scale), round(gray.shape[0] / scale)),
            interpolation=cv2.INTER_AREA if scale > 1 else cv2.INTER_CUBIC,
        )
    )
    return locate_page(
        small,
        layout,
        PageLocatorConfig(expected_spacing_px=SVGA_SPACING_PX, seed_attempts=12),
    )


def locate(gray: np.ndarray, layout: PageLayout, spacing_px: float | None = None):
    """Page model of a still or photo; returns (location, scale), where the
    location is in an image ``scale`` times smaller than ``gray``.

    Board stills (800 or 1600 wide) are scaled by their width; otherwise
    (photos) ``spacing_px`` or the PHOTO_SPACINGS are tried in turn."""
    if spacing_px is None and gray.shape[1] in (SVGA_WIDTH, 2 * SVGA_WIDTH):
        scale = gray.shape[1] / SVGA_WIDTH
        return _locate_at(gray, layout, scale), scale
    errors = []
    for spacing in (spacing_px,) if spacing_px else PHOTO_SPACINGS:
        scale = spacing / SVGA_SPACING_PX
        try:
            return _locate_at(gray, layout, scale), scale
        except Exception as error:  # noqa: BLE001 - try the next scale
            errors.append(f"{spacing:g} px: {type(error).__name__}")
    raise ValueError("page not found in the photo (" + "; ".join(errors) + ")")


def to_gray(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image


def scan_page(
    gray: np.ndarray,
    layout: PageLayout,
    box_mm=None,
    lines_mm=None,
    config: ScanConfig | None = None,
    located=None,
    crop_to_ink: bool = False,
) -> Scan:
    """Clean ink picture of ``box_mm`` (default: the pen's path, else the
    printed area).

    ``lines_mm``: the pen's path (list of (N, 2) page-mm arrays). With
    ``config.near_mm`` > 0 only ink near it is kept (off by default: the path
    can be offset where the paper moved, and specks are few anyway).
    ``located``: (location, scale) from ``locate`` if already known.
    ``crop_to_ink``: trim the picture to the ink found (e.g. a phone photo
    of the whole sheet with no pen path)."""
    c = config or ScanConfig()
    gray = to_gray(gray)
    location, scale = located if located is not None else locate(gray, layout)
    s = layout.spacing_mm
    if box_mm is None and lines_mm:
        pts = np.concatenate([np.asarray(p, float) for p in lines_mm if len(p)])
        box_mm = (*pts.min(0), *pts.max(0))
    if box_mm is None:
        rows, cols = layout.shape
        box_mm = (0.0, 0.0, (cols - 1) * s, (rows - 1) * s)
    m = c.margin_mm
    u0, v0, u1, v1 = box_mm[0] - m, box_mm[1] - m, box_mm[2] + m, box_mm[3] + m
    mpp = c.mm_per_px
    w, h = int(np.ceil((u1 - u0) / mpp)), int(np.ceil((v1 - v0) / mpp))
    # page mm -> still pixels on a 1 mm grid, interpolated to the raster
    gu = np.arange(u0, u1 + 1.0, 1.0)
    gv = np.arange(v1, v0 - 1.0, -1.0)
    uu, vv = np.meshgrid(gu, gv)
    px = location.page_to_pixel(np.column_stack((uu.ravel(), vv.ravel())) / s)
    px = (px + 0.5) * scale - 0.5
    map_x = px[:, 0].reshape(uu.shape).astype(np.float32)
    map_y = px[:, 1].reshape(uu.shape).astype(np.float32)
    # exact bilinear lookup of the 1 mm grid (cv2.resize would align pixel
    # centres, not the grid points, and shift the map up to half a cell)
    fx, fy = np.meshgrid(
        (np.arange(w, dtype=np.float32) + 0.5) * mpp,
        (np.arange(h, dtype=np.float32) + 0.5) * mpp,
    )
    map_x = cv2.remap(map_x, fx, fy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    map_y = cv2.remap(map_y, fx, fy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    rect = cv2.remap(
        gray.astype(np.float32),
        map_x,
        map_y,
        cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,  # off the photo: white paper
        borderValue=255,
    )
    # paper level: grey closing removes everything darker and thinner
    r = max(3, int(round(c.paper_mm / mpp)) | 1)
    paper = cv2.dilate(rect, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (r, r)))
    paper = cv2.GaussianBlur(paper, (0, 0), r / 2)
    dark = np.clip(1.0 - rect / np.maximum(paper, 1.0), 0, 1)
    # printed dots at their known positions
    _, printed = layout.printed_positions()
    dots = printed * s
    inside = (
        (dots[:, 0] > u0 - 1)
        & (dots[:, 0] < u1 + 1)
        & (dots[:, 1] > v0 - 1)
        & (dots[:, 1] < v1 + 1)
    )
    dots = dots[inside]
    mask = np.zeros((h, w), np.uint8)
    xy = (
        np.column_stack(((dots[:, 0] - u0) / mpp - 0.5, (v1 - dots[:, 1]) / mpp - 0.5))
        .round()
        .astype(int)
    )
    xy = _snap_to_blobs(dark, xy, c, mpp)
    rad = _dot_radius_px(dark, xy, c, mpp)
    # a dot with ink around it lies under a stroke: leave it (erasing it
    # would cut the stroke; under ink it is invisible anyway)
    gap = max(2, int(round(0.2 / mpp)))
    ring = np.zeros((2 * (rad + gap) + 1,) * 2, np.uint8)
    cv2.circle(ring, (rad + gap, rad + gap), rad + gap, 1, 1)
    ring_rc = np.argwhere(ring > 0) - (rad + gap)
    # darkness on the ring that a neighbouring printed dot explains is not ink
    others = np.zeros((h, w), np.uint8)
    for x, y in xy:
        cv2.circle(others, (int(x), int(y)), rad + 1, 1, -1)
    for x, y in xy:
        rr, cc = ring_rc[:, 0] + y, ring_rc[:, 1] + x
        ok = (rr >= 0) & (rr < h) & (cc >= 0) & (cc < w)
        rr, cc = rr[ok], cc[ok]
        free = others[rr, cc] == 0
        if free.any() and dark[rr[free], cc[free]].max() > c.ring_ink:
            continue
        cv2.circle(mask, (x, y), rad, 255, -1)
    dark8 = np.clip(dark * 255, 0, 255).astype(np.uint8)
    dark8 = cv2.inpaint(dark8, mask, rad + 1, cv2.INPAINT_TELEA)
    dark = dark8.astype(np.float32) / 255
    # ink alpha, specks out, optionally only near the pen's path
    alpha = np.clip((dark - c.ink_low) / (c.ink_high - c.ink_low), 0, 1)
    solid = (dark > (c.ink_low + c.ink_high) / 2).astype(np.uint8)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(solid, connectivity=8)
    keep = np.zeros(n, bool)
    keep[1:] = stats[1:, cv2.CC_STAT_AREA] * mpp**2 >= c.min_area_mm2
    if lines_mm and c.near_mm > 0:
        near = np.zeros((h, w), np.uint8)
        for p in lines_mm:
            p = np.asarray(p, float)
            if len(p) < 1:
                continue
            q = np.column_stack(((p[:, 0] - u0) / mpp, (v1 - p[:, 1]) / mpp))
            cv2.polylines(near, [np.rint(q * 4).astype(np.int32)], False, 1, 1, shift=2)
        rr = int(round(c.near_mm / mpp))
        near = cv2.dilate(
            near, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * rr + 1,) * 2)
        )
        hit = np.zeros(n, bool)
        hit[np.unique(labels[(near > 0) & (solid > 0)])] = True
        keep &= hit
    support = cv2.dilate(keep[labels].astype(np.uint8), np.ones((3, 3), np.uint8))
    # objects far wider than a pen line (the pen lying on the sheet, a hand
    # or sleeve) are not writing: drop them with a small rim
    t = max(3, int(round(c.thick_mm / mpp)) | 1)
    thick = cv2.morphologyEx(
        solid, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (t, t))
    )
    obstructed = bool(thick.sum() * mpp**2 > 4.0)  # > 4 mm2 of it
    if thick.any():
        rim = max(1, int(round(c.thick_rim_mm / mpp)))
        thick = cv2.dilate(
            thick, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * rim + 1,) * 2)
        )
        support[thick > 0] = 0
    # small blobs with no real writing nearby are leftover dots (beyond the
    # snapping range, e.g. at the edges of a photo), not punctuation
    kept = keep[labels] & (support > 0)
    big = np.zeros(n, bool)
    big[1:] = stats[1:, cv2.CC_STAT_AREA] * mpp**2 >= c.lone_area_mm2
    reach = max(1, int(round(c.lone_mm / mpp)))
    near_big = cv2.dilate(
        (big[labels] & kept).astype(np.uint8),
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * reach + 1,) * 2),
    )
    lone = np.zeros(n, bool)
    small = np.flatnonzero(keep & ~big)
    if len(small):
        touched = np.zeros(n, bool)
        touched[np.unique(labels[(near_big > 0) & (solid > 0)])] = True
        lone[small] = ~touched[small]
    support[
        cv2.dilate(lone[labels].astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    ] = 0
    alpha = np.where(support > 0, alpha, 0)
    alpha = (alpha * 255).astype(np.uint8)
    if crop_to_ink and alpha.any():
        rows, cols = np.nonzero(alpha > 32)
        pad = int(round(c.margin_mm / mpp))
        r0, r1 = max(rows.min() - pad, 0), min(rows.max() + pad + 1, h)
        c0, c1 = max(cols.min() - pad, 0), min(cols.max() + pad + 1, w)
        alpha = alpha[r0:r1, c0:c1]
        u0, u1 = u0 + c0 * mpp, u0 + c1 * mpp
        v0, v1 = v1 - r1 * mpp, v1 - r0 * mpp
    return Scan(alpha, (u0, v0, u1, v1), mpp, float(location.rms_px), obstructed)
