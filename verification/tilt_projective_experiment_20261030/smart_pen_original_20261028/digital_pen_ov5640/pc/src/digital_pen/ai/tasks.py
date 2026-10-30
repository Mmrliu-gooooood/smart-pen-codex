"""What the gateway asks the model: feedback on a practice character, and
draw-and-guess. Replies are JSON, checked and trimmed before use; the local
score is never replaced, the model only words the feedback."""

from __future__ import annotations

from digital_pen.ai.client import AIError, ChatClient, first_json, image_part

# Reasoning models can deliberate over a rough sketch until the token budget
# runs out with no answer; asking for a quick judgement keeps them short.
QUICK = "\n不需要反复推敲：快速看一眼，直接给出结果。"

EVALUATE_PROMPT = (
    "你是耐心的书法老师。图片是学生用硬笔写的“{char}”（白底黑字的照片）。\n"
    "本地程序的分析（仅供参考）：总分 {score}/100；"
    "形状 {shape}、结构 {structure}、笔顺 {order}、方向 {direction}（0–1）。\n"
    "程序发现的问题：{issues}\n"
    "请看图，用简短中文给出评语和改进建议。只输出一个 JSON 对象，不要其他文字：\n"
    '{{"comment": "一两句总体评价（不超过60字）", '
    '"suggestions": ["具体建议1", "建议2"]}}\n'
    "建议 1–3 条，每条不超过30字，针对这个字的笔画和结构。" + QUICK
)

GUESS_PROMPT = (
    "这是一幅用笔在纸上画的简笔画（白底黑线）。请猜它画的是什么。\n"
    "只输出一个 JSON 对象，不要其他文字：\n"
    '{"guesses": [{"label": "中文名称", "confidence": 0.0到1.0}, '
    "...最多3个，按可能性从高到低], "
    '"reason": "一句话理由（不超过30字）"}' + QUICK
)


def _text(value, limit: int) -> str:
    return str(value).strip()[:limit] if value is not None else ""


def evaluate(client: ChatClient, png: bytes, char: str, score: dict | None) -> dict:
    s = score or {}
    parts = s.get("parts", {})
    prompt = EVALUATE_PROMPT.format(
        char=char,
        score=s.get("score", "未知"),
        shape=parts.get("shape", "?"),
        structure=parts.get("structure", "?"),
        order=parts.get("order", "?"),
        direction=parts.get("direction", "?"),
        issues="；".join(s.get("issues", [])[:6]) or "无",
    )
    reply = client.chat(
        [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}, image_part(png)],
            }
        ]
    )
    data = first_json(reply)
    comment = _text(data.get("comment"), 120)
    suggestions = [
        _text(x, 60) for x in (data.get("suggestions") or []) if _text(x, 60)
    ]
    if not comment:
        raise AIError("模型没有给出评语。", "bad_reply")
    return {"comment": comment, "suggestions": suggestions[:3]}


def guess(client: ChatClient, png: bytes) -> dict:
    reply = client.chat(
        [
            {
                "role": "user",
                "content": [{"type": "text", "text": GUESS_PROMPT}, image_part(png)],
            }
        ]
    )
    data = first_json(reply)
    out = []
    for g in data.get("guesses") or []:
        if not isinstance(g, dict) or not _text(g.get("label"), 20):
            continue
        try:
            conf = float(g.get("confidence", 0))
        except (TypeError, ValueError):
            conf = 0.0
        out.append(
            {
                "label": _text(g.get("label"), 20),
                "confidence": round(min(max(conf, 0.0), 1.0), 2),
            }
        )
    if not out:
        raise AIError("模型没有给出猜测。", "bad_reply")
    return {"guesses": out[:3], "reason": _text(data.get("reason"), 60)}


def ping(client: ChatClient) -> str:
    """A tiny text call to check the key, URL and model."""
    reply = client.chat(
        [{"role": "user", "content": "只回复两个字：你好"}], max_tokens=400
    )
    return _text(reply, 40)
