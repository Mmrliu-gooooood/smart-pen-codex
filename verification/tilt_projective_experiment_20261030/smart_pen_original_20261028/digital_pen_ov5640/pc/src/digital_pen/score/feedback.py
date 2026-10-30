"""Instant written feedback from the local score (Task 17): a short comment
and up to three suggestions, by fixed rules, in well under a millisecond. The
AI comment (Task 16) arrives later and is shown beside it, never instead."""

from __future__ import annotations

from digital_pen.score.scorer import ScoreResult

# part -> (said when good, said when weak); stroke count is left out: pen
# up/down detection is not reliable enough to comment on
PHRASES = {
    "shape": ("笔画形状到位", "笔画的形状和位置还有偏差"),
    "structure": ("结构匀称", "结构比例还要调整"),
    "order": ("笔顺正确", "笔顺有错"),
    "direction": ("运笔方向正确", "有笔画方向写反了"),
}
GOOD, WEAK = 0.85, 0.7


def level(score: int) -> str:
    if score >= 85:
        return "写得很好"
    if score >= 70:
        return "整体不错"
    if score >= 55:
        return "基本成形"
    return "还需要多练"


def local_feedback(result: ScoreResult) -> dict:
    """``{"comment", "suggestions", "speech"}`` for the page and the voice."""
    if not result.strokes or not result.parts:
        comment = "没有找到可评的笔迹。"
        return {"comment": comment, "suggestions": [], "speech": comment}
    parts = result.parts
    good = [PHRASES[k][0] for k in PHRASES if parts.get(k, 0) >= GOOD]
    weak = sorted((parts.get(k, 0), k) for k in PHRASES if parts.get(k, 0) < WEAK)
    said = [level(result.score)] + good[:2]
    if weak:
        said.append("但" + "，".join(PHRASES[k][1] for _, k in weak[:2]))
    comment = "，".join(said) + "。"
    # the scorer's issues are already actionable and ordered by importance;
    # the stroke-count one is a caveat, not advice
    suggestions = [
        text
        for text in result.issues
        if not text.startswith("笔画数") and text != "写得很规范。"
    ][:3]
    speech = f"{result.char}，{result.score}分。{comment}" + "".join(
        f"{text.rstrip('。')}。" for text in suggestions
    )
    return {"comment": comment, "suggestions": suggestions, "speech": speech}
