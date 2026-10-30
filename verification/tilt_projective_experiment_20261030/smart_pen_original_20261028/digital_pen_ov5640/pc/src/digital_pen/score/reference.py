"""Standard strokes of a character (Make Me a Hanzi medians, Task 14).

The glyph data (``hanzi/<char>.json``, the same data Hanzi Writer draws;
Arphic Public License, see hanzi/ARPHICPL.TXT) gives each stroke's centre
line in writing order and direction, in a 1024 em box with y up (top 900,
bottom -124). Here they become unit-box polylines (x right, y up, 0..1),
resampled evenly, with a plain stroke name from their shape.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parent / "hanzi"


@dataclass(frozen=True)
class RefStroke:
    index: int  # 0-based, writing order
    points: np.ndarray  # (n, 2) unit box, writing direction
    name: str  # 横 竖 撇 捺 点 提, 横折 竖钩 ...

    @property
    def length(self) -> float:
        return float(np.sum(np.linalg.norm(np.diff(self.points, axis=0), axis=1)))


@dataclass(frozen=True)
class Reference:
    char: str
    strokes: tuple[RefStroke, ...]

    @property
    def points(self) -> np.ndarray:
        return np.concatenate([s.points for s in self.strokes])


def resample(points: np.ndarray, n: int) -> np.ndarray:
    """``n`` points evenly spaced along a polyline."""
    p = np.asarray(points, float)
    seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
    s = np.concatenate(([0.0], np.cumsum(seg)))
    if s[-1] <= 1e-9:
        return np.repeat(p[:1], n, axis=0)
    grid = np.linspace(0, s[-1], n)
    return np.column_stack([np.interp(grid, s, p[:, k]) for k in range(2)])


def _direction_name(d: np.ndarray, length: float) -> str:
    a = np.degrees(np.arctan2(d[1], d[0]))  # 0 = right, -90 = down (y up)
    if length < 0.12:
        return "点"
    if -25 <= a <= 25:
        return "横"
    if 25 < a < 80:
        return "提"
    if d[1] < 0:  # downward: drift left = 撇, straight = 竖, right = 捺
        r = d[0] / -d[1]
        if r < -0.25:
            return "撇"
        if r <= 0.45:
            return "竖"
        return "捺"
    return "撇" if d[0] < 0 else "提"


def stroke_name(points: np.ndarray) -> str:
    """A plain name from the centre line (y up): 横 竖 撇 捺 点 提, or a
    fold (横折, 竖折, ...) / hook (竖钩, ...) after its first part."""
    p = resample(np.asarray(points, float), 32)
    length = float(np.sum(np.linalg.norm(np.diff(p, axis=0), axis=1)))
    if length < 1e-6:
        return "点"
    # turning measured over a short window (a corner is often spread over
    # two or three median segments)
    w = 3
    turn = np.zeros(len(p))
    for i in range(w, len(p) - w):
        a, b = p[i] - p[i - w], p[i + w] - p[i]
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        if na > 1e-9 and nb > 1e-9:
            turn[i] = np.degrees(np.arccos(np.clip(a @ b / (na * nb), -1, 1)))
    k = int(np.argmax(turn))
    if turn[k] > 60:
        head = _direction_name(p[k] - p[0], 1.0)
        f = k / (len(p) - 1)
        if f > 0.8:
            return head + "钩"
        if f > 0.12:
            return head + "折"
    return _direction_name(p[-1] - p[0], length)


@lru_cache(maxsize=256)
def load(char: str, n: int = 24) -> Reference:
    """The character's standard strokes; KeyError if not bundled."""
    path = DATA / f"{char}.json"
    if not path.exists():
        raise KeyError(f"no glyph data for {char!r}")
    data = json.loads(path.read_text(encoding="utf-8"))
    strokes = []
    for k, median in enumerate(data["medians"]):
        m = np.asarray(median, float)
        unit = np.column_stack((m[:, 0] / 1024.0, (m[:, 1] + 124.0) / 1024.0))
        strokes.append(RefStroke(k, resample(unit, n), stroke_name(unit)))
    return Reference(char, tuple(strokes))


def available() -> list[str]:
    return sorted(p.stem for p in DATA.glob("*.json"))
