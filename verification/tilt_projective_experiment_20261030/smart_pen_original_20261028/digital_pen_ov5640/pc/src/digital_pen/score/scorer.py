"""Local stroke scoring (Task 14): offline, explainable, deterministic.

The pen's strokes come from the tip path, whose splitting at pen lifts is
not reliable yet (Task 11: lifts inside compact characters get merged; a
pen-down sensor will fix that). So the scoring does not trust the user's
stroke boundaries. It takes the pen-down path in time order and finds, for
every standard stroke, the stretch of that path that matches it best
(subsequence DTW, both directions). From those matches:

  shape      50  per standard stroke, mean distance of its match (unit box);
                 a stroke with no good match counts as missing
  structure  20  layout (distances between the strokes' centres) and the
                 character's proportions, against the standard
  order      15  writing order from the matched stretches' times
  direction  10  each stroke written in its standard direction
  count       5  number of strokes (for reference until the pen-down sensor)

plus a list of per-stroke problems in plain words. When the final photo of
the ink is available (``ink_points``: its centre lines), shape and structure
come from the real ink instead (a stroke the tip path lost but the paper
shows is not "missing"); order and direction always come from the timed
tip path. Coordinates: the
standard is a unit box (x right, y up); the writing (page mm, rotated by
the caller so that up is the writer's up) is fitted to it by translation
and one scale.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

import numpy as np

from digital_pen.score.reference import Reference, load

WEIGHTS = {"shape": 50, "structure": 20, "order": 15, "direction": 10, "count": 5}
GOOD, MISSING = 0.025, 0.12  # mean match distance (unit box): perfect / missing
INK_GOOD, INK_MISSING = 0.02, 0.09  # same for the nearest real ink
MAX_POINTS = 240  # the pen path is thinned to at most this many points


@dataclass
class StrokeResult:
    index: int  # 1-based, standard order
    name: str
    matched: bool
    error: float  # mean distance of the match, unit box
    reversed: bool
    length_ratio: float  # matched stretch length / standard length
    start_t: float | None  # when the matched stretch was written


@dataclass
class ScoreResult:
    char: str
    score: int  # 0..100
    parts: dict[str, float]  # each 0..1
    strokes: list[StrokeResult] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    user_strokes: int = 0
    standard_strokes: int = 0
    count_reliable: bool = False
    shape_from: str = "path"  # "ink": shape and structure from the photo

    def as_dict(self) -> dict:
        return asdict(self)


# -- helpers --------------------------------------------------------------------------


def _pen_path(strokes) -> tuple[np.ndarray, np.ndarray]:
    """Pen-down points in time order (N, 2) and their times (N,)."""
    pts, ts = [], []
    for t, mm in sorted(strokes, key=lambda s: float(np.asarray(s[0])[0])):
        mm = np.asarray(mm, float).reshape(-1, 2)
        t = np.asarray(t, float).reshape(-1)
        if len(t) != len(mm):
            t = np.linspace(t[0], t[-1], len(mm))
        pts.append(mm)
        ts.append(t)
    if not pts:
        return np.zeros((0, 2)), np.zeros(0)
    p, t = np.concatenate(pts), np.concatenate(ts)
    if len(p) > MAX_POINTS:
        k = np.linspace(0, len(p) - 1, MAX_POINTS).round().astype(int)
        p, t = p[k], t[k]
    return p, t


def _fit(user: np.ndarray, ref: np.ndarray, rounds: int = 4) -> np.ndarray:
    """User points mapped onto the standard (translation + one scale)."""
    lo, hi = user.min(0), user.max(0)
    rlo, rhi = ref.min(0), ref.max(0)
    s = max(rhi - rlo) / max(float(max(hi - lo)), 1e-6)
    u = (user - (lo + hi) / 2) * s + (rlo + rhi) / 2
    for _ in range(rounds):
        d = np.linalg.norm(ref[:, None] - u[None], axis=2)
        j = d.argmin(1)
        keep = d[np.arange(len(ref)), j] <= np.quantile(d.min(1), 0.8)
        a, b = u[j[keep]], ref[keep]
        am, bm = a.mean(0), b.mean(0)
        var = float(((a - am) ** 2).sum())
        if var < 1e-9:
            break
        k = float(((a - am) * (b - bm)).sum()) / var
        k = float(np.clip(k, 0.7, 1.4))
        u = (u - am) * k + bm
    return u


def _subsequence_dtw(ref: np.ndarray, user: np.ndarray):
    """Best stretch of ``user`` matching all of ``ref``: (mean distance,
    user index of each ref point)."""
    c = np.linalg.norm(ref[:, None] - user[None], axis=2)
    n, m = c.shape
    d = np.empty((n, m))
    d[0] = c[0]  # free start anywhere on the user path
    for i in range(1, n):
        prev = d[i - 1]
        diag = np.concatenate(([np.inf], prev[:-1]))
        best = np.minimum(prev, diag)
        row = d[i]
        row[0] = c[i, 0] + best[0]
        for j in range(1, m):
            row[j] = c[i, j] + min(best[j], row[j - 1])
    j = int(np.argmin(d[-1]))  # free end
    path = [(n - 1, j)]
    i = n - 1
    while i > 0 or (i == 0 and False):
        if i == 0:
            break
        options = [(d[i - 1, j], i - 1, j)]
        if j > 0:
            options += [(d[i - 1, j - 1], i - 1, j - 1), (d[i, j - 1], i, j - 1)]
        _, i, j = min(options)
        path.append((i, j))
    path.reverse()
    cost = np.mean([c[a, b] for a, b in path])
    idx = np.zeros(n, int)
    for a, b in path:
        idx[a] = b  # last user point matched to each ref point
    return float(cost), idx


def _length(p: np.ndarray) -> float:
    return (
        float(np.sum(np.linalg.norm(np.diff(p, axis=0), axis=1))) if len(p) > 1 else 0.0
    )


# -- scoring --------------------------------------------------------------------------


def score(
    char: str, strokes, reference: Reference | None = None, ink_points=None
) -> ScoreResult:
    """Score the writing of ``char``. ``strokes``: [(times, (N, 2) mm), ...],
    oriented so that +v is up for the writer; ``ink_points``: (M, 2) mm
    centre-line points of the real ink in the same frame (optional)."""
    ref = reference or load(char)
    n_ref = len(ref.strokes)
    path, times = _pen_path(strokes)
    result = ScoreResult(char, 0, dict.fromkeys(WEIGHTS, 0.0), standard_strokes=n_ref)
    result.user_strokes = sum(1 for _ in strokes)
    if len(path) < 3:
        result.issues.append("没有可评的笔迹。")
        return result
    u = _fit(path, ref.points)
    matches = []
    for rs in ref.strokes:
        fwd, idx_f = _subsequence_dtw(rs.points, u)
        rev, idx_r = _subsequence_dtw(rs.points[::-1], u)
        # reversed only when the forward match is poor and the reverse much
        # better: a pen-up move back along a stroke (still in the path while
        # lifts are merged) matches the reversed stroke too
        reverse = fwd > 2 * GOOD and rev < 0.7 * fwd and rs.length > 0.1
        cost, idx = (rev, idx_r[::-1]) if reverse else (fwd, idx_f)
        a, b = int(idx.min()), int(idx.max())
        matched = cost <= MISSING
        seg = u[a : b + 1]
        matches.append((rs, cost, reverse, idx, matched, seg))
        result.strokes.append(
            StrokeResult(
                rs.index + 1,
                rs.name,
                bool(matched),
                round(cost, 4),
                bool(reverse and matched),
                round(_length(seg) / max(rs.length, 1e-6), 3) if matched else 0.0,
                round(float(times[a]), 3) if matched else None,
            )
        )
    good = [m for m in matches if m[4]]
    ink = None if ink_points is None else np.asarray(ink_points, float).reshape(-1, 2)
    if ink is not None and len(ink) >= 10:
        _ink_shape(result, ref, ink, matches)
        return _finish(result, ref, matches, times, *_ink_parts(ref, ink))
    # shape
    per = [
        float(np.clip(1 - (m[1] - GOOD) / (MISSING - GOOD), 0, 1)) if m[4] else 0.0
        for m in matches
    ]
    shape = float(np.mean(per))
    covered = np.zeros(len(u), bool)
    for m in good:
        covered[int(m[3].min()) : int(m[3].max()) + 1] = True
    near_ref = np.linalg.norm(u[:, None] - ref.points[None], axis=2).min(1) <= 0.08
    extra = float(np.mean(~covered & ~near_ref))
    if extra > 0.2:
        shape *= 1 - 0.5 * (extra - 0.2)
    # structure: layout between stroke centres, and proportions
    if len(good) >= 2:
        uc = np.array([m[5].mean(0) for m in good])
        rc = np.array([m[0].points.mean(0) for m in good])
        du = np.linalg.norm(uc[:, None] - uc[None], axis=2)
        dr = np.linalg.norm(rc[:, None] - rc[None], axis=2)
        layout = float(np.clip(1 - np.abs(du - dr).mean() * 2 / 0.12, 0, 1))
    else:
        layout = 1.0 if good else 0.0
    aspect, tall = _aspect(u, ref)
    return _finish(result, ref, matches, times, shape, layout, aspect, tall, extra)


def _aspect(u: np.ndarray, ref: Reference) -> tuple[float, bool]:
    uw, uh = np.ptp(u, axis=0) + 1e-3
    rw, rh = np.ptp(ref.points, axis=0) + 1e-3
    aspect = float(np.clip(1 - abs(np.log((uh / uw) / (rh / rw))) / 0.6, 0, 1))
    return aspect, bool((uh / uw) > (rh / rw))


def _ink_shape(result: ScoreResult, ref: Reference, ink: np.ndarray, matches) -> None:
    """Per-stroke errors from the real ink (nearest centre-line points)."""
    v = _fit(ink, ref.points)
    result.shape_from = "ink"
    for s, rs in zip(result.strokes, ref.strokes, strict=True):
        d = np.linalg.norm(rs.points[:, None] - v[None], axis=2).min(1)
        err = float(d.mean())
        s.error = round(err, 4)
        s.matched = bool(err <= INK_MISSING)


def _ink_parts(ref: Reference, ink: np.ndarray):
    v = _fit(ink, ref.points)
    errs, cents = [], []
    for rs in ref.strokes:
        d = np.linalg.norm(rs.points[:, None] - v[None], axis=2)
        j = d.argmin(1)
        errs.append(float(d[np.arange(len(rs.points)), j].mean()))
        cents.append(v[j].mean(0))
    per = [
        float(np.clip(1 - (e - INK_GOOD) / (INK_MISSING - INK_GOOD), 0, 1))
        if e <= INK_MISSING
        else 0.0
        for e in errs
    ]
    shape = float(np.mean(per))
    far = np.linalg.norm(v[:, None] - ref.points[None], axis=2).min(1) > 0.08
    extra = float(far.mean())
    if extra > 0.2:
        shape *= 1 - 0.5 * (extra - 0.2)
    ok = [k for k, e in enumerate(errs) if e <= INK_MISSING]
    if len(ok) >= 2:
        uc, rc = (
            np.array([cents[k] for k in ok]),
            np.array([ref.strokes[k].points.mean(0) for k in ok]),
        )
        du = np.linalg.norm(uc[:, None] - uc[None], axis=2)
        dr = np.linalg.norm(rc[:, None] - rc[None], axis=2)
        layout = float(np.clip(1 - np.abs(du - dr).mean() * 2 / 0.12, 0, 1))
    else:
        layout = 1.0 if ok else 0.0
    aspect, tall = _aspect(v, ref)
    return shape, layout, aspect, tall, extra


def _finish(result, ref, matches, times, shape, layout, aspect, tall, extra):
    n_ref = len(ref.strokes)
    good = [m for m in matches if m[4]]
    structure = 0.6 * layout + 0.4 * aspect
    # order and direction (always from the timed tip path)
    starts = [(m[0].index, float(times[int(m[3].min())])) for m in good]
    pairs = [(a, b) for i, a in enumerate(starts) for b in starts[i + 1 :]]
    wrong = [(a, b) for a, b in pairs if a[1] > b[1]]
    order = 1 - len(wrong) / len(pairs) if pairs else (1.0 if good else 0.0)
    dirs = [m for m in good if m[0].length > 0.1]
    direction = (
        1 - sum(m[2] for m in dirs) / len(dirs) if dirs else (1.0 if good else 0.0)
    )
    count = max(0.0, 1 - abs(result.user_strokes - n_ref) / n_ref)
    result.parts = {
        "shape": round(shape, 3),
        "structure": round(structure, 3),
        "order": round(order, 3),
        "direction": round(direction, 3),
        "count": round(count, 3),
    }
    result.score = int(round(sum(WEIGHTS[k] * result.parts[k] for k in WEIGHTS)))
    # problems in plain words, most important first
    issues = result.issues
    for s in result.strokes:
        label = f"第{s.index}笔（{s.name}）"
        if not s.matched:
            issues.append(f"{label}没有找到，可能漏写了或写得太偏。")
    shown = set()
    for a, b in sorted(wrong, key=lambda p: (p[1][0], p[0][0])):
        if b[0] in shown:
            continue
        shown.add(b[0])
        sa, sb = result.strokes[a[0]], result.strokes[b[0]]
        issues.append(
            f"笔顺：第{sb.index}笔（{sb.name}）写早了，应在第{sa.index}笔（{sa.name}）之后。"
        )
    for s in result.strokes:
        if s.reversed:
            issues.append(f"第{s.index}笔（{s.name}）方向反了。")
    for s in result.strokes:
        big = 0.05 if result.shape_from == "ink" else 0.06
        if s.matched and s.error > big:
            issues.append(f"第{s.index}笔（{s.name}）位置或形状偏差较大。")
        elif s.matched and s.length_ratio < 0.6:
            issues.append(f"第{s.index}笔（{s.name}）写短了。")
        elif s.matched and s.length_ratio > 1.7:
            issues.append(f"第{s.index}笔（{s.name}）写长了。")
    if aspect < 0.6:
        issues.append("整体偏" + ("瘦长" if tall else "扁宽") + "，注意字的比例。")
    if extra > 0.2:
        issues.append("有多出来的笔迹（也可能是抬笔时笔尖贴着纸）。")
    if result.user_strokes != n_ref:
        issues.append(
            f"笔画数 {result.user_strokes}，标准 {n_ref}（抬笔判断还不准，仅供参考）。"
        )
    if not issues:
        issues.append("写得很规范。")
    return result
