"""Strokes rebuilt from the final photo and the tip path (Task 18 follow-up).

Without a pen-down sensor the tip path alone cannot tell writing from
hovering, and it has gaps where the tip was lost. The final photo (Task 13)
shows exactly where the ink is, but not in what order. Together:

  1. the photo's ink (near the pen path) is thinned to centre lines and
     traced into edges between ends and junctions (``inkvec`` helpers);
     junction pixels that touch form one node;
  2. every edge gets a time profile from the tip path that ran along it
     (``inkvec.pixel_times``), gaps filled along the edge and smoothed; an
     edge the tip never reached takes the times of the nearest tip points;
  3. an edge is cut only where its time really jumps or turns back (a 竖 and
     the 横折 written after it meet in one corner of the ink), into pieces of
     at least ``min_piece_mm``;
  4. pieces are chained through junctions by good continuation: the pair
     that goes straight on and is written at about the same time (the 横 of
     a 十 runs through the cross); free ends this close and in line are
     joined too (a faint gap in the ink line);
  5. chains are oriented by their times and ordered by start time.

So the shape comes from the photo, the order and direction from the pen. A
first version (``inkvec.vectorize`` on the photo) cut at every small time
jump and broke characters into many pieces (rated samples: stroke count
right in 2/65 vs 20/65 for the tip path).

The photo is the session's scan: ``gray`` (white paper, dark ink) on the
page box ``box_mm`` (u0, v0, u1, v1) at ``mm_per_px``, row 0 at v1.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import cv2
import numpy as np

from digital_pen.strokes.inkvec import (
    InkStroke,
    InkVectorConfig,
    _degree,
    _directions,
    pixel_times,
    prune_spurs,
    thin,
    trace_edges,
)
from digital_pen.strokes.post import resample, smooth
from digital_pen.strokes.segment import Stroke


@dataclass(frozen=True)
class PhotoConfig:
    work_mm_per_px: float = 0.2  # the photo is reduced to this first
    threshold: float = 0.2  # ink darkness (0..1) in the photo
    # ink is this writing when its connected piece comes this close to the
    # pen path (all of it then: also where the tip was lost)
    near_mm: float = 2.5
    min_area_mm2: float = 0.5  # specks smaller than this go
    close_mm: float = 0.6  # holes in thick ink smaller than this are filled
    spur_mm: float = 1.0  # skeleton side branches shorter than this go
    filter_mm: float = 2.0  # median filter of the time along an edge
    gap_s: float = 0.35  # time jump along the ink that means pen up
    turn_s: float = 0.25  # a time peak/valley this deep: two strokes
    min_piece_mm: float = 2.0
    junction_mm: float = 1.5  # times this close to a junction are not used
    join_cos: float = 0.5  # continuation through a node: turn < 60 degrees
    join_dt_s: float = 0.6  # and written within this
    join_gap_mm: float = 1.5  # ends this close may be one line
    # written without a pause on both sides: one stroke round any corner
    corner_dt_s: float = 0.3
    min_len_mm: float = 1.5  # shorter chains are crumbs
    crumb_mm: float = 4.0  # shorter chains touching a longer stroke too
    crumb_touch_mm: float = 2.0
    # share of its points that close to a longer stroke; 0: any point (rated
    # samples: exact count 28/65 vs 19/65 at 0.7, ink coverage 0.80 vs 0.82)
    crumb_share: float = 0.0
    step_mm: float = 0.5
    # timing of ink pixels from the tip path (only the matching part is used)
    timing: InkVectorConfig = field(
        default_factory=lambda: InkVectorConfig(match_mm=2.0, max_gap_s=0.4)
    )


def tip_path(strokes) -> tuple[np.ndarray, np.ndarray]:
    """Times (N,) and page mm (N, 2) of session strokes, in time order.
    ``strokes``: (t, mm) pairs."""
    pairs = sorted(
        (
            (np.asarray(t, float).reshape(-1), np.asarray(mm, float).reshape(-1, 2))
            for t, mm in strokes
            if len(mm)
        ),
        key=lambda p: p[0][0],
    )
    if not pairs:
        return np.zeros(0), np.zeros((0, 2))
    return np.concatenate([t for t, _ in pairs]), np.concatenate([m for _, m in pairs])


_RING = ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1))


def _one_pixel(skel: np.ndarray) -> np.ndarray:
    """Remove skeleton pixels the line does not need (2-pixel staircases
    left by thinning in thick ink): a pixel goes when its neighbours stay
    one connected group without it and it is not a line end. Without this,
    whole runs of thick ink looked like one big junction and were dropped
    (live 2026-10-27: ~20% of the ink)."""
    skel = skel.copy()
    h, w = skel.shape
    changed = True
    while changed:
        changed = False
        deg = cv2.filter2D(skel.astype(np.uint8), -1, np.ones((3, 3), np.float32)) - 1
        for r, c in zip(*np.nonzero(skel & (deg >= 2)), strict=True):
            if not (0 < r < h - 1 and 0 < c < w - 1):
                continue
            on = [i for i, (dr, dc) in enumerate(_RING) if skel[r + dr, c + dc]]
            if len(on) < 2 or _groups(on) != 1:
                continue
            skel[r, c] = False
            changed = True
    return skel


# neighbour positions i, j touch (8-adjacent) when they are next to each other
_TOUCH = [
    [
        i != j and max(abs(a[0] - b[0]), abs(a[1] - b[1])) == 1
        for j, b in enumerate(_RING)
    ]
    for i, a in enumerate(_RING)
]


def _groups(on: list[int]) -> int:
    """Connected groups among the set neighbour positions."""
    left, groups = set(on), 0
    while left:
        groups += 1
        stack = [left.pop()]
        while stack:
            i = stack.pop()
            for j in [j for j in left if _TOUCH[i][j]]:
                left.remove(j)
                stack.append(j)
    return groups


def _median(x: np.ndarray, k: int) -> np.ndarray:
    if len(x) < k:
        return x
    pad = np.pad(x, k // 2, mode="edge")
    return np.median(np.lib.stride_tricks.sliding_window_view(pad, k), axis=1)


def _cuts(t: np.ndarray, c: PhotoConfig, min_px: int) -> list[int]:
    """Indices where an edge's (smoothed) time profile splits."""
    cuts = [i for i in range(1, len(t)) if abs(t[i] - t[i - 1]) > c.gap_s]

    def turn(a: int, b: int) -> None:  # one peak or valley per stretch
        seg = t[a:b]
        if b - a <= 2 * min_px:
            return
        inner = slice(min_px, len(seg) - min_px)
        for k in (int(np.argmax(seg[inner])), int(np.argmin(seg[inner]))):
            k += min_px
            left, right = seg[: k + 1], seg[k:]
            peak = min(seg[k] - left.min(), seg[k] - right.min())
            valley = min(left.max() - seg[k], right.max() - seg[k])
            if max(peak, valley) >= c.turn_s:
                cuts.append(a + k)
                turn(a, a + k)
                turn(a + k, b)
                return

    bounds = [0, *sorted(cuts), len(t)]
    for a, b in zip(bounds[:-1], bounds[1:], strict=True):
        turn(a, b)
    return sorted(set(cuts))


def reconstruct(
    gray: np.ndarray,
    box_mm,
    mm_per_px: float,
    strokes,
    config: PhotoConfig | None = None,
    debug: dict | None = None,
) -> list[InkStroke]:
    """Strokes (page mm, writing order) from the photo and the tip path.
    ``debug``: filled with the pieces and join candidates (development)."""
    c = config or PhotoConfig()
    w = c.work_mm_per_px
    tip_t, tip_mm = tip_path(strokes)
    if not len(tip_t):
        return []
    f = mm_per_px / w
    darkness = (255.0 - gray.astype(np.float32)) / 255.0
    ink = cv2.resize(darkness, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
    u0, _, _, v1 = box_mm

    def to_mm(px):
        px = np.asarray(px, float).reshape(-1, 2)
        return np.column_stack((u0 + (px[:, 0] + 0.5) * w, v1 - (px[:, 1] + 0.5) * w))

    def to_px(mm):
        mm = np.asarray(mm, float).reshape(-1, 2)
        return np.column_stack(((mm[:, 0] - u0) / w - 0.5, (v1 - mm[:, 1]) / w - 0.5))

    # 1. ink of this writing -> skeleton -> edges, junction clusters as nodes
    mask = ink > c.threshold
    k = max(3, round(c.close_mm / w) | 1)
    mask = cv2.morphologyEx(
        mask.astype(np.uint8),
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)),
    )
    near = np.zeros(mask.shape, np.uint8)
    cv2.polylines(
        near, [np.rint(to_px(tip_mm) * 4).astype(np.int32)], False, 1, 1, shift=2
    )
    r = max(1, round(c.near_mm / w))
    near = cv2.dilate(
        near, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1,) * 2)
    )
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    keep = np.zeros(count, bool)
    keep[np.unique(labels[(near > 0) & (mask > 0)])] = True  # touches the path
    keep[0] = False
    keep &= stats[:, cv2.CC_STAT_AREA] * w * w >= c.min_area_mm2
    if debug is not None:
        debug["stage_mm"] = {"ink": float(thin(mask > 0).sum() * w)}
    mask = keep[labels]
    if not mask.any():
        return []
    width = cv2.distanceTransform(mask.astype(np.uint8), cv2.DIST_L2, 5) * 2 * w
    skel = prune_spurs(_one_pixel(thin(mask)), round(c.spur_mm / w))
    if debug is not None:
        debug["stage_mm"]["this writing"] = float(thin(mask).sum() * w)
        debug["stage_mm"]["skeleton"] = float(skel.sum() * w)
    deg = _degree(skel)
    _, node_of = cv2.connectedComponents((deg >= 3).astype(np.uint8), connectivity=8)
    edges = [e for e in trace_edges(skel) if len(e) > 1]
    # thinning can shrink a short mark (a 点, a tick) to a pixel or two: such
    # a blob becomes the line along its long axis
    count, blobs = cv2.connectedComponents(mask.astype(np.uint8), connectivity=8)
    for k in range(1, count):
        inside = blobs == k
        if int((skel & inside).sum()) >= 3:
            continue
        rc = np.argwhere(inside).astype(float)
        centre = rc.mean(0)
        axis = np.linalg.svd(rc - centre, full_matrices=False)[2][0]
        s = (rc - centre) @ axis
        n = max(2, int(np.ceil(s.max() - s.min())) + 1)
        line = centre + np.linspace(s.min(), s.max(), n)[:, None] * axis
        path = [tuple(p) for p in np.rint(line).astype(int)]
        edges.append([p for i, p in enumerate(path) if i == 0 or p != path[i - 1]])

    def node(p) -> int | None:  # junction cluster id of an end pixel, or None
        return int(node_of[p]) if deg[p] >= 3 else None

    # scraps inside one junction cluster are not strokes
    edges = [
        e
        for e in edges
        if not (len(e) <= 4 and node(e[0]) is not None and node(e[0]) == node(e[-1]))
    ]
    # 2-3. time profile per edge, cut at real jumps / turns
    k_filter = max(5, round(c.filter_mm / w) | 1)
    min_px = max(2, round(c.min_piece_mm / w))
    near_node = max(1, round(c.junction_mm / w))
    pieces = []  # (pixels, times, node at start, node at end)
    for e in edges:
        rc = np.array(e, float)
        where = to_mm(rc[:, ::-1])
        t = pixel_times(
            where, _directions(rc), np.full(len(e), np.inf), tip_t, tip_mm, c.timing
        )
        # at a junction the other stroke's pass is just as close: those
        # times are not this edge's own
        if len(e) > 2 * near_node + 2:
            if node(e[0]) is not None:
                t[:near_node] = np.nan
            if node(e[-1]) is not None:
                t[-near_node:] = np.nan
        ok = np.isfinite(t)
        if ok.any():
            t = np.interp(np.arange(len(t)), np.flatnonzero(ok), t[ok])
        else:  # the tip never got here: the nearest tip points' times
            t = tip_t[np.linalg.norm(where[:, None] - tip_mm[None], axis=2).argmin(1)]
        t = _median(t, k_filter)
        bounds = [0, *_cuts(t, c, min_px), len(e)]
        for a, b in zip(bounds[:-1], bounds[1:], strict=True):
            if b - a < 2:
                continue
            start = node(e[a]) if a == 0 else None
            end = node(e[b - 1]) if b == len(e) else None
            pieces.append((e[a:b], t[a:b], start, end))
    if debug is not None:
        debug["stage_mm"]["edges"] = float(sum(len(e) for e in edges) * w)
        debug["stage_mm"]["pieces"] = float(sum(len(p[0]) for p in pieces) * w)
    if not pieces:
        return []

    # 4. chain pieces: through junction nodes, and free ends close in line
    def end_info(i: int, side: int):
        px, ts = pieces[i][0], pieces[i][1]
        n = min(len(px), max(3, round(1.5 / w)))
        seg = np.array(px[:n] if side == 0 else px[-n:][::-1], float)
        out = seg[-1] - seg[0]  # pointing from the end into the piece
        out = -out / max(np.linalg.norm(out), 1e-9)  # away from the piece
        t_end = float(np.median(ts[:n] if side == 0 else ts[-n:]))
        return np.array(px[0] if side == 0 else px[-1], float), out, t_end

    ends = [(i, s) for i in range(len(pieces)) for s in (0, 1)]
    info = {key: end_info(*key) for key in ends}
    candidates = []
    for x in range(len(ends)):
        for y in range(x + 1, len(ends)):
            a, b = ends[x], ends[y]
            if a[0] == b[0]:
                continue
            na = pieces[a[0]][2 + a[1]]
            nb = pieces[b[0]][2 + b[1]]
            pa, oa, ta = info[a]
            pb, ob, tb = info[b]
            if na is not None and na == nb:
                pass  # meet in a junction
            elif np.hypot(*(pa - pb)) * w <= c.join_gap_mm:
                pass  # ends next to each other (a faint gap in the ink line)
            else:
                continue
            straight = -float(oa @ ob)  # 1: one goes on where the other stops
            dt = abs(ta - tb)
            if (straight >= c.join_cos and dt <= c.join_dt_s) or dt <= c.corner_dt_s:
                candidates.append(((1 - straight) + dt, a, b))
    if debug is not None:
        debug["pieces"] = [
            (len(px), a, b, round(float(ts[0]), 2), round(float(ts[-1]), 2))
            for px, ts, a, b in pieces
        ]
        debug["ends"] = {
            k: (v[1].round(2).tolist(), round(v[2], 2)) for k, v in info.items()
        }
        debug["candidates"] = candidates
    link: dict[tuple[int, int], tuple[int, int]] = {}
    for _, a, b in sorted(candidates, key=lambda x: x[0]):
        if a not in link and b not in link:
            link[a], link[b] = b, a
    # walk the chains
    used = set()
    chains = []
    for start in range(len(pieces)):
        if start in used:
            continue
        # go to one end of the chain first
        i, side = start, 0
        seen = {start}
        while (i, side) in link:
            j, s = link[(i, side)]
            if j in seen:
                break
            seen.add(j)
            i, side = j, 1 - s
        # i's ``side`` end is a chain end: walk from it
        chain, cur, enter = [], i, side
        while True:
            used.add(cur)
            chain.append((cur, enter))
            nxt = link.get((cur, 1 - enter))
            if nxt is None or nxt[0] in used:
                break
            cur, enter = nxt
        chains.append(chain)

    # 5. chains as strokes: orient by time, order by start
    built = []  # (stroke, pixels)
    for chain in chains:
        px, ts = [], []
        for i, enter in chain:
            p, t = pieces[i][0], pieces[i][1]
            if enter == 1:
                p, t = p[::-1], t[::-1]
            px += list(p)
            ts.append(t)
        t = np.concatenate(ts)
        half = max(1, len(t) // 2)
        if np.median(t[half:]) < np.median(t[:half]):
            px, t = px[::-1], t[::-1]
        rc = np.array(px, float)
        built.append((Stroke(np.maximum.accumulate(t), to_mm(rc[:, ::-1])), rc))
    # crumbs: very short chains, and short ones touching a longer stroke
    # (bits of a thick or broken line; ``crumb_share`` > 0 keeps those that
    # only touch it at one end); a short mark on its own (a dot) stays
    long_pts = [b[0].mm for b in built if b[0].length_mm >= c.crumb_mm]
    if long_pts:
        long_all = np.concatenate(long_pts)
    out: list[InkStroke] = []
    for stroke, rc in built:
        n = stroke.length_mm
        if len(built) > 1 and n < c.min_len_mm:
            continue
        if n < c.crumb_mm and long_pts:
            d = np.linalg.norm(stroke.mm[:, None] - long_all[None], axis=2).min(1)
            near = float(np.mean(d <= c.crumb_touch_mm))
            if near > 0 and near >= c.crumb_share:
                continue
        smoothed = smooth(resample(stroke, c.step_mm))
        wd = float(np.median(width[rc[:, 0].astype(int), rc[:, 1].astype(int)]))
        out.append(InkStroke(smoothed.t, smoothed.mm, max(wd, w)))
    if debug is not None:
        debug["stage_mm"]["chains"] = float(sum(b[0].length_mm for b in built))
        debug["stage_mm"]["strokes"] = float(
            sum(np.linalg.norm(np.diff(o.mm, axis=0), axis=1).sum() for o in out)
        )
    out.sort(key=lambda s: s.t[0])
    return out
