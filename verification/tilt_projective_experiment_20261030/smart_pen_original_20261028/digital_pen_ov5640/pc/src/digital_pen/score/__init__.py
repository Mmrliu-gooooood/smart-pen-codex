"""Local stroke scoring against standard strokes (Task 14)."""

from digital_pen.score.reference import Reference, RefStroke, available, load
from digital_pen.score.scorer import WEIGHTS, ScoreResult, StrokeResult, score

__all__ = [
    "WEIGHTS",
    "RefStroke",
    "Reference",
    "ScoreResult",
    "StrokeResult",
    "available",
    "load",
    "score",
]
