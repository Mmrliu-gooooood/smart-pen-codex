"""Frame-by-frame stroke building on top of the tip pipeline (Task 11).

Per ROI frame (after TipPipeline.on_roi):
  1. a found tip with a page position becomes a trail point, its "before"
     darkness read from the canvas before this frame is written;
  2. the frame's darkness is written to the canvas where pen, hand and
     shadows do not cover the paper;
  3. pending trail points whose "after" view is now available are resolved.

``strokes()`` segments the resolved trail. Strokes are kept in page mm.

For a long-running service, ``collect(now)`` finalizes strokes as soon as
they are settled (all their points resolved and the pen gone for
``settle_s``) and returns them with the still-open strokes; finalized points
are dropped, and with ``keep_epochs=False`` so are old canvases, so memory
stays bounded.

Page model changes (``page_changed``): the paper is often pushed while
writing, and each relocation can also differ from the previous model by a
pixel or so. Canvas content written under the old model then no longer
lines up with new frames, and old ink would show up as "fresh" ink beside
itself. So every page model gets its own canvas *epoch*: evidence, ink links
and snapping only ever compare views taken under the same model. Points
still pending at the switch become unknown (the segmenter bridges them).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from digital_pen.strokes.canvas import CanvasConfig, PaperCanvas
from digital_pen.strokes.ink import (
    InkConfig,
    InkWatcher,
    TrailPoint,
    cover_mask,
    ink_darkness,
)
from digital_pen.strokes.post import finish, split_on_ink
from digital_pen.strokes.segment import SegmenterConfig, Stroke, segment
from digital_pen.tip.detector import darkness_map


@dataclass
class StrokeTrackerConfig:
    canvas: CanvasConfig = field(default_factory=CanvasConfig)
    ink: InkConfig = field(default_factory=InkConfig)
    segmenter: SegmenterConfig = field(default_factory=SegmenterConfig)
    snap: bool = True
    step_mm: float = 0.5
    # Tips scoring below this (detector logit) are not trusted as trail
    # points: such tips are often an ink end or edge held by the tracker
    # after the pen has left, and a "tip" that never moves away can never be
    # checked for ink. (2.0 vs 3.0 chosen on the training sessions.)
    min_tip_score: float = 2.0
    # Decide stroke breaks by new ink between consecutive points (segment.py).
    ink_links: bool = True
    # Keep every canvas epoch and the whole trail (offline evaluation); a
    # service sets both False and uses collect().
    keep_epochs: bool = True
    keep_trail: bool = True
    settle_s: float = 1.6
    # Cut settled strokes where they cross paper without new ink (pen-up
    # lines the segmentation missed); off for the Task 11 evaluations.
    ink_split: bool = False


@dataclass
class Epoch:
    """Canvas and trail points under one page model."""

    t0: float
    canvas: PaperCanvas
    trail: list[TrailPoint] = field(default_factory=list)
    t1: float = float("inf")


class StrokeTracker:
    def __init__(self, config: StrokeTrackerConfig | None = None):
        self.config = config or StrokeTrackerConfig()
        self.trail: list[TrailPoint] = []  # all points, every epoch
        self.epochs: list[Epoch] = []
        self.finished: list[Stroke] = []  # collect(): settled strokes, in order
        self._pending_final: list[Stroke] = []
        self._start_epoch(-np.inf)

    def _start_epoch(self, t: float) -> None:
        self.canvas = PaperCanvas(self.config.canvas)
        self.watcher = InkWatcher(self.canvas, self.config.ink)
        self.epochs.append(Epoch(t, self.canvas))

    def page_changed(self, t: float) -> None:
        """The page model changed at ``t``: start a new canvas epoch."""
        current = self.epochs[-1]
        if not current.trail and np.all(np.isinf(current.canvas.stamp)):
            return
        self.watcher.flush()
        current.t1 = t
        if not self.config.keep_epochs:
            # Settle everything of the old epoch now; its canvas goes away.
            self._pending_final += self._settle(current, np.inf)[0]
            self.epochs.remove(current)
        self._start_epoch(t)

    def canvas_at(self, t: float) -> PaperCanvas:
        for epoch in self.epochs:
            if epoch.t0 <= t < epoch.t1:
                return epoch.canvas
        return self.canvas

    def on_frame(
        self,
        gray: np.ndarray,
        t: float,
        frame_to_mm,
        tip_frame=None,
        theta: float | None = None,
        tip_mm=None,
        score: float | None = None,
    ) -> list[TrailPoint]:
        """Feed one ROI frame; ``tip_frame`` is the tip in this frame's pixels.

        ``frame_to_mm`` maps (N, 2) frame pixels to page mm with the page model
        valid for this frame. Returns the trail points resolved now.
        """
        trusted = score is None or score >= self.config.min_tip_score
        if tip_mm is not None and trusted:
            point = self.watcher.add(t, tip_mm)
            if self.config.keep_trail:
                self.trail.append(point)
            self.epochs[-1].trail.append(point)
        # Pen, hand: plain darkness; ink on the canvas: shadow-free darkness.
        covered = cover_mask(darkness_map(gray), tip_frame, theta, self.config.ink)
        ink = ink_darkness(gray, self.config.ink.shadow_sigma_px)
        self.canvas.update(ink, ~covered, frame_to_mm, t)
        return self.watcher.resolve(t, tip_mm if trusted else None)

    def flush(self) -> list[TrailPoint]:
        return self.watcher.flush()

    def _epoch_strokes(self):
        for epoch in self.epochs:
            canvas = epoch.canvas if self.config.ink_links else None
            for stroke in segment(epoch.trail, self.config.segmenter, canvas):
                yield epoch, stroke

    def _settle(self, epoch: Epoch, now: float):
        """(newly settled finished strokes, open raw strokes) of an epoch."""
        canvas = epoch.canvas if self.config.ink_links else None
        strokes = segment(epoch.trail, self.config.segmenter, canvas)
        times = np.array([p.t for p in epoch.trail])
        pending = (
            [p.t for p in self.watcher.pending] if epoch is self.epochs[-1] else []
        )
        oldest_pending = min(pending) if pending else np.inf
        settled, cut = [], 0
        for stroke in strokes:
            end = stroke.t[-1]
            if end < now - self.config.settle_s and end < oldest_pending:
                ink = (
                    epoch.canvas.new_ink()
                    if self.config.snap or self.config.ink_split
                    else None
                )
                done = finish(
                    stroke,
                    epoch.canvas if self.config.snap else None,
                    ink,
                    self.config.step_mm,
                )
                if self.config.ink_split:
                    settled += split_on_ink(done, ink, epoch.canvas)
                else:
                    settled.append(done)
                cut = int(np.searchsorted(times, end, side="right"))
            else:
                break
        open_strokes = strokes[len(settled) :]
        # Drop points that can no longer join a stroke: those of settled
        # strokes, and resolved pen-up points before the first open stroke
        # that are older than the settle time.
        limit = min(
            open_strokes[0].t[0] if open_strokes else np.inf,
            now - self.config.settle_s,
            oldest_pending,
        )
        cut = max(cut, int(np.searchsorted(times, limit, side="left")))
        if cut:
            epoch.trail = epoch.trail[cut:]
        return settled, open_strokes

    def collect(self, now: float) -> tuple[list[Stroke], list[Stroke]]:
        """Strokes settled since the last call, and the still-open ones (raw)."""
        settled = self._pending_final
        self._pending_final = []
        new, open_strokes = self._settle(self.epochs[-1], now)
        settled = settled + new
        self.finished += settled
        return settled, open_strokes

    def raw_strokes(self) -> list[Stroke]:
        return [stroke for _, stroke in self._epoch_strokes()]

    def strokes(self) -> list[Stroke]:
        out, inks = [], {}
        for epoch, stroke in self._epoch_strokes():
            if self.config.snap:
                key = id(epoch)
                if key not in inks:
                    inks[key] = epoch.canvas.new_ink()
                out.append(finish(stroke, epoch.canvas, inks[key], self.config.step_mm))
            else:
                out.append(finish(stroke, None, None, self.config.step_mm))
        return out
