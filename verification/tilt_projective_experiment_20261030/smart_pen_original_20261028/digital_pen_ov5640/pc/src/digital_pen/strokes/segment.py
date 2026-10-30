"""Pen-down / pen-up segmentation of a tip trail into strokes (Task 11).

Each trail point carries ink evidence (darkening after the tip left, nan if
unknown). Two consecutive points are *linked* when new ink connects them:
along the straight path between them (searched ``link_reach_mm`` to either
side, so gentle curves pass), at least ``link_share`` of the samples show
ink that appeared between the two visits (older ink, e.g. a stroke being
crossed, does not count). Very short steps are judged by the point
evidence instead. Without a canvas, links fall back to time: a gap of up to
``bridge_s`` between clear points is bridged.

A stroke is a maximal chain of linked points that contains at least one
point with clear ink (``down``). The tip is often hidden for a few frames
(fingers, motion), so consecutive points can be millimetres apart; the link
test is what tells "pen stayed down while unseen" (ink between them) from
"pen lifted and moved" (no ink between them).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass(frozen=True)
class SegmenterConfig:
    down: float = 0.06
    up: float = 0.03
    bridge_s: float = 0.15
    lead_s: float = 0.15
    min_points: int = 3
    min_length_mm: float = 1.0
    # Ink links between consecutive points.
    link_step_mm: float = 0.4
    link_reach_mm: float = 0.6
    link_share: float = 0.7
    link_min_mm: float = 0.8
    link_ink: float = 0.08
    link_before_s: float = 0.3
    link_after_s: float = 1.5
    # A point with clearly no new ink breaks the chain even when ink lies
    # along the path (a pen-up move retracing a stroke just written).
    break_on_up: bool = True
    # Runs over old ink at least this long count as pen-up retraces.
    retrace_mm: float = 2.5


@dataclass
class Stroke:
    t: np.ndarray  # (N,) seconds
    mm: np.ndarray  # (N, 2) page mm (u right, v up)
    evidence: np.ndarray = field(default_factory=lambda: np.zeros(0))

    @property
    def length_mm(self) -> float:
        if len(self.mm) < 2:
            return 0.0
        return float(np.sum(np.linalg.norm(np.diff(self.mm, axis=0), axis=1)))


def classify(evidence: float, config: SegmenterConfig, old_ink: bool = False) -> str:
    """'D' clear ink, 'U' clearly none, 'W' weak, 'N' unknown.

    On ink written earlier no new ink can show: "none" there is undecided.
    """
    if not np.isfinite(evidence):
        return "N"
    if evidence >= config.down:
        return "D"
    if evidence <= config.up:
        return "N" if old_ink else "U"
    return "W"


def ink_link(
    canvas, a, b, t_a: float, t_b: float, config: SegmenterConfig, new=None
) -> float:
    """Share of the path a->b (page mm) over ink that appeared in the interval.

    Ink counts as fresh only where the spot was last seen ink-free at or
    after ``t_a - link_before_s`` (the canvas ``clear`` time): ink written
    earlier but first seen later (the hand covered it) is not fresh. Path
    samples on such older ink (also a stroke being crossed) show nothing new
    and are left out; nan when no sample can be judged.
    """
    a, b = np.asarray(a, float), np.asarray(b, float)
    length = float(np.hypot(*(b - a)))
    count = max(2, int(np.ceil(length / config.link_step_mm)) + 1)
    pts = a + np.linspace(0.0, 1.0, count)[:, None] * (b - a)
    if count > 2:
        pts = pts[1:-1]
    new = canvas.new_ink() if new is None else new
    lo, hi = t_a - config.link_before_s, t_b + config.link_after_s
    hits = judged = 0
    for q in pts:
        box = canvas.window(q, config.link_reach_mm)
        if box is None:
            continue
        inked, clear = canvas.inked[box], canvas.clear[box]
        ink = new[box] > config.link_ink
        fresh = bool(((clear >= lo) & (inked <= hi) & ink).any())
        old = bool(((clear < lo) & ink).any())
        if fresh:
            hits += 1
            judged += 1
        elif not old:
            judged += 1
    return hits / judged if judged else float("nan")


def segment(points, config: SegmenterConfig | None = None, canvas=None) -> list[Stroke]:
    """Strokes from trail points (objects with t, mm, evidence), time order."""
    c = config or SegmenterConfig()
    if not points:
        return []
    t = np.array([p.t for p in points], float)
    mm = np.array([p.mm for p in points], float).reshape(-1, 2)
    ev = np.array([p.evidence for p in points], float)
    states = [
        classify(e, c, getattr(p, "old_ink", False))
        for e, p in zip(ev, points, strict=True)
    ]
    n = len(t)
    if canvas is None:
        return _segment_by_time(t, mm, ev, states, c)
    # A long run over old ink without fresh ink is a pen-up move retracing a
    # stroke (moving to the next stroke's start in 口/日/田); a crossing is
    # only about a line width long.
    old = [
        getattr(p, "old_ink", False) and s != "D"
        for p, s in zip(points, states, strict=True)
    ]
    k = 0
    while k < n:
        if not old[k]:
            k += 1
            continue
        end = k
        while end + 1 < n and old[end + 1]:
            end += 1
        run = float(np.sum(np.linalg.norm(np.diff(mm[k : end + 1], axis=0), axis=1)))
        if run >= c.retrace_mm:
            for j in range(k, end + 1):
                states[j] = "U"
        k = end + 1
    linked = np.zeros(max(0, n - 1), bool)
    new = canvas.new_ink()
    for k in range(n - 1):
        step = float(np.hypot(*(mm[k + 1] - mm[k])))
        clear_up = "U" in (states[k], states[k + 1])
        if step < c.link_min_mm:
            # Too short to judge the path: linked unless either end is
            # clearly without ink.
            linked[k] = not clear_up
        elif c.break_on_up and clear_up:
            linked[k] = False
        else:
            share = ink_link(canvas, mm[k], mm[k + 1], t[k], t[k + 1], c, new)
            # Only old ink along the path (a crossing): judge by the ends.
            if np.isnan(share):
                # Only older ink along the path: a short step is a crossing
                # (judge by the ends), a long one a pen-up retrace.
                linked[k] = (not clear_up) and step < c.retrace_mm
            else:
                linked[k] = share >= c.link_share
    strokes, start = [], 0
    for k in range(n):
        if k == n - 1 or not linked[k]:
            chain = slice(start, k + 1)
            if any(s == "D" for s in states[chain]):
                stroke = Stroke(t[chain], mm[chain], ev[chain])
                if (
                    len(stroke.t) >= c.min_points
                    and stroke.length_mm >= c.min_length_mm
                ):
                    strokes.append(stroke)
            start = k + 1
    return strokes


def _segment_by_time(t, mm, ev, states, c: SegmenterConfig) -> list[Stroke]:
    down = [k for k, s in enumerate(states) if s == "D"]
    runs = []
    for k in down:
        if runs and t[k] - t[runs[-1][1]] <= c.bridge_s:
            runs[-1][1] = k
        else:
            runs.append([k, k])
    strokes = []
    previous_end = -1
    for a, b in runs:
        # Extend over undecided points (never over clear "no ink"), at most
        # lead_s beyond the first / last clear point.
        first, last = t[a], t[b]
        while (
            a - 1 > previous_end
            and states[a - 1] in "NW"
            and first - t[a - 1] <= c.lead_s
        ):
            a -= 1
        while b + 1 < len(t) and states[b + 1] in "NW" and t[b + 1] - last <= c.lead_s:
            b += 1
        previous_end = b
        stroke = Stroke(t[a : b + 1], mm[a : b + 1], ev[a : b + 1])
        if len(stroke.t) >= c.min_points and stroke.length_mm >= c.min_length_mm:
            strokes.append(stroke)
    return strokes
