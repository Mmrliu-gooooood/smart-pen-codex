"""Operator logic of the recording tool, independent of any window system.

The app turns key presses and mouse clicks into calls on this controller;
the controller drives the recorder and the TRACK session (ROI moves, page
snapshots). Keys:
  space  start / finish the current prompt
  r      discard: the sample being written, or else the previous one (redo)
  n      skip the current prompt
  m      paper moved (marks the event, takes a page snapshot; completes an
         "action" prompt)
  p      page snapshot now
  q      end the session
A click on the overview moves the writing cell there (not while writing).
The page snapshot after a sample is taken AFTER_SNAP_DELAY_S later, so the
hand has time to leave the ink (digits-01: several were taken with the hand
still over it); call :meth:`tick` regularly.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from digital_pen.capture.protocol import SessionSpec
from digital_pen.capture.recorder import SessionRecorder

AFTER_SNAP_DELAY_S = 1.0


def cell_rois(crop, size: int, frame=(800, 600)) -> list[tuple[int, int, int, int]]:
    """3x3 writing cells inside the page crop (row-major), size x size each."""
    x, y, w, h = crop
    cells = []
    for fy in (0.25, 0.5, 0.75):
        for fx in (0.25, 0.5, 0.75):
            cells.append(roi_at(x + fx * w, y + fy * h, size, frame))
    return cells


def roi_at(
    cx: float, cy: float, size: int, frame=(800, 600)
) -> tuple[int, int, int, int]:
    """size x size window centred on (cx, cy), kept inside the frame."""
    x = int(round(cx - size / 2))
    y = int(round(cy - size / 2))
    x = min(max(0, x), frame[0] - size)
    y = min(max(0, y), frame[1] - size)
    return (x, y, size, size)


@dataclass
class Status:
    text: str
    detail: str
    writing: bool
    done: bool


class CaptureController:
    def __init__(
        self, spec: SessionSpec, recorder: SessionRecorder, session, roi, clock=None
    ):
        self.spec = spec
        self.recorder = recorder
        self.session = session  # TrackSession (or a stand-in with set_roi/snap)
        self.roi = tuple(int(v) for v in roi)
        self.index = 0
        self.writing = False
        self.quit = False
        self.message = ""
        self._clock = clock or time.monotonic
        self._snap_due: float | None = None

    # -- state ------------------------------------------------------------------

    @property
    def prompt(self):
        return (
            self.spec.prompts[self.index]
            if self.index < len(self.spec.prompts)
            else None
        )

    def status(self) -> Status:
        total = len(self.spec.prompts)
        ok = sum(s.status == "ok" for s in self.recorder.samples)
        prompt = self.prompt
        if self._snap_due is not None:
            return Status("请把手移开", "马上拍写完后的整页", False, False)
        if prompt is None:
            return Status("本会话完成，按 q 结束", f"有效样本 {ok}", False, True)
        if prompt.kind == "action":
            return Status(prompt.text, f"第 {self.index + 1}/{total} 步", False, False)
        if self.writing:
            return Status(
                f"正在记录：{prompt.label}", "写完按空格；写坏了按 r", True, False
            )
        return Status(
            prompt.text,
            f"第 {self.index + 1}/{total} 个，按空格开始；有效样本 {ok}",
            False,
            False,
        )

    # -- input ------------------------------------------------------------------

    def tick(self) -> None:
        """Take a pending after-sample snapshot once its delay has passed."""
        if self._snap_due is not None and self._clock() >= self._snap_due:
            self._snap_due = None
            self.session.snap()

    def _flush_snap(self) -> None:
        if self._snap_due is not None:
            self._snap_due = None
            self.session.snap()

    def key(self, key: str) -> None:
        self.message = ""
        prompt = self.prompt
        if key in (" ", "q", "m", "p"):
            self._flush_snap()
        if key == "q":
            if self.writing:
                self.recorder.end_sample(notes="session ended while writing")
                self.writing = False
            self.quit = True
        elif key == " ":
            if prompt is None or prompt.kind == "action":
                return
            if not self.writing:
                self.recorder.begin_sample(
                    prompt.label, prompt.kind, prompt.text, self.roi
                )
                self.session.snap()  # page before writing
                self.writing = True
            else:
                self.recorder.end_sample()
                # Page with the finished ink, once the hand is away.
                self._snap_due = self._clock() + AFTER_SNAP_DELAY_S
                self.writing = False
                self.index += 1
        elif key == "r":
            if self.writing:
                self.recorder.discard_last()
                self.writing = False
                self.message = "已丢弃，重写这一个"
            else:
                discarded = self.recorder.discard_last()
                if discarded is not None and self.index > 0:
                    self.index -= 1
                    self.message = f"已丢弃上一个（{discarded.label}），重写"
        elif key == "n":
            if self.writing:
                self.recorder.discard_last()
                self.writing = False
            if prompt is not None:
                self.recorder.mark("skipped", label=prompt.label)
                self.index += 1
        elif key == "m":
            self.recorder.mark("paper_moved")
            self.session.snap()
            if prompt is not None and prompt.kind == "action":
                self.index += 1
            self.message = "已记录：纸张移动"
        elif key == "p":
            self.session.snap()
            self.recorder.mark("snapshot_requested")

    def click(self, frame_x: float, frame_y: float) -> None:
        """Move the writing cell (frame pixels); ignored while writing."""
        if self.writing:
            self.message = "写完当前样本后再移动区域"
            return
        size = self.roi[2]
        self.roi = roi_at(frame_x, frame_y, size)
        self.session.set_roi(self.roi)
        self.recorder.mark("roi_moved", roi=list(self.roi))
