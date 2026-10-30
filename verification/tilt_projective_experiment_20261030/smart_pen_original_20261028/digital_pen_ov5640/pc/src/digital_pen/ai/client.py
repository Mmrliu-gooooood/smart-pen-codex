"""OpenAI-compatible chat completions with image input (httpx)."""

from __future__ import annotations

import base64
import json
import re

import cv2
import httpx
import numpy as np

from digital_pen.ai.config import PRESETS, AISettings


class AIError(Exception):
    """A failed AI call, with a message for the page (no secrets in it)."""

    def __init__(self, message: str, kind: str = "error"):
        super().__init__(message)
        self.kind = (
            kind  # not_configured / auth / quota / timeout / network / bad_reply
        )


def image_part(png: bytes, detail: str = "default", max_side: int = 512) -> dict:
    """A PNG as an image content part, downscaled so its long side is at most
    ``max_side`` (a finished scan can be ~1500 px; the model needs far less,
    and smaller images come back faster)."""
    image = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_UNCHANGED)
    if image is not None and max(image.shape[:2]) > max_side:
        f = max_side / max(image.shape[:2])
        size = (round(image.shape[1] * f), round(image.shape[0] * f))
        image = cv2.resize(image, size, interpolation=cv2.INTER_AREA)
        png = cv2.imencode(".png", image)[1].tobytes()
    url = "data:image/png;base64," + base64.b64encode(png).decode("ascii")
    return {"type": "image_url", "image_url": {"url": url, "detail": detail}}


def first_json(text: str) -> dict:
    """The first JSON object in a reply (models sometimes add prose or ```)."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    start = text.find("{")
    while start >= 0:
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start : i + 1])
                    except ValueError:
                        break
        start = text.find("{", start + 1)
    raise AIError("模型没有返回可用的结果。", "bad_reply")


class ChatClient:
    def __init__(self, settings: AISettings, timeout_s: float = 60.0, transport=None):
        self.settings = settings
        self.timeout_s = timeout_s
        self.transport = transport  # tests: httpx.MockTransport

    def chat(self, messages: list[dict], max_tokens: int = 4000) -> str:
        """The reply text. Reasoning models (MiniMax M3.x) spend most of
        ``max_tokens`` thinking before the answer, so the budget is generous."""
        s = self.settings
        if not s.configured:
            raise AIError(
                "还没有配置 AI 模型（在设置里填写 API Key）。", "not_configured"
            )
        url = s.base_url.rstrip("/") + "/chat/completions"
        body = {
            **PRESETS.get(s.provider, {}).get("extra_body", {}),
            "model": s.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.3,
        }
        headers = {"Authorization": f"Bearer {s.api_key}"}
        try:
            with httpx.Client(timeout=self.timeout_s, transport=self.transport) as http:
                response = http.post(url, json=body, headers=headers)
        except httpx.TimeoutException as error:
            raise AIError("AI 服务响应超时，已保留本地结果。", "timeout") from error
        except httpx.HTTPError as error:
            raise AIError(
                "连不上 AI 服务（网络不通？），已保留本地结果。", "network"
            ) from error
        if response.status_code in (401, 403):
            raise AIError("API Key 无效或没有权限，请在设置里检查。", "auth")
        if response.status_code == 429:
            raise AIError("额度不足或请求太频繁，请稍后再试。", "quota")
        if response.status_code >= 400:
            detail = ""
            try:
                detail = str(response.json().get("error", {}).get("message", ""))[:120]
            except ValueError:
                pass
            raise AIError(f"AI 服务返回错误 {response.status_code}。{detail}", "error")
        try:
            data = response.json()
            choice = data["choices"][0]
            text = choice["message"].get("content")
        except (ValueError, KeyError, IndexError, TypeError, AttributeError) as error:
            raise AIError("模型没有返回可用的结果。", "bad_reply") from error
        if not text and choice.get("finish_reason") == "length":
            raise AIError("模型想得太久，没来得及回答，请再试一次。", "bad_reply")
        if text is None:
            raise AIError("模型没有返回可用的结果。", "bad_reply")
        if isinstance(text, list):  # content parts
            text = "".join(p.get("text", "") for p in text if isinstance(p, dict))
        return str(text)
