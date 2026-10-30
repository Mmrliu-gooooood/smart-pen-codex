"""Writing session: mode, target, finished strokes, export (Task 12).

Strokes are kept in page millimetres (u right, v up). Exports render them
cleanly: polylines smoothed by Chaikin corner cutting, round caps and joins,
one line width (``line_mm``). The PNG and SVG use page millimetres scaled to
pixels with v pointing down, cropped to the strokes plus a margin.

Two kinds of lines are kept: ``strokes`` from the tip path (order, timing,
count; used for scoring) and ``ink`` pieces vectorized from the ink the
camera saw (the true shape; digital_pen.strokes.inkvec). Display and export
use the ink when there is any.

``rotation`` (0, 90, 180 or 270 degrees, counter-clockwise) turns the view to
match how the sheet lies in front of the writer (e.g. 180 when the page is
upside down relative to its printed pattern). Strokes stay in page mm; the
exports apply the rotation and the JSON reports it for the browser.
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, field

import cv2
import numpy as np

MODES = ("practice", "free", "draw")
ROTATIONS = (0, 90, 180, 270)


def rotate(points: np.ndarray, degrees: int) -> np.ndarray:
    """Page mm turned counter-clockwise by a multiple of 90 degrees."""
    u, v = points[:, 0], points[:, 1]
    turned = {0: (u, v), 90: (-v, u), 180: (-u, -v), 270: (v, -u)}[degrees]
    return np.column_stack(turned)


def chaikin(points: np.ndarray, rounds: int = 2) -> np.ndarray:
    """Corner-cutting smoothing of an open polyline (ends kept)."""
    pts = np.asarray(points, float)
    for _ in range(rounds):
        if len(pts) < 3:
            return pts
        q = 0.75 * pts[:-1] + 0.25 * pts[1:]
        r = 0.25 * pts[:-1] + 0.75 * pts[1:]
        mid = np.empty((2 * len(q), 2))
        mid[0::2], mid[1::2] = q, r
        pts = np.vstack((pts[:1], mid, pts[-1:]))
    return pts


@dataclass
class SessionStroke:
    id: int
    t0: float
    t1: float
    points: list[list[float]]  # page mm
    dt: list[float] = field(default_factory=list)  # per point, s after t0
    width_mm: float | None = None  # ink pieces: measured line width

    def as_dict(self) -> dict:
        out = {
            "id": self.id,
            "t0": self.t0,
            "t1": self.t1,
            "points": self.points,
            "dt": self.dt,
        }
        if self.width_mm is not None:
            out["width_mm"] = self.width_mm
        return out


@dataclass
class WritingSession:
    mode: str = "free"
    target: str | None = None
    strokes: list[SessionStroke] = field(default_factory=list)
    started_utc: str = ""
    finished: bool = False
    line_mm: float = 0.6
    rotation: int = 0
    ink: dict[int, SessionStroke] = field(default_factory=dict)
    generation: int = 0  # changes on start / clear (the engine resets its ink)
    scan: dict | None = None  # photo finalization: png + placement
    # the strokes of the tip path while ``strokes`` holds ones rebuilt from
    # the photo (None: ``strokes`` are the tip path's own)
    tip_strokes: list[SessionStroke] | None = None
    _next_id: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def start(
        self, mode: str = "free", target: str | None = None, rotation: int | None = None
    ) -> dict:
        if mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}")
        if rotation is not None and rotation not in ROTATIONS:
            raise ValueError(f"rotation must be one of {ROTATIONS}")
        with self._lock:
            self.mode, self.target = mode, target
            if rotation is not None:
                self.rotation = rotation
            self.strokes = []
            self.tip_strokes = None
            self.ink = {}
            self.scan = None
            self.generation += 1
            self.finished = False
            self.started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return self.summary()

    def set_rotation(self, rotation: int) -> dict:
        if rotation not in ROTATIONS:
            raise ValueError(f"rotation must be one of {ROTATIONS}")
        with self._lock:
            self.rotation = rotation
        return self.summary()

    def finish(self) -> dict:
        with self._lock:
            self.finished = True
        return self.summary()

    def add(self, t, mm) -> SessionStroke | None:
        """Add a finished stroke (times, (N, 2) page mm); ignored once finished."""
        with self._lock:
            if self.finished:
                return None
            stroke = self._make(self._next_id, t, mm)
            self._next_id += 1
            self.strokes.append(stroke)
            return stroke

    @staticmethod
    def _make(id_: int, t, mm) -> SessionStroke:
        t = np.asarray(t, float)
        pts = np.round(np.asarray(mm, float), 3).tolist()
        dt = np.round(t - t[0], 3).tolist() if len(t) == len(pts) else []
        return SessionStroke(
            id_, round(float(t[0]), 4), round(float(t[-1]), 4), pts, dt
        )

    def replace(self, id_: int, pieces) -> list[SessionStroke]:
        """Replace stroke ``id_`` by ``pieces`` [(t, mm), ...] (final ink
        correction); the pieces get new ids. Returns them."""
        with self._lock:
            k = next((i for i, s in enumerate(self.strokes) if s.id == id_), None)
            if k is None:
                return []
            new = []
            for t, mm in pieces:
                new.append(self._make(self._next_id, t, mm))
                self._next_id += 1
            self.strokes[k : k + 1] = new
            return new

    def undo(self) -> SessionStroke | None:
        with self._lock:
            return self.strokes.pop() if self.strokes else None

    def tip_path(self) -> list[tuple[np.ndarray, np.ndarray]]:
        """(times, page mm) of the tip path's strokes, even after they were
        replaced by strokes rebuilt from the photo."""
        with self._lock:
            strokes = self.strokes if self.tip_strokes is None else self.tip_strokes
            out = []
            for s in strokes:
                pts = np.asarray(s.points, float).reshape(-1, 2)
                if not len(pts):
                    continue
                t = (
                    s.t0 + np.asarray(s.dt, float)
                    if len(s.dt) == len(pts)
                    else np.linspace(s.t0, s.t1, len(pts))
                )
                out.append((t, pts))
            return out

    def use_photo_strokes(self, pieces) -> int:
        """Replace the strokes by ones rebuilt from the photo ([(t, mm), ...],
        writing order); the tip path's are kept so that a new photo is
        matched against them again. Returns how many."""
        with self._lock:
            if self.tip_strokes is None:
                self.tip_strokes = list(self.strokes)
            new = []
            for t, mm in pieces:
                new.append(self._make(self._next_id, t, mm))
                self._next_id += 1
            self.strokes = new
            return len(new)

    def clear(self) -> None:
        with self._lock:
            self.strokes = []
            self.tip_strokes = None
            self.ink = {}
            self.scan = None
            self.generation += 1

    def set_scan(self, scan, source: str) -> dict:
        """Store a scan.Scan of the finished writing; returns its metadata."""
        with self._lock:
            version = (self.scan or {}).get("version", 0) + 1
            self.scan = {
                "png": scan.png(),
                "gray": scan.on_white(),
                "box_mm": [round(float(v), 3) for v in scan.box_mm],
                "mm_per_px": scan.mm_per_px,
                "rms_px": round(scan.rms_px, 3),
                "source": source,
                "obstructed": bool(getattr(scan, "obstructed", False)),
                "version": version,
            }
            return self._scan_meta()

    def _scan_meta(self) -> dict | None:
        if self.scan is None:
            return None
        meta = {k: v for k, v in self.scan.items() if k not in ("png", "gray")}
        meta["url"] = f"/api/scan.png?v={self.scan['version']}"
        return meta

    def scan_centerlines(self, mm_per_px: float = 0.25) -> np.ndarray | None:
        """Centre-line points (page mm) of the ink in the scan, or None."""
        with self._lock:
            if self.scan is None:
                return None
            gray, box = self.scan["gray"], self.scan["box_mm"]
            src = self.scan["mm_per_px"]
        alpha = (255.0 - gray.astype(np.float32)) * 255 / 229
        f = src / mm_per_px
        small = cv2.resize(alpha, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
        from digital_pen.strokes.inkvec import thin

        rows, cols = np.nonzero(thin(small > 100))
        if not len(rows):
            return None
        u0, _, _, v1 = box
        return np.column_stack(
            (u0 + (cols + 0.5) * mm_per_px, v1 - (rows + 0.5) * mm_per_px)
        )

    def scan_png(self) -> bytes | None:
        with self._lock:
            return None if self.scan is None else self.scan["png"]

    def apply_ink(self, removed, added) -> dict | None:
        """Ink layer changes (ids, InkPiece-like with id/t/mm/width_mm).
        Returns the event for the page, or None (finished or no change)."""
        with self._lock:
            if self.finished or not (removed or added):
                return None
            for i in removed:
                self.ink.pop(i, None)
            new = []
            for piece in added:
                stroke = self._make(piece.id, piece.t, piece.mm)
                stroke.width_mm = round(float(piece.width_mm), 3)
                self.ink[piece.id] = stroke
                new.append(stroke.as_dict())
            return {"type": "ink", "remove": list(removed), "add": new}

    def summary(self) -> dict:
        return {
            "mode": self.mode,
            "target": self.target,
            "strokes": len(self.strokes),
            "started_utc": self.started_utc,
            "finished": self.finished,
            "rotation": self.rotation,
            "ink": len(self.ink),
            # "photo": strokes rebuilt from the final photo + tip path
            "stroke_source": "tip" if self.tip_strokes is None else "photo",
        }

    # -- export -----------------------------------------------------------------

    def to_json(self) -> dict:
        with self._lock:
            strokes = [s.as_dict() for s in self.strokes]
            ink = [s.as_dict() for s in sorted(self.ink.values(), key=lambda k: k.t0)]
            tip = (
                None
                if self.tip_strokes is None
                else [s.as_dict() for s in self.tip_strokes]
            )
        out = {
            "schema": "pen-session-v1",
            **self.summary(),
            "units": "page mm, v up",
            "strokes": strokes,
            "ink_strokes": ink,
            "scan": self._scan_meta(),
        }
        if tip is not None:  # the tip path's strokes, under rebuilt ones
            out["tip_strokes"] = tip
        return out

    def upright_polylines(self) -> list[np.ndarray]:
        """The drawing as smoothed polylines in mm, turned like the sheet
        (x right, y up): the ink pieces when there are any, else the strokes."""
        with self._lock:
            lines = list(self.ink.values()) or self.strokes
            return [
                rotate(chaikin(np.array(s.points)), self.rotation)
                for s in lines
                if s.points
            ]

    def _layout(self, margin_mm: float):
        polylines = self.upright_polylines()
        if not polylines:
            return polylines, np.zeros(2), np.array((10.0, 10.0))
        pts = np.concatenate(polylines)
        lo = pts.min(0) - margin_mm
        hi = pts.max(0) + margin_mm
        return polylines, lo, hi

    def to_svg(self, margin_mm: float = 3.0) -> str:
        polylines, lo, hi = self._layout(margin_mm)
        w, h = hi - lo
        paths = []
        for p in polylines:
            d = " ".join(f"{x - lo[0]:.2f},{hi[1] - y:.2f}" for x, y in p)
            paths.append(f'<polyline points="{d}"/>')
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{w:.1f}mm" height="{h:.1f}mm" viewBox="0 0 {w:.2f} {h:.2f}">'
            f'<g fill="none" stroke="#1a1a1a" stroke-width="{self.line_mm}" '
            'stroke-linecap="round" stroke-linejoin="round">'
            + "".join(paths)
            + "</g></svg>"
        )

    def to_png(self, px_per_mm: float = 12.0, margin_mm: float = 3.0) -> bytes:
        with self._lock:
            gray = None if self.scan is None else self.scan["gray"]
        if gray is not None:  # the photo of the real ink, turned like the sheet
            ok, data = cv2.imencode(".png", np.rot90(gray, self.rotation // 90))
            if not ok:
                raise RuntimeError("PNG encoding failed")
            return data.tobytes()
        return self._strokes_png(px_per_mm, margin_mm)

    def _strokes_png(self, px_per_mm: float, margin_mm: float) -> bytes:
        polylines, lo, hi = self._layout(margin_mm)
        w, h = np.ceil((hi - lo) * px_per_mm).astype(int)
        image = np.full((max(h, 1), max(w, 1), 3), 255, np.uint8)
        width = max(1, int(round(self.line_mm * px_per_mm)))
        for p in polylines:
            q = np.column_stack(
                ((p[:, 0] - lo[0]) * px_per_mm, (hi[1] - p[:, 1]) * px_per_mm)
            )
            cv2.polylines(
                image,
                [np.rint(q * 16).astype(np.int32)],
                False,
                (26, 26, 26),
                width,
                cv2.LINE_AA,
                shift=4,
            )
        ok, data = cv2.imencode(".png", image)
        if not ok:
            raise RuntimeError("PNG encoding failed")
        return data.tobytes()

    def to_json_bytes(self) -> bytes:
        return json.dumps(self.to_json(), ensure_ascii=False).encode("utf-8")
