"""Chinese text on OpenCV images (cv2.putText has no CJK glyphs)."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_PATHS = (
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
)
_FONTS: dict[int, ImageFont.ImageFont] = {}


def _font(size: int):
    if size not in _FONTS:
        for path in FONT_PATHS:
            if Path(path).exists():
                _FONTS[size] = ImageFont.truetype(path, size)
                break
        else:
            _FONTS[size] = ImageFont.load_default()
    return _FONTS[size]


def put_text(canvas: np.ndarray, lines, origin=(12, 8)) -> np.ndarray:
    """Draw ``(text, size, BGR colour)`` lines from ``origin`` downwards."""
    image = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image)
    x, y = origin
    for text, size, colour in lines:
        draw.text(
            (x, y), text, font=_font(size), fill=tuple(int(c) for c in reversed(colour))
        )
        y += int(size * 1.3)
    return cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
