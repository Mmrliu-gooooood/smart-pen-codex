"""Pen-tip detection, tracking and page mapping for the overhead camera (Task 10)."""

from digital_pen.tip.detector import (
    COARSE_MODEL_PATH,
    MODEL_PATH,
    PatchModel,
    TipDetection,
    TipDetector,
    TipDetectorConfig,
    darkness_map,
)
from digital_pen.tip.page_map import PageCheck, PageMapper
from digital_pen.tip.pipeline import TipPipeline, TipResult
from digital_pen.tip.tracker import (
    TipTracker,
    TrackerConfig,
    TrackState,
    detect_in_overview,
)

__all__ = [
    "COARSE_MODEL_PATH",
    "MODEL_PATH",
    "PageCheck",
    "PageMapper",
    "PatchModel",
    "TipDetection",
    "TipDetector",
    "TipDetectorConfig",
    "TipPipeline",
    "TipResult",
    "TipTracker",
    "TrackState",
    "TrackerConfig",
    "darkness_map",
    "detect_in_overview",
]
