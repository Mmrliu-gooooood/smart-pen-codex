"""AI settings in the user's home folder (never in the repository)."""

from __future__ import annotations

import json
import os
import threading
from dataclasses import asdict, dataclass
from pathlib import Path

# Providers with an OpenAI-compatible chat-completions API and image input.
PRESETS = {
    "minimax": {
        "label": "MiniMax",
        "base_url": "https://api.minimax.cn/v1",
        "models": ["MiniMax-M3", "MiniMax-M3.1-Flash"],
        # M3.x always reasons first; on a rough sketch it can think through the
        # whole token budget without answering. "low" keeps it short (live
        # 2026-10-26: 6/6 answered in 10-27 s, vs 0/4 without).
        "extra_body": {"reasoning_effort": "low"},
    },
    "openai": {
        "label": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-4o-mini", "gpt-4o"],
    },
    "openrouter": {
        "label": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "models": [],
    },
    "custom": {"label": "其他（OpenAI 兼容）", "base_url": "", "models": []},
}


def default_path() -> Path:
    return (
        Path(os.environ.get("DIGITAL_PEN_HOME", Path.home() / ".digital_pen"))
        / "ai.json"
    )


@dataclass
class AISettings:
    provider: str = "minimax"
    base_url: str = PRESETS["minimax"]["base_url"]
    model: str = "MiniMax-M3"
    api_key: str = ""

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.base_url and self.model)

    def public(self) -> dict:
        """What the page may see: everything but the key (masked)."""
        k = self.api_key
        masked = (k[:3] + "…" + k[-4:]) if len(k) > 10 else ("已设置" if k else "")
        return {
            "configured": self.configured,
            "provider": self.provider,
            "base_url": self.base_url,
            "model": self.model,
            "key": masked,
        }


class SettingsStore:
    """Load / save / delete the settings file (owner-only permissions where
    the system supports them)."""

    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path else default_path()
        self._lock = threading.Lock()

    def load(self) -> AISettings:
        with self._lock:
            if not self.path.exists():
                return AISettings()
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                return AISettings()
            known = {k: data[k] for k in asdict(AISettings()) if k in data}
            return AISettings(**known)

    def save(self, settings: AISettings) -> None:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(
                json.dumps(asdict(settings), ensure_ascii=False), encoding="utf-8"
            )
            try:
                os.chmod(tmp, 0o600)
            except OSError:
                pass
            tmp.replace(self.path)

    def delete(self) -> None:
        with self._lock:
            if self.path.exists():
                self.path.unlink()

    def update(self, **changes) -> AISettings:
        """Apply changes; an empty or missing api_key keeps the stored one."""
        current = self.load()
        for key in ("provider", "base_url", "model"):
            if changes.get(key):
                setattr(current, key, str(changes[key]).strip())
        if changes.get("api_key"):
            current.api_key = str(changes["api_key"]).strip()
        if current.provider not in PRESETS:
            raise ValueError(f"unknown provider {current.provider!r}")
        if not current.base_url.startswith(
            ("https://", "http://127.0.0.1", "http://localhost")
        ):
            raise ValueError("base URL must start with https://")
        self.save(current)
        return current
