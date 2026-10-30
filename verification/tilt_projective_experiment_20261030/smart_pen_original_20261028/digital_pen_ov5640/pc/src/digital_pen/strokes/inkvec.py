"""Strokes from the ink itself (Task 13 follow-up): vectorize the canvas ink.

The tip path says where and when the pen moved, but not reliably whether it
touched the paper; the canvas sees the ink that was actually written. Here
the shape comes from the ink and only the timing from the tip path:

  1. ink mask: new ink (``clean - first``) above ``threshold``, kept only
     within ``near_mm`` of the tip path (printed-dot residue and shadows
     elsewhere drop out), small holes closed, specks removed;
  2. skeleton (Zhang-Suen thinning), short spurs pruned;
  3. the skeleton traced into edges between end points and junctions
     (closed loops, e.g. a 口 written in one go, as cycles);
  4. a time for every skeleton pixel from the tip path: the closest
     tip-path segment within ``match_mm`` that runs along the ink there
     (direction within ~50 degrees; hover passes mostly cross the ink) and
     is not later than when the ink first appeared;
  5. edges split where the time jumps by more than ``gap_s`` (pen up), and
     pieces re-joined across junctions and touching ends when one starts
     right after the other ends (a 十's bar continues through the cross,
     a 横折 continues round the corner);
  6. pieces as page-mm polylines in writing order, resampled and smoothed,
     with the ink's own line width.

Everything is in canvas raster coordinates of one crop; ``to_mm`` maps crop
pixels (col, row) to page mm.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from digital_pen.strokes.post import resample, smooth
from digital_pen.strokes.segment import Stroke

_NEIGHBOURS = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))


@dataclass(frozen=True)
class InkVectorConfig:
    threshold: float = 0.08  # new-ink darkness
    min_cos: float = 0.65  # tip direction vs ink direction for timing
    near_mm: float = 1.5  # ink kept within this of the tip path
    min_area_mm2: float = 0.3  # specks smaller than this are dropped
    spur_mm: float = 0.75  # skeleton side branches shorter than this go
    match_mm: float = 1.5  # tip-path segments this close can time a pixel
    max_gap_s: float = 0.4  # tip-path segments longer in time are not used
    max_jump_mm: float = 10.0  # nor ones longer than this
    lag_s: float = 0.15  # ink may be "seen" slightly before the tip time
    gap_s: float = 0.15  # time jump along the ink that means pen up
    fill_mm: float = 3.0  # untimed skeleton runs this short are interpolated
    filter_mm: float = 2.0  # median filter of the times along an edge
    min_piece_mm: float = 1.25  # shorter time-split pieces are absorbed
    junction_mm: float = 1.0  # times this close to a junction are not used
    join_px: float = 4.0  # piece ends this close may be one stroke
    join_cos: float = 0.3  # and turning less than ~70 degrees
    min_len_mm: float = 0.6
    step_mm: float = 0.5
    # Keep ink no tip pass timed (the tip was lost there), timed by the
    # nearest tip point; for the final photo, where all ink is real.
    keep_untimed: bool = False


@dataclass
class InkStroke:
    t: np.ndarray  # (N,) s
    mm: np.ndarray  # (N, 2) page mm
    width_mm: float

    def as_stroke(self) -> Stroke:
        return Stroke(self.t, self.mm)


# -- raster helpers ------------------------------------------------------------------


def thin(mask: np.ndarray) -> np.ndarray:
    """Zhang-Suen thinning of a bool mask to one-pixel centrelines."""
    ys, xs = np.nonzero(mask)
    out = np.zeros(mask.shape, bool)
    if not len(ys):
        return out
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    img = np.pad(mask[y0:y1, x0:x1].astype(np.uint8), 1)
    order = ((1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1))
    changed = True
    while changed:
        changed = False
        for step in (0, 1):
            n = [np.roll(np.roll(img, dy, 0), dx, 1) for dy, dx in order]
            b = sum(n)
            a = sum((n[k] == 0) & (n[(k + 1) % 8] == 1) for k in range(8))
            if step == 0:
                c = (n[0] * n[2] * n[4] == 0) & (n[2] * n[4] * n[6] == 0)
            else:
                c = (n[0] * n[2] * n[6] == 0) & (n[0] * n[4] * n[6] == 0)
            remove = (img == 1) & (b >= 2) & (b <= 6) & (a == 1) & c
            if remove.any():
                img = img.copy()
                img[remove] = 0
                changed = True
    out[y0:y1, x0:x1] = img[1:-1, 1:-1].astype(bool)
    return out


def _degree(skel: np.ndarray) -> np.ndarray:
    k = np.ones((3, 3), np.float32)
    k[1, 1] = 0
    return np.where(
        skel, cv2.filter2D(skel.astype(np.float32), -1, k, borderType=0), 0
    ).astype(int)


def _neighbours(skel: np.ndarray, r: int, c: int):
    h, w = skel.shape
    for dr, dc in _NEIGHBOURS:
        rr, cc = r + dr, c + dc
        if 0 <= rr < h and 0 <= cc < w and skel[rr, cc]:
            yield rr, cc


def prune_spurs(skel: np.ndarray, length_px: int) -> np.ndarray:
    """Remove end branches shorter than ``length_px`` that hang off a junction."""
    skel = skel.copy()
    deg = _degree(skel)
    for r, c in zip(*np.nonzero(deg == 1), strict=True):
        path, prev, cur = [(r, c)], None, (r, c)
        while len(path) <= length_px:
            nxt = [p for p in _neighbours(skel, *cur) if p != prev and p not in path]
            if len(nxt) != 1:
                break
            prev, cur = cur, nxt[0]
            if deg[cur] >= 3:  # reached a junction: a short spur
                for p in path:
                    skel[p] = False
                break
            path.append(cur)
    return skel


def trace_edges(skel: np.ndarray) -> list[list[tuple[int, int]]]:
    """Skeleton -> pixel paths between nodes (ends, junctions), plus cycles."""
    deg = _degree(skel)
    node = skel & (deg != 2)
    seen_step: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    visited = np.zeros(skel.shape, bool)
    edges = []
    for r, c in zip(*np.nonzero(node), strict=True):
        visited[r, c] = True
        if deg[r, c] == 0:
            edges.append([(r, c)])
            continue
        for first in _neighbours(skel, r, c):
            if ((r, c), first) in seen_step:
                continue
            path, prev, cur = [(r, c), first], (r, c), first
            while not node[cur]:
                visited[cur] = True
                nxt = [p for p in _neighbours(skel, *cur) if p != prev]
                # prefer 4-neighbours so diagonal shortcuts are not doubled
                nxt.sort(key=lambda p: abs(p[0] - cur[0]) + abs(p[1] - cur[1]))
                if not nxt:
                    break
                prev, cur = cur, nxt[0]
                path.append(cur)
            seen_step.add(((r, c), first))
            seen_step.add((path[-1], path[-2]))
            edges.append(path)
    # cycles without any node
    for r, c in zip(*np.nonzero(skel & ~visited & ~node), strict=True):
        if visited[r, c]:
            continue
        path, prev, cur = [(r, c)], None, (r, c)
        visited[r, c] = True
        while True:
            nxt = [p for p in _neighbours(skel, *cur) if p != prev and not visited[p]]
            if not nxt:
                break
            prev, cur = cur, nxt[0]
            visited[cur] = True
            path.append(cur)
        path.append(path[0])
        edges.append(path)
    return edges


# -- timing ---------------------------------------------------------------------------


def pixel_times(
    mm: np.ndarray,
    direction: np.ndarray,
    inked: np.ndarray,
    tip_t: np.ndarray,
    tip_mm: np.ndarray,
    config: InkVectorConfig,
) -> np.ndarray:
    """Writing time of each skeleton pixel (nan when no tip pass is close).

    ``direction``: unit ink direction at each pixel."""
    if len(tip_t) < 2 or not len(mm):
        return np.full(len(mm), np.nan)
    a, b = tip_mm[:-1], tip_mm[1:]
    ab = b - a
    seg_len = np.linalg.norm(ab, axis=1)
    # segments across a gap in the tip track (lost tip, or points filtered
    # out between them) say nothing about where the pen was
    valid = (np.diff(tip_t) <= config.max_gap_s) & (seg_len <= config.max_jump_mm)
    L2 = np.maximum(seg_len**2, 1e-9)
    ap = mm[:, None, :] - a[None]
    s = np.clip((ap * ab[None]).sum(2) / L2[None], 0, 1)
    d = np.linalg.norm(ap - s[..., None] * ab[None], axis=2)
    t = tip_t[:-1][None] + s * (tip_t[1:] - tip_t[:-1])[None]
    unit = ab / np.maximum(seg_len, 1e-9)[:, None]
    cos = np.abs(direction @ unit.T)
    # a nearly still tip has no direction: do not let it veto
    cos = np.where(seg_len[None] < 0.3, 1.0, cos)
    close = (d <= config.match_mm) & valid[None]
    early = t <= (np.where(np.isfinite(inked), inked, np.inf) + config.lag_s)[:, None]
    out = np.full(len(mm), np.nan)
    for ok in (close & early & (cos >= config.min_cos), close & early, close):
        score = np.where(ok, d, np.inf)
        k = score.argmin(1)
        found = np.isfinite(score[np.arange(len(mm)), k]) & np.isnan(out)
        out[found] = t[found, k[found]]
    return out


def _directions(rc: np.ndarray) -> np.ndarray:
    """Unit direction along a pixel path (page mm axes: u = col, v = -row)."""
    n = len(rc)
    if n < 2:
        return np.tile((1.0, 0.0), (n, 1))
    i = np.arange(n)
    a, b = rc[np.maximum(i - 2, 0)], rc[np.minimum(i + 2, n - 1)]
    v = np.column_stack((b[:, 1] - a[:, 1], -(b[:, 0] - a[:, 0]))).astype(float)
    return v / np.maximum(np.linalg.norm(v, axis=1), 1e-9)[:, None]


def _fill_gaps(t: np.ndarray, max_run: int) -> np.ndarray:
    """Interpolate runs of nan up to ``max_run`` long between timed pixels;
    such runs at an end take the nearest time."""
    t = t.copy()
    bad = ~np.isfinite(t)
    if not bad.any() or bad.all():
        return t
    good = np.flatnonzero(~bad)
    edges = np.flatnonzero(np.diff(np.concatenate(([0], bad.astype(int), [0]))))
    for a, b in zip(edges[0::2], edges[1::2], strict=True):
        if b - a <= max_run:
            t[a:b] = np.interp(np.arange(a, b), good, t[good])
    return t


def _median_filter(x: np.ndarray, k: int = 5) -> np.ndarray:
    if len(x) < k:
        return x
    pad = np.pad(x, k // 2, mode="edge")
    windows = np.lib.stride_tricks.sliding_window_view(pad, k)
    return np.nanmedian(windows, axis=1)


# -- main ------------------------------------------------------------------------------


def vectorize(
    new_ink: np.ndarray,
    inked: np.ndarray,
    to_mm,
    mm_per_px: float,
    tip_t: np.ndarray,
    tip_mm: np.ndarray,
    to_px,
    config: InkVectorConfig | None = None,
    inked_window: tuple[float, float] | None = None,
) -> list[InkStroke]:
    """Ink strokes of one crop. ``to_mm``/``to_px`` map crop pixels <-> page mm.

    ``inked_window`` (t0, t1): only ink that first appeared in it (the ink of
    this writing, not older ink the pen passed over)."""
    c = config or InkVectorConfig()
    mask = np.nan_to_num(new_ink) > c.threshold
    if inked_window is not None:
        mask &= (inked >= inked_window[0]) & (inked <= inked_window[1])
    near = np.zeros(mask.shape, np.uint8)
    if len(tip_mm) >= 2:
        q = np.rint(to_px(tip_mm) * 4).astype(np.int32)
        cv2.polylines(near, [q], False, 1, 1, shift=2)
    elif len(tip_mm):
        q = np.rint(to_px(tip_mm)).astype(int)[0]
        cv2.circle(near, (int(q[0]), int(q[1])), 0, 1, -1)
    r = max(1, int(round(c.near_mm / mm_per_px)))
    near = cv2.dilate(
        near, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1,) * 2)
    )
    mask &= near > 0
    mask = (
        cv2.morphologyEx(
            mask.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)
        )
        > 0
    )
    count, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask.astype(np.uint8), connectivity=8
    )
    keep = np.zeros(count, bool)
    keep[1:] = stats[1:, cv2.CC_STAT_AREA] * mm_per_px**2 >= c.min_area_mm2
    mask = keep[labels]
    if not mask.any():
        return []
    width = cv2.distanceTransform(mask.astype(np.uint8), cv2.DIST_L2, 5) * 2 * mm_per_px
    skel = prune_spurs(thin(mask), int(round(c.spur_mm / mm_per_px)))
    edges = trace_edges(skel)
    deg = _degree(skel)
    junction = [
        (deg[e[0]] >= 3, deg[e[-1]] >= 3) if len(e) > 1 else (False, False)
        for e in edges
    ]
    # scraps between neighbouring junction pixels are not strokes
    keep_edges = [
        k for k, e in enumerate(edges) if not (len(e) <= 3 and all(junction[k]))
    ]
    edges = [edges[k] for k in keep_edges]
    junction = [junction[k] for k in keep_edges]
    near_node = max(1, int(round(c.junction_mm / mm_per_px)))
    # times per edge (each edge owns its pixels, junction pixels included)
    edge_t = []
    for e in edges:
        rc = np.array(e, float)
        edge_t.append(
            pixel_times(
                to_mm(rc[:, ::-1]),
                _directions(rc),
                inked[rc[:, 0].astype(int), rc[:, 1].astype(int)],
                tip_t,
                tip_mm,
                c,
            )
        )
    # split edges at time jumps, orient pieces forward in time
    pieces: list[list[tuple[int, int]]] = []
    piece_t: list[np.ndarray] = []
    window = max(5, int(round(c.filter_mm / mm_per_px)) | 1)
    short = int(round(c.min_piece_mm / mm_per_px))
    for e, raw_t, ends in zip(edges, edge_t, junction, strict=True):
        # at a crossing the pixels belong to both strokes: their times are
        # not this edge's own
        raw_t = raw_t.copy()
        if len(e) > 2 * near_node + 2:
            if ends[0]:
                raw_t[:near_node] = np.nan
            if ends[1]:
                raw_t[-near_node:] = np.nan
        t = _fill_gaps(raw_t, int(round(c.fill_mm / mm_per_px)))
        t = _median_filter(t, window)
        cut = [0]
        for i in range(1, len(e)):
            if (
                not (np.isfinite(t[i]) and np.isfinite(t[i - 1]))
                or abs(t[i] - t[i - 1]) > c.gap_s
            ):
                cut.append(i)
        cut.append(len(e))
        # absorb pieces too short to be strokes into their neighbours (a few
        # pixels timed by a hover pass are not a pen lift)
        runs = [(a, b) for a, b in zip(cut[:-1], cut[1:], strict=True) if b > a]
        while len(runs) > 1:
            k = min(range(len(runs)), key=lambda i: runs[i][1] - runs[i][0])
            if runs[k][1] - runs[k][0] >= short:
                break
            j = k - 1 if k > 0 else k + 1
            a, b = min(runs[k][0], runs[j][0]), max(runs[k][1], runs[j][1])
            runs[min(k, j)] = (a, b)
            del runs[max(k, j)]
            seg_t = t[a:b]
            if np.isfinite(seg_t).any():
                t[a:b] = np.interp(
                    np.arange(a, b),
                    np.flatnonzero(np.isfinite(seg_t)) + a,
                    seg_t[np.isfinite(seg_t)],
                )
        for a, b in runs:
            seg, ts = e[a:b], t[a:b]
            if len(seg) and not np.isfinite(ts).any() and c.keep_untimed and len(tip_t):
                where = to_mm(np.array(seg, float)[:, ::-1])
                d = np.linalg.norm(where[:, None] - tip_mm[None], axis=2)
                ts = tip_t[d.argmin(1)].astype(float)
            if not len(seg) or not np.isfinite(ts).any():
                continue
            ts = np.where(np.isfinite(ts), ts, np.nanmedian(ts))
            half = max(1, len(ts) // 2)
            if np.median(ts[half:]) < np.median(ts[:half]):
                seg, ts = seg[::-1], ts[::-1]
            pieces.append(list(seg))
            piece_t.append(np.maximum.accumulate(ts))  # forward in time
    # re-join pieces that continue one another in time
    order = sorted(range(len(pieces)), key=lambda i: piece_t[i][0])
    used_next: set[int] = set()
    nxt: dict[int, int] = {}
    starts = np.array([pieces[i][0] for i in range(len(pieces))], float)

    def heading(path, at_end):
        q = np.array(path[-6:] if at_end else path[:6], float)
        v = q[-1] - q[0]
        return v / max(np.linalg.norm(v), 1e-9)

    for i in order:
        end = np.array(pieces[i][-1], float)
        out_dir = heading(pieces[i], True)
        best, best_cost = None, np.inf
        for j in range(len(pieces)):
            if j == i or j in used_next:
                continue
            dt = piece_t[j][0] - piece_t[i][-1]
            if not (-0.05 <= dt <= c.gap_s) or np.hypot(*(starts[j] - end)) > c.join_px:
                continue
            turn = float(out_dir @ heading(pieces[j], False))
            if len(pieces[i]) > 4 and len(pieces[j]) > 4 and turn < c.join_cos:
                continue
            cost = dt + 0.1 * (1 - turn)
            if cost < best_cost:
                best, best_cost = j, cost
        if best is not None:
            nxt[i] = best
            used_next.add(best)
    out: list[InkStroke] = []
    has_prev = set(nxt.values())
    done: set[int] = set()
    for i in order:
        if i in has_prev or i in done:
            continue
        ids = [i]
        while ids[-1] in nxt and nxt[ids[-1]] not in done and nxt[ids[-1]] not in ids:
            ids.append(nxt[ids[-1]])
        done.update(ids)
        chain: list[tuple[int, int]] = []
        ts = []
        for k in ids:
            seg, tk = pieces[k], piece_t[k]
            if chain and seg[0] == chain[-1]:
                seg, tk = seg[1:], tk[1:]
            chain += seg
            ts.append(tk)
        t = np.concatenate(ts)
        rc = np.array(chain, float)
        mm = to_mm(rc[:, ::-1])
        stroke = Stroke(np.maximum.accumulate(t), mm)
        if stroke.length_mm < c.min_len_mm and len(pieces) > 1:
            continue
        stroke = smooth(resample(stroke, c.step_mm))
        w = float(np.median(width[rc[:, 0].astype(int), rc[:, 1].astype(int)]))
        out.append(InkStroke(stroke.t, stroke.mm, max(w, mm_per_px)))
    out.sort(key=lambda s: s.t[0])
    return out


# -- incremental layer (engine) --------------------------------------------------------


@dataclass
class InkPiece:
    id: int
    t: np.ndarray
    mm: np.ndarray
    width_mm: float
    epoch_t0: float  # page model it was vectorized under

    @property
    def box(self) -> np.ndarray:
        return np.concatenate((self.mm.min(0), self.mm.max(0)))

    @property
    def centre(self) -> np.ndarray:
        b = self.box
        return (b[:2] + b[2:]) / 2


def _inside(p: np.ndarray, box: np.ndarray) -> bool:
    return bool(box[0] <= p[0] <= box[2] and box[1] <= p[1] <= box[3])


def _overlaps(a: np.ndarray, b: np.ndarray) -> bool:
    return bool(a[0] <= b[2] and b[0] <= a[2] and a[1] <= b[3] and b[1] <= a[3])


class InkLayer:
    """Ink-vectorized pieces of one writing session, kept up to date.

    ``add_tip`` every frame with a tip on the page; ``update(canvas, ...)``
    when strokes settle, with the page-mm boxes they cover: the area (grown
    to the pieces already there) is vectorized again from the ink that
    appeared since the session started, and its pieces replaced. Pieces of
    earlier page models are kept as they are (their ink is old ink to the
    new canvas). Returns (removed ids, added pieces).
    """

    def __init__(
        self,
        config: InkVectorConfig | None = None,
        margin_mm: float = 3.0,
        max_tips: int = 200_000,
    ):
        self.config = config or InkVectorConfig()
        self.margin_mm = margin_mm
        self.max_tips = max_tips  # a whole session (~3 h at 21 fps)
        self.pieces: dict[int, InkPiece] = {}
        self._tips: list[tuple[float, float, float]] = []
        self._next_id = 0
        self.since = -np.inf
        self.excluded: list[tuple[float, float]] = []  # undone time ranges

    def add_tip(self, t: float, mm) -> None:
        self._tips.append((t, float(mm[0]), float(mm[1])))
        if len(self._tips) > self.max_tips:
            del self._tips[: len(self._tips) // 4]

    def reset(self, since: float) -> list[int]:
        """New or cleared session: drop everything, ignore older ink."""
        removed = list(self.pieces)
        self.pieces.clear()
        self._tips = [p for p in self._tips if p[0] >= since - 1.0]
        self.excluded.clear()
        self.since = since
        return removed

    def exclude(self, t0: float, t1: float) -> list[int]:
        """An undone stroke: drop pieces written in [t0, t1], now and later."""
        self.excluded.append((t0, t1))
        gone = [
            i
            for i, p in self.pieces.items()
            if t0 - 0.2 <= float(np.median(p.t)) <= t1 + 0.2
        ]
        for i in gone:
            del self.pieces[i]
        return gone

    def _excluded(self, t: np.ndarray) -> bool:
        m = float(np.median(t))
        return any(a - 0.2 <= m <= b + 0.2 for a, b in self.excluded)

    def update(self, canvas, epoch_t0: float, boxes, now: float):
        """prepare + compute + commit in one go (replay, tests, finishing)."""
        job = self.prepare(canvas, epoch_t0, boxes, now)
        if job is None:
            return [], []
        return self.commit(job, self.compute(job))

    def prepare(self, canvas, epoch_t0: float, boxes, now: float) -> dict | None:
        """Copy what vectorizing an area needs (engine thread; cheap)."""
        if not boxes:
            return None
        m = self.margin_mm
        box = np.array(boxes, float).reshape(-1, 4)
        box = np.concatenate((box[:, :2].min(0) - m, box[:, 2:].max(0) + m))
        for p in self.pieces.values():  # grow once to whole pieces already there
            if p.epoch_t0 == epoch_t0 and _overlaps(p.box, box):
                box = np.concatenate(
                    (np.minimum(box[:2], p.box[:2]), np.maximum(box[2:], p.box[2:]))
                )
        crop = np.concatenate((box[:2] - 1.5, box[2:] + 1.5))
        (c0, r1), (c1, r0) = np.rint(canvas.to_px([crop[:2], crop[2:]])).astype(int)
        r0, c0 = max(r0, 0), max(c0, 0)
        r1, c1 = min(r1 + 1, canvas.shape[0]), min(c1 + 1, canvas.shape[1])
        if r1 - r0 < 4 or c1 - c0 < 4:
            return None
        win = (slice(r0, r1), slice(c0, c1))
        tips = np.array(self._tips, float).reshape(-1, 3)
        since = max(self.since, epoch_t0)
        keep = (tips[:, 0] >= since - 1.0) & (tips[:, 0] <= now)
        pad = self.config.match_mm + 1.0
        keep &= (tips[:, 1] >= crop[0] - pad) & (tips[:, 1] <= crop[2] + pad)
        keep &= (tips[:, 2] >= crop[1] - pad) & (tips[:, 2] <= crop[3] + pad)
        new_ink = canvas.clean[win].astype(np.float32) - canvas.first[win].astype(
            np.float32
        )
        return {
            "box": box,
            "epoch_t0": epoch_t0,
            "now": now,
            "since": since,
            "new_ink": np.nan_to_num(new_ink),
            "inked": canvas.inked[win].copy(),
            "tips": tips[keep],
            "origin": np.array((c0, r0), float),
            "canvas": canvas.config,
            "excluded": list(self.excluded),
        }

    def compute(self, job: dict) -> list[InkStroke]:
        """Vectorize a prepared area (pure: safe in a worker thread)."""
        cc, origin = job["canvas"], job["origin"]
        mpp, top = cc.mm_per_px, cc.v0 + cc.size_mm

        def to_mm(px):
            px = np.asarray(px, float).reshape(-1, 2) + origin
            return np.column_stack((cc.u0 + px[:, 0] * mpp, top - px[:, 1] * mpp))

        def to_px(mm):
            mm = np.asarray(mm, float).reshape(-1, 2)
            return (
                np.column_stack(((mm[:, 0] - cc.u0) / mpp, (top - mm[:, 1]) / mpp))
                - origin
            )

        tips = job["tips"]
        return vectorize(
            job["new_ink"],
            job["inked"],
            to_mm,
            mpp,
            tips[:, 0],
            tips[:, 1:],
            to_px,
            self.config,
            inked_window=(job["since"] - 0.5, job["now"]),
        )

    def commit(self, job: dict, strokes: list[InkStroke]):
        """Replace the area's pieces (engine thread). (removed ids, added)."""
        box, epoch_t0 = job["box"], job["epoch_t0"]
        if job["since"] < self.since:  # the session was reset meanwhile
            return [], []
        removed = [
            i
            for i, p in self.pieces.items()
            if p.epoch_t0 == epoch_t0 and _inside(p.centre, box)
        ]
        for i in removed:
            del self.pieces[i]
        added = []
        for s in strokes:
            piece = InkPiece(self._next_id, s.t, s.mm, s.width_mm, epoch_t0)
            if not _inside(piece.centre, box) or self._excluded(s.t):
                continue
            self._next_id += 1
            self.pieces[piece.id] = piece
            added.append(piece)
        return removed, added
