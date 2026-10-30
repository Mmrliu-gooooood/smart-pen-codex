"""Per-event tip pipeline for a TRACK stream (Task 10).

Glue between the stream events and detector, tracker and page mapper, with
no I/O, so the live app, replay and later the engine service (Task 12) share
it:

  on_roi(image, metadata)       detect (tracker hint first, full search if it
                                fails; only on the page once it is located),
                                update the track, map the tip to mm;
                                returns a TipResult with the ROI to request
                                next (None: keep the current one)
  on_overview(image, metadata)  while lost: coarse search, reacquire; while
                                the track has been still for a while: the same
                                search, to see whether the tip is elsewhere
  on_page(image, metadata)      paper-movement check / relocation

A mark on the paper can look enough like a tip that, once the track is on
it, every ROI frame confirms it: the track never gets lost, so the overview
search that would find the pen never runs, and the ROI stays parked there
(seen live, Task 18: the tip dot frozen while the pen drew elsewhere). So a
still track is checked against the overview every ``check_every_s``; when the
best tip there is somewhere else, the track moves to it and the still spot is
excluded from all later searches (kept in page mm, so it survives paper
relocation). A pen really held still stays the best tip and keeps its track.

With no pen in view at all the mark is the best tip, so the check alone
keeps it. Every overview frame therefore also goes to ``note_overview``: when
the whole scene has not changed over ``static_s`` (99th percentile of the
pixel change below ``static_level``; a hand holding a pen always moves a
little, live 2026-10-27: ~2 with nobody there, ~50 while drawing) and the
track has been still that long, nothing is there: the track is dropped and
its spot excluded.

Without a pen the searches then hopped from mark to mark (live, Task 18:
the dot jumping about with the pen out of view). So a track only starts
where something moved (``require_motion``): a pen that comes into view
always moves, a mark never does. An overview detection needs a change near
it from the previous overview frame, an ROI detection from the previous ROI
frame at the same origin (blurred difference >= ``motion_level`` within
``motion_px``).

Frame metadata are the device fields of the stream (``x``/``y`` ROI origin,
``timestamp_us``, ``id``, ``scale``).
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from digital_pen.tip.detector import TipDetection, TipDetector
from digital_pen.tip.page_map import PageCheck, PageMapper
from digital_pen.tip.tracker import TipTracker, TrackState, detect_in_overview


@dataclass(frozen=True)
class TipResult:
    frame_id: int
    t: float
    detection: TipDetection  # sensor pixels
    state: TrackState
    mm: tuple[float, float] | None  # page millimetres (u right, v up)
    roi: tuple[int, int, int, int] | None  # ROI to request, if it changed
    searched: bool


class TipPipeline:
    def __init__(
        self,
        detector: TipDetector,
        tracker: TipTracker | None = None,
        mapper: PageMapper | None = None,
        *,
        roi_lead_s: float = 0.09,
        coarse_detector: TipDetector | None = None,
        track_paper: bool = True,
        sensor_size: tuple[int, int] = (800, 600),
        page_margin_mm: float = 1.5,
        check_every_s: float = 2.0,
        far_px: float = 12.0,
        excluded_mm: float = 3.0,
        max_excluded: int = 16,
        static_s: float = 2.0,
        static_level: float = 8.0,
        require_motion: bool = True,
        motion_level: float = 20.0,
        motion_px: float = 32.0,
    ):
        self.sensor_size = sensor_size
        self.static_s = static_s
        self.static_level = static_level
        self.require_motion = require_motion
        self.motion_level = motion_level
        self.motion_px = motion_px  # sensor px
        self._last_roi: tuple[tuple[float, float], np.ndarray] | None = None
        self.rejected_still = 0  # starts refused for want of motion
        self._overviews: list[tuple[float, np.ndarray]] = []
        self.drops = 0
        self.check_every_s = check_every_s
        self.far_px = far_px  # an overview tip this far away is "elsewhere"
        self.excluded_mm = excluded_mm
        self.max_excluded = max_excluded
        self.excluded: list[tuple[float, float]] = []  # page mm (or sensor px)
        self.switches = 0
        self._next_check = -np.inf
        # Follow small paper slips from the dots of every ROI frame.
        self.track_paper = track_paper
        self.page_margin_mm = page_margin_mm
        self.detector = detector
        # Overview search may use a different model (see COARSE_MODEL_PATH).
        self.coarse_detector = coarse_detector or detector
        self.roi_lead_s = roi_lead_s
        self.tracker = tracker or TipTracker()
        self.mapper = mapper
        self.requested_roi: tuple[int, int, int, int] | None = None
        self.page_checks: list[PageCheck] = []

    def _located(self) -> bool:
        return self.mapper is not None and self.mapper.location is not None

    def _spot(self, x: float, y: float) -> tuple[float, float]:
        """A sensor point as kept in ``excluded``: page mm once located."""
        if self._located():
            u, v = self.mapper.to_mm((x, y))[0]
            return float(u), float(v)
        return float(x), float(y)

    def _is_excluded(self, x: float, y: float) -> bool:
        if not self.excluded:
            return False
        p = np.array(self._spot(x, y))
        r = self.excluded_mm if self._located() else self.excluded_mm * 2.6
        return bool((np.hypot(*(np.array(self.excluded) - p).T) <= r).any())

    def _region(self, origin, exclude: bool = True):
        """Allowed-tip test in the pixels of a frame at ``origin`` (or None):
        on the page and, with ``exclude``, not on an excluded spot. Excluded
        spots only stop a track from starting there: a pen being tracked
        through a dense drawing passes them (live, Task 18: tracks were lost
        where the spots piled up)."""
        w, h = self.sensor_size
        mask = None
        if self.mapper is not None:
            mask = self.mapper.page_mask((h, w), self.page_margin_mm)
        exclude = exclude and bool(self.excluded)
        if mask is None and not exclude:
            return None

        def inside(x, y):
            sx, sy = x + origin[0], y + origin[1]
            if mask is not None:
                xi, yi = int(round(sx)), int(round(sy))
                if not (0 <= xi < w and 0 <= yi < h and bool(mask[yi, xi])):
                    return False
            return not (exclude and self._is_excluded(sx, sy))

        return inside

    @staticmethod
    def _time(metadata) -> float:
        return float(metadata.get("timestamp_us", 0)) * 1e-6

    def _moved(self, a: np.ndarray, b: np.ndarray, cx: float, cy: float, r: float):
        """Did anything change within ``r`` px of (cx, cy) between a and b?"""
        if a.shape != b.shape:
            return False
        h, w = a.shape
        x0, x1 = max(int(cx - r), 0), min(int(cx + r) + 1, w)
        y0, y1 = max(int(cy - r), 0), min(int(cy + r) + 1, h)
        if x1 - x0 < 3 or y1 - y0 < 3:
            return False
        pa = cv2.GaussianBlur(a[y0:y1, x0:x1], (3, 3), 0)
        pb = cv2.GaussianBlur(b[y0:y1, x0:x1], (3, 3), 0)
        return float(cv2.absdiff(pa, pb).max()) >= self.motion_level

    def _roi_moved(self, now, before, sx: float, sy: float) -> bool:
        """Change around a sensor point between two ROI frames ((origin,
        image) each; the ROI may have moved in between)."""
        r = self.motion_px
        x0, x1 = int(sx - r), int(sx + r) + 1
        y0, y1 = int(sy - r), int(sy + r) + 1
        frames = [((int(ox), int(oy)), image) for (ox, oy), image in (now, before)]
        for (ox, oy), image in frames:  # the window seen by both, sensor px
            h, w = image.shape
            x0, x1 = max(x0, ox), min(x1, ox + w)
            y0, y1 = max(y0, oy), min(y1, oy + h)
        if x1 - x0 < 3 or y1 - y0 < 3:
            return False
        a, b = (
            cv2.GaussianBlur(image[y0 - oy : y1 - oy, x0 - ox : x1 - ox], (3, 3), 0)
            for (ox, oy), image in frames
        )
        return float(cv2.absdiff(a, b).max()) >= self.motion_level

    def _overview_moved(self, det: TipDetection, metadata: dict) -> bool:
        """Change near an overview detection since the previous overview."""
        t = self._time(metadata)
        times = [o[0] for o in self._overviews]
        k = next((i for i, s in enumerate(times) if abs(s - t) < 1e-6), None)
        if k is None or k == 0 or t - times[k - 1] > 1.2:
            return False
        scale = float(metadata.get("scale", 4))
        return self._moved(
            self._overviews[k][1],
            self._overviews[k - 1][1],
            det.x / scale,
            det.y / scale,
            self.motion_px / scale,
        )

    def on_roi(self, image: np.ndarray, metadata: dict) -> TipResult:
        t = self._time(metadata)
        origin = (float(metadata.get("x", 0)), float(metadata.get("y", 0)))
        hints = self.tracker.hint(t, origin)
        # not firmly tracking: a detection may start a track (lost) or re-start
        # it elsewhere (two agreeing far detections while coasting), so
        # excluded spots are skipped; motion is required only to start from
        # lost (while coasting the ROI moves with the prediction, and asking
        # for motion there broke tracks: replay 2026-10-27)
        region = self._region(origin, exclude=self.tracker.status != "track")
        searched = False
        det = None
        if hints:
            det = self.detector.detect(image, hints, search=False, region=region)
        if det is None or not det.found:
            det = self.detector.detect(image, hints, region=region)
            searched = True
        last, self._last_roi = self._last_roi, (origin, image)
        start_ok = True
        if self.require_motion and det.found and self.tracker.status == "lost":
            # (re)starting a track here: only where the frame changed
            start_ok = last is not None and self._roi_moved(
                (origin, image), last, det.x + origin[0], det.y + origin[1]
            )
            self.rejected_still += not start_ok
            if not start_ok:
                # not a pen: reported as nothing found (no dot on the page,
                # nothing for the stroke trail)
                det = TipDetection(False, det.x, det.y, det.theta, det.score)
        det = det.shifted(*origin)
        if self.track_paper and self.mapper is not None:
            self.mapper.track(image, origin)
        state = self.tracker.update(t, det if det.found else None)
        mm = None
        if det.found and self.mapper is not None and self.mapper.location is not None:
            u, v = self.mapper.to_mm((det.x, det.y))[0]
            mm = (float(u), float(v))
        return TipResult(
            int(metadata.get("id", -1)), t, det, state, mm, self._next_roi(t), searched
        )

    def note_overview(self, image: np.ndarray, metadata: dict) -> bool:
        """Call with every overview frame. Drops a still track when nothing in
        the scene has moved for ``static_s`` (see the module notes); True if
        it did."""
        t = self._time(metadata)
        self._overviews = [o for o in self._overviews if t - o[0] <= self.static_s * 2]
        self._overviews.append((t, image))
        if self.tracker.still_for(t) < self.static_s:
            return False
        # every frame of the last static_s alike (a hand that moved in between
        # and back is not "nothing there")
        window = [o for o in self._overviews[:-1] if t - o[0] <= self.static_s + 0.6]
        if not window or t - window[0][0] < self.static_s:
            return False
        now = image.astype(np.int16)
        for _, old in window:
            if old.shape != image.shape:
                return False
            change = np.abs(now - old.astype(np.int16))
            if float(np.percentile(change, 99)) >= self.static_level:
                return False
        s = self.tracker.state()
        self.excluded = (self.excluded + [self._spot(s.x, s.y)])[-self.max_excluded :]
        self.tracker.reset()
        self.drops += 1
        return True

    def needs_overview(self, metadata: dict) -> bool:
        """Is a coarse search of this overview frame wanted: track lost, or
        still for a while and not checked lately."""
        if self.tracker.status == "lost":
            return True
        t = self._time(metadata)
        return (
            self.tracker.still_for(t) >= self.tracker.config.still_s
            and t >= self._next_check
        )

    def on_overview(self, image: np.ndarray, metadata: dict) -> TipResult | None:
        """Coarse search while lost or still; None when not needed."""
        if not self.needs_overview(metadata):
            return None
        return self.apply_overview(self.search_overview(image, metadata), metadata)

    def search_overview(self, image: np.ndarray, metadata: dict) -> TipDetection:
        """The coarse search alone (~150 ms); touches no tracker state, so it
        can run in a worker thread while ROI frames keep being processed."""
        return detect_in_overview(
            self.coarse_detector,
            image,
            float(metadata.get("scale", 4)),
            self._region((0.0, 0.0)),
        )

    def apply_overview(self, det: TipDetection, metadata: dict) -> TipResult | None:
        """Re-start the track from a coarse detection if it is lost; move a
        still track to it if the tip is elsewhere (see the module notes)."""
        t = self._time(metadata)
        moved = not self.require_motion or (
            det.found and self._overview_moved(det, metadata)
        )
        if self.tracker.status != "lost":
            if self.tracker.still_for(t) < self.tracker.config.still_s:
                return None  # moving again since the search was asked for
            self._next_check = t + self.check_every_s
            x, y = self.tracker.state().x, self.tracker.state().y
            if not det.found or np.hypot(det.x - x, det.y - y) <= self.far_px:
                return None  # the still spot is still the best tip: keep it
            if not moved:
                self.rejected_still += 1
                return None  # elsewhere, but nothing moves there: not a pen
            self.excluded = (self.excluded + [self._spot(x, y)])[-self.max_excluded :]
            self.switches += 1
        elif det.found and not moved:
            self.rejected_still += 1
            return None
        state = self.tracker.reacquire(t, det)
        return TipResult(
            int(metadata.get("id", -1)), t, det, state, None, self._next_roi(t), True
        )

    def on_page(self, image: np.ndarray, metadata: dict) -> PageCheck | None:
        if self.mapper is None:
            return None
        check = self.mapper.check(
            image, origin=(metadata.get("x", 0), metadata.get("y", 0))
        )
        self.page_checks.append(check)
        return check

    def _next_roi(self, t: float):
        # A new ROI takes effect within two frames (Task 8); aim it at where
        # the tip will be then.
        roi = self.tracker.next_roi(t + self.roi_lead_s)
        if roi is None or roi == self.requested_roi:
            return None
        self.requested_roi = roi
        return roi
