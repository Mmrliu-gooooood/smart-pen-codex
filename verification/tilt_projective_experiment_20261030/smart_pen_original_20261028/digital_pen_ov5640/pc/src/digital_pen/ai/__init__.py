"""AI gateway (Task 16): the user's own model account, by API key.

The engine server talks to an OpenAI-compatible chat-completions endpoint
(MiniMax, OpenAI, OpenRouter or a custom base URL) for the written feedback
on a practice character and for draw-and-guess. Settings, including the API
key, live in the user's home folder (``~/.digital_pen/ai.json``), never in
the repository, the logs or the browser (the page only sees a masked key).
Without settings, or when the call fails, the page keeps the local results.
"""

from digital_pen.ai.client import AIError, ChatClient
from digital_pen.ai.config import PRESETS, AISettings, SettingsStore
from digital_pen.ai.tasks import evaluate, guess

__all__ = [
    "PRESETS",
    "AIError",
    "AISettings",
    "ChatClient",
    "SettingsStore",
    "evaluate",
    "guess",
]
