"""Ink detection, pen-down/up and stroke reconstruction (Task 11)."""

from digital_pen.strokes.canvas import CanvasConfig, PaperCanvas
from digital_pen.strokes.ink import InkConfig, InkWatcher, TrailPoint, cover_mask
from digital_pen.strokes.post import finish, resample, smooth, snap_to_ink
from digital_pen.strokes.segment import SegmenterConfig, Stroke, segment
from digital_pen.strokes.tracker import StrokeTracker, StrokeTrackerConfig

__all__ = [
    "CanvasConfig",
    "InkConfig",
    "InkWatcher",
    "PaperCanvas",
    "SegmenterConfig",
    "Stroke",
    "StrokeTracker",
    "StrokeTrackerConfig",
    "TrailPoint",
    "cover_mask",
    "finish",
    "resample",
    "segment",
    "smooth",
    "snap_to_ink",
]
