"""The pen engine: TRACK stream events in, tips and strokes out (Task 12).

``Engine.on_event(kind, image, metadata)`` runs one stream event through the
whole chain and returns output events (plain dicts, ready for JSON):

  tip      every ROI frame: tip in page mm (or null), track status, frame
           time (device clock) and frame id
  stroke   a finished stroke (page mm, settled: ink confirmed, snapped to
           the ink, resampled); added to the session
  ink      ink pieces vectorized from the canvas (the true shape: what the
           page draws), as {remove: [ids], add: [pieces]}; every
           ``ink_interval_s`` over the tip runs that settled, and again
           ``ink_late_s`` later for ink the hand uncovered late
  open     every ``stroke_interval_s``: strokes still being written (raw)
  page     page snapshot check results (moved / pending / unknown)
  session  the whole session again after ``finalize_session`` re-cut it
  health   every ``health_interval_s``: rates, processing time, drops,
           paper and track status

ROI commands for the device collect in ``roi_requests``, snapshot requests
(after an unconfirmed page jump) in ``snap_requests``. The engine itself is
single-threaded and deterministic: replaying the same events gives the same
outputs. In live use the caller may run ``check_page`` in a worker thread
(``sync_pages=False``); the page model state is thread-safe.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field

import cv2
import numpy as np

from digital_pen.engine.session import WritingSession, rotate
from digital_pen.pose import PageLayout, PageLocatorConfig
from digital_pen.scan import PHOTO, scan_page
from digital_pen.score import score
from digital_pen.score.feedback import local_feedback
from digital_pen.strokes import StrokeTracker, StrokeTrackerConfig
from digital_pen.strokes.inkvec import InkLayer, InkVectorConfig
from digital_pen.strokes.photo import reconstruct
from digital_pen.strokes.post import split_on_ink
from digital_pen.strokes.segment import Stroke
from digital_pen.tip import (
    COARSE_MODEL_PATH,
    PageMapper,
    TipDetector,
    TipPipeline,
    TipTracker,
    TrackerConfig,
)


@dataclass
class EngineConfig:
    roi_size: int = 128
    sensor_size: tuple[int, int] = (800, 600)
    spacing_px: float = 9.3
    stroke_interval_s: float = 0.25
    health_interval_s: float = 1.0
    strokes: StrokeTrackerConfig = field(
        default_factory=lambda: StrokeTrackerConfig(
            keep_epochs=False, keep_trail=False, ink_split=True
        )
    )
    # Ink-vectorized shapes (strokes/inkvec.py): off by default. On small,
    # dense writing the ink is only 1-2 camera pixels wide and the pieces
    # come out more fragmented than the tip path (artifacts/ink-vector-2026-10).
    ink: InkVectorConfig | None = None
    ink_interval_s: float = 1.0
    ink_late_s: float = 5.0


class Health:
    """Rolling statistics over the last ``window`` ROI frames."""

    def __init__(self, window: int = 200):
        self.proc_ms = deque(maxlen=window)
        self.frame_t = deque(maxlen=window)
        self.age_ms = deque(maxlen=window)
        self.frames = 0
        self.found = deque(maxlen=window)
        self.dropped = 0
        self.page = {"checks": 0, "moved": 0, "pending": 0, "unknown": 0}

    def roi(self, t: float, proc_ms: float, found: bool, age_us=None) -> None:
        self.frames += 1
        self.frame_t.append(t)
        self.proc_ms.append(proc_ms)
        self.found.append(found)
        if age_us is not None:
            self.age_ms.append(age_us / 1e3)

    def report(self, status: str, relocations: int, slip_px) -> dict:
        span = self.frame_t[-1] - self.frame_t[0] if len(self.frame_t) > 1 else 0.0
        proc = np.array(self.proc_ms) if self.proc_ms else np.zeros(1)
        return {
            "type": "health",
            "fps": round((len(self.frame_t) - 1) / span, 2) if span > 0 else None,
            "proc_ms_p50": round(float(np.median(proc)), 2),
            "proc_ms_p95": round(float(np.percentile(proc, 95)), 2),
            "device_age_ms_p95": round(float(np.percentile(self.age_ms, 95)), 1)
            if self.age_ms
            else None,
            "tip_found": round(float(np.mean(self.found)), 3) if self.found else None,
            "frames": self.frames,
            "dropped": self.dropped,
            "track": status,
            "page": dict(self.page, relocations=relocations),
            "slip_px": [round(float(v), 2) for v in slip_px],
        }


def writing_box(lines, low: float = 3.0, high: float = 97.0):
    """Page-mm box of the writing, ignoring the few far-off points of a
    stray stroke (percentiles); None without lines."""
    if not lines:
        return None
    pts = np.concatenate([np.asarray(p, float).reshape(-1, 2) for p in lines])
    lo, hi = np.percentile(pts, low, axis=0), np.percentile(pts, high, axis=0)
    return (float(lo[0]), float(lo[1]), float(hi[0]), float(hi[1]))


def near_path(points: np.ndarray, path_rotated, rotation: int, reach_mm: float):
    """``points`` (page mm, not rotated) within ``reach_mm`` of the pen path
    (given rotated by ``rotation``)."""
    path = np.concatenate([np.asarray(p, float) for p in path_rotated])
    path = rotate(path, (360 - rotation) % 360)  # back to page mm
    step = 0.5
    lo = path.min(0) - reach_mm - 1
    shape = tuple(np.ceil((path.max(0) + reach_mm + 1 - lo) / step).astype(int) + 1)
    grid = np.zeros((shape[1], shape[0]), np.uint8)
    q = np.rint((path - lo) / step).astype(int)
    grid[q[:, 1], q[:, 0]] = 1
    r = int(np.ceil(reach_mm / step))
    grid = cv2.dilate(
        grid, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1,) * 2)
    )
    k = np.rint((points - lo) / step).astype(int)
    inside = (
        (k[:, 0] >= 0) & (k[:, 0] < shape[0]) & (k[:, 1] >= 0) & (k[:, 1] < shape[1])
    )
    keep = np.zeros(len(points), bool)
    keep[inside] = grid[k[inside, 1], k[inside, 0]] > 0
    return points[keep]


class Engine:
    def __init__(
        self,
        layout: PageLayout,
        full_frame: np.ndarray,
        config: EngineConfig | None = None,
        *,
        detector: TipDetector | None = None,
        coarse_detector: TipDetector | None = None,
        sync_pages: bool = True,
        clock=time.perf_counter,
    ):
        self.config = c = config or EngineConfig()
        self.mapper = PageMapper(
            # more seed tries: on a written sheet the first seeds can land
            # on ink (the locator stops at the first that decodes)
            layout,
            PageLocatorConfig(expected_spacing_px=c.spacing_px, seed_attempts=12),
        )
        self.mapper.locate(full_frame)
        w, h = c.sensor_size
        self.pipeline = TipPipeline(
            detector or TipDetector(),
            TipTracker(
                TrackerConfig(roi_size=(c.roi_size, c.roi_size), sensor_size=(w, h))
            ),
            self.mapper,
            coarse_detector=coarse_detector or TipDetector(model=COARSE_MODEL_PATH),
            sensor_size=(w, h),
        )
        self.strokes = StrokeTracker(c.strokes)
        self.session = WritingSession()
        self.health = Health()
        self.sync_pages = sync_pages
        self.clock = clock
        self.roi_requests: list[tuple[int, int, int, int]] = []
        self.snap_requests = 0
        self._relocations = self.mapper.relocations
        self._last_t = None
        self._next_strokes = None
        self._next_health = None
        self.ink = InkLayer(c.ink) if c.ink is not None else None
        self._ink_next = None
        self._ink_cut = [-np.inf, -np.inf]  # settled pass, late pass
        self._session_gen = self.session.generation
        # live (sync_pages=False): ink areas are vectorized in a worker; the
        # service takes the prepared jobs from here and calls commit_ink
        self.ink_jobs: list[dict] = []
        self.last_page_image: np.ndarray | None = None  # scan fallback
        # canvases of page models just replaced: ink the hand still covered
        # at the switch is vectorized once more, ink_late_s later
        self._retired: list[tuple[float, object, float, float]] = []

    def page_info(self) -> dict:
        """Printed page geometry for the browser (page mm, u right, v up)."""
        layout = self.mapper.layout
        rows, cols = layout.shape
        s = layout.spacing_mm
        return {
            "id": layout.page_id,
            "printed_mm": [
                0.0,
                0.0,
                round((cols - 1) * s, 3),
                round((rows - 1) * s, 3),
            ],
            "spacing_mm": s,
        }

    def finalize_session(self) -> int:
        """Final ink correction when writing ends: re-cut the session strokes
        of the current page model against the latest ink (the hand has moved
        away by now, so the whole sheet has been seen). Strokes from earlier
        page models are left alone: their ink is old ink to the new canvas.
        The ink pieces of the current page model are vectorized again too.
        Returns how many strokes and ink pieces changed. Call from the engine
        thread."""
        changed = 0
        if self.ink is not None and self._last_t is not None:
            for event in self._ink_pass(
                self.ink.since, np.inf, self._last_t + 1.0, inline=True
            ):
                changed += len(event["remove"]) + len(event["add"])
        if not self.config.strokes.ink_split:
            return changed
        epoch = self.strokes.epochs[-1]
        ink = epoch.canvas.new_ink()
        for stroke in list(self.session.strokes):
            if stroke.t0 < epoch.t0 or len(stroke.points) < 2:
                continue
            t = (
                stroke.t0 + np.asarray(stroke.dt)
                if len(stroke.dt) == len(stroke.points)
                else np.linspace(stroke.t0, stroke.t1, len(stroke.points))
            )
            pieces = split_on_ink(
                Stroke(t, np.asarray(stroke.points)), ink, epoch.canvas
            )
            if len(pieces) == 1 and len(pieces[0].mm) == len(stroke.points):
                continue
            self.session.replace(stroke.id, [(p.t, p.mm) for p in pieces])
            changed += 1
        return changed

    def rebuild_strokes(self) -> int:
        """After the final photo: the session's strokes rebuilt from the
        photo's ink and the tip path (shape from the photo, order and
        direction from the pen; ``strokes.photo``). Returns how many; 0 when
        there is no photo or nothing came out (the strokes stay). Safe to run
        outside the engine thread once the session is finished."""
        session = self.session
        with session._lock:
            scan = session.scan
        tip = session.tip_path()
        if scan is None or not tip:
            return 0
        pieces = reconstruct(scan["gray"], scan["box_mm"], scan["mm_per_px"], tip)
        if not pieces:
            return 0
        return session.use_photo_strokes([(p.t, p.mm) for p in pieces])

    def make_scan(self, image: np.ndarray, photo: bool = False):
        """Clean ink picture of the session's writing from a still (any
        size; the page is located in the still itself, so this is safe to
        run outside the engine thread). ``photo``: an uploaded phone photo
        (shrunk to at most 2000 px, photo contrast settings; with no strokes
        in the session the picture is cropped to the ink it finds)."""
        data = self.session.to_json()
        lines = [s["points"] for s in data["strokes"] + data["ink_strokes"]]
        if not photo:
            return scan_page(
                image,
                self.mapper.layout,
                box_mm=writing_box(lines),
                lines_mm=lines or None,
            )
        longest = max(image.shape[:2])
        if longest > 2000:
            f = 2000 / longest
            image = cv2.resize(image, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
        return scan_page(
            image,
            self.mapper.layout,
            lines_mm=lines or None,
            config=PHOTO,
            crop_to_ink=not lines,
        )

    def score_session(self) -> dict:
        """Local score of the practice character (Task 14); ValueError when
        there is no target or no glyph data for it. Shape and structure come
        from the final photo when there is one, else from the tip path."""
        data = self.session.to_json()
        target = data["target"]
        if not target:
            raise ValueError("no target character (practice mode)")
        r = data["rotation"]
        strokes = []
        for s in data["strokes"]:
            if not s["points"]:
                continue
            pts = np.asarray(s["points"], float)
            t = (
                s["t0"] + np.asarray(s["dt"], float)
                if len(s["dt"]) == len(pts)
                else np.linspace(s["t0"], s["t1"], len(pts))
            )
            strokes.append((t, rotate(pts, r)))
        ink = self.session.scan_centerlines()
        if ink is not None and strokes:
            # only the ink of this writing: other characters on the sheet and
            # the outline of a hand left on it are not part of it
            ink = near_path(ink, [p for _, p in strokes], r, 3.0)
        try:
            result = score(
                target, strokes, ink_points=None if ink is None else rotate(ink, r)
            )
        except KeyError as error:
            raise ValueError(str(error)) from error
        return {"type": "score", **result.as_dict(), "feedback": local_feedback(result)}

    def undo_ink(self, t0: float, t1: float) -> dict | None:
        """An undone stroke: its ink pieces go (now and when vectorized
        again). Returns the ink event. Call from the engine thread."""
        if self.ink is None:
            return None
        return self.session.apply_ink(self.ink.exclude(t0, t1), [])

    def _tip_boxes(self, t_from: float, t_to: float) -> list[np.ndarray]:
        """Page-mm boxes of the tip runs in (t_from, t_to]: split where the
        tip jumps or was lost, long travel moves left out, overlaps merged."""
        tips = np.array(self.ink._tips, float).reshape(-1, 3)
        tips = tips[(tips[:, 0] > t_from) & (tips[:, 0] <= t_to)]
        if not len(tips):
            return []
        step = np.linalg.norm(np.diff(tips[:, 1:], axis=0), axis=1)
        cut = np.flatnonzero((np.diff(tips[:, 0]) > 0.4) | (step > 5.0)) + 1
        boxes = []
        for run in np.split(tips[:, 1:], cut):
            lo, hi = run.min(0), run.max(0)
            if np.hypot(*(hi - lo)) <= 40.0:
                boxes.append(np.concatenate((lo, hi)))
        merged = True
        while merged and len(boxes) > 1:
            merged = False
            for i in range(len(boxes)):
                for j in range(i + 1, len(boxes)):
                    a, b = boxes[i], boxes[j]
                    if (
                        a[0] - 3 <= b[2]
                        and b[0] - 3 <= a[2]
                        and a[1] - 3 <= b[3]
                        and b[1] - 3 <= a[3]
                    ):
                        boxes[i] = np.concatenate(
                            (np.minimum(a[:2], b[:2]), np.maximum(a[2:], b[2:]))
                        )
                        del boxes[j]
                        merged = True
                        break
                if merged:
                    break
        return boxes

    def _ink_pass(
        self,
        t_from: float,
        t_to: float,
        now: float,
        inline: bool = False,
        epoch=None,
    ) -> list[dict]:
        canvas, epoch_t0 = (
            (self.strokes.epochs[-1].canvas, self.strokes.epochs[-1].t0)
            if epoch is None
            else epoch
        )
        out = []
        for box in self._tip_boxes(t_from, t_to):
            job = self.ink.prepare(canvas, epoch_t0, [box], now)
            if job is None:
                continue
            if self.sync_pages or inline:
                out += self.commit_ink(job, self.ink.compute(job))
            else:
                self.ink_jobs.append(job)
        return out

    def commit_ink(self, job: dict, strokes) -> list[dict]:
        """Apply a vectorized area (engine thread). Returns ink events."""
        event = self.session.apply_ink(*self.ink.commit(job, strokes))
        return [] if event is None else [event]

    def _ink_tick(self, now: float) -> list[dict]:
        out = []
        while self._retired and self._retired[0][0] <= now:
            _, canvas, epoch_t0, t_end = self._retired.pop(0)
            out += self._ink_pass(
                max(epoch_t0, self.ink.since), t_end, now, epoch=(canvas, epoch_t0)
            )
        lags = (self.config.strokes.settle_s, self.config.ink_late_s)
        for k, lag in enumerate(lags):
            t_to = now - lag
            if t_to > self._ink_cut[k]:
                out += self._ink_pass(max(self._ink_cut[k], self.ink.since), t_to, now)
                self._ink_cut[k] = t_to
        return out

    def start_roi(self) -> tuple[int, int, int, int]:
        w, h = self.config.sensor_size
        s = self.config.roi_size
        return ((w - s) // 2, (h - s) // 2, s, s)

    # -- events -----------------------------------------------------------------

    def on_event(
        self, kind: str, image: np.ndarray | None, metadata: dict
    ) -> list[dict]:
        if kind == "roi":
            return self._roi(image, metadata)
        if kind == "overview":
            self.pipeline.note_overview(image, metadata)
            result = self.pipeline.on_overview(image, metadata)
            if result is not None and result.roi is not None:
                self.roi_requests.append(result.roi)
            return []
        if kind == "page" and self.sync_pages:
            return self.check_page(image, metadata)
        return []

    def check_page(self, image: np.ndarray, metadata: dict) -> list[dict]:
        self.last_page_image = image
        check = self.pipeline.on_page(image, metadata)
        if check is None:
            return []
        self.health.page["checks"] += 1
        if check.status in self.health.page:
            self.health.page[check.status] += 1
        if check.status == "pending":
            self.snap_requests += 1  # confirm the jump with a fresh snapshot
        return [
            {
                "type": "page",
                "status": check.status,
                "relocated": check.relocated,
                "shift_px": None
                if check.shift_px is None
                else round(check.shift_px, 2),
                "frame_id": metadata.get("id"),
            }
        ]

    def _roi(self, image: np.ndarray, metadata: dict) -> list[dict]:
        out: list[dict] = []
        start = self.clock()
        if self.mapper.relocations != self._relocations:
            self._relocations = self.mapper.relocations
            if self._last_t is not None:
                if self.ink is not None:
                    # the old canvas goes now: vectorize what it still holds,
                    # and once more a little later (the hand may cover ink)
                    old = self.strokes.epochs[-1]
                    out += self._ink_pass(
                        max(self._ink_cut[1], self.ink.since),
                        self._last_t,
                        self._last_t,
                    )
                    self._retired.append(
                        (
                            self._last_t + self.config.ink_late_s,
                            old.canvas,
                            old.t0,
                            self._last_t,
                        )
                    )
                    self._retired = self._retired[-2:]
                    self._ink_cut = [self._last_t, self._last_t]
                self.strokes.page_changed(self._last_t)
        result = self.pipeline.on_roi(image, metadata)
        if result.roi is not None:
            self.roi_requests.append(result.roi)
        if self.ink is not None:
            if self.session.generation != self._session_gen:
                # new or cleared session: its ink starts now
                self._session_gen = self.session.generation
                self.ink.reset(result.t)
                self._ink_cut = [result.t, result.t]
            if result.mm is not None and result.detection.found:
                self.ink.add_tip(result.t, result.mm)
        det = result.detection
        origin = np.array((metadata.get("x", 0), metadata.get("y", 0)), float)
        mapper = self.mapper
        self.strokes.on_frame(
            image,
            result.t,
            lambda px, o=origin: mapper.to_mm(np.asarray(px, float) + o),
            (det.x - origin[0], det.y - origin[1]) if det.found else None,
            det.theta if det.found else None,
            result.mm,
            det.score if det.found else None,
        )
        self._last_t = result.t
        out.append(
            {
                "type": "tip",
                "t": round(result.t, 4),
                "frame_id": result.frame_id,
                "mm": None if result.mm is None else [round(v, 3) for v in result.mm],
                "status": result.state.status,
            }
        )
        if self._next_strokes is None or result.t >= self._next_strokes:
            self._next_strokes = result.t + self.config.stroke_interval_s
            settled, open_strokes = self.strokes.collect(result.t)
            for stroke in settled:
                added = self.session.add(stroke.t, stroke.mm)
                if added is not None:
                    out.append({"type": "stroke", **added.as_dict()})
            out.append(
                {
                    "type": "open",
                    "t": round(result.t, 4),
                    "strokes": [np.round(s.mm, 3).tolist() for s in open_strokes],
                }
            )
        if self.ink is not None and (
            self._ink_next is None or result.t >= self._ink_next
        ):
            self._ink_next = result.t + self.config.ink_interval_s
            out += self._ink_tick(result.t)
        self.health.roi(
            result.t, (self.clock() - start) * 1e3, det.found, metadata.get("age_us")
        )
        if self._next_health is None or result.t >= self._next_health:
            self._next_health = result.t + self.config.health_interval_s
            out.append(
                self.health.report(
                    result.state.status,
                    self.mapper.relocations - 1,
                    self.mapper.slip_px,
                )
            )
        return out

    def flush(self) -> list[dict]:
        """End of input: settle every remaining stroke."""
        self.strokes.flush()
        out = []
        settled, _ = self.strokes.collect(np.inf)
        for stroke in settled:
            added = self.session.add(stroke.t, stroke.mm)
            if added is not None:
                out.append({"type": "stroke", **added.as_dict()})
        if self.ink is not None and self._last_t is not None:
            out += self._ink_pass(
                self.ink.since, np.inf, self._last_t + 1.0, inline=True
            )
        return out
