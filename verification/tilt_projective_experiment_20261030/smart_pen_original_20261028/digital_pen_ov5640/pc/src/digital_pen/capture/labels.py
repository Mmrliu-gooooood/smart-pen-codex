"""Pen-tip labels for recorded sessions (Task 9), and tracking suggestions.

labels.json (schema pen-tip-labels-v1) holds one entry per labeled frame:
  stream      "roi" or "overview"
  i           frame index in that stream
  visibility  "tip" (tip visible, position given) | "occluded" (pen in view,
              tip hidden) | "absent" (no pen in view)
  x, y        tip position in full-frame sensor pixels (SVGA), float
  local       tip position inside the stored frame (ROI or overview pixels)
  contact     "down" (touching paper) | "up" (hovering) | "unknown"
  method      "click" | "track" (accepted template suggestion) | "key"
              (a / o keys: absent or occluded)
  sample      sample id the frame belongs to, or null
Writes are atomic (temporary file + replace).
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import cv2
import numpy as np

SCHEMA = "pen-tip-labels-v1"
VISIBILITY = ("tip", "occluded", "absent")
CONTACT = ("down", "up", "unknown")


class LabelStore:
    def __init__(self, path: Path, labeler: str = ""):
        self.path = Path(path)
        self.labeler = labeler
        self.labels: dict[tuple[str, int], dict[str, Any]] = {}
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if data.get("schema") != SCHEMA:
                raise ValueError(f"{self.path}: unknown schema {data.get('schema')!r}")
            for entry in data["labels"]:
                self.labels[(entry["stream"], int(entry["i"]))] = entry

    def set(
        self,
        stream: str,
        i: int,
        visibility: str,
        *,
        local=None,
        frame_xy=None,
        contact: str = "unknown",
        method: str = "click",
        sample: int | None = None,
    ) -> dict:
        if visibility not in VISIBILITY or contact not in CONTACT:
            raise ValueError("bad visibility or contact")
        if visibility == "tip" and (local is None or frame_xy is None):
            raise ValueError("a visible tip needs a position")
        entry = {
            "stream": stream,
            "i": int(i),
            "visibility": visibility,
            "contact": contact,
            "method": method,
            "sample": sample,
            "labeler": self.labeler,
            "time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        if visibility == "tip":
            entry["local"] = [round(float(local[0]), 2), round(float(local[1]), 2)]
            entry["x"] = round(float(frame_xy[0]), 2)
            entry["y"] = round(float(frame_xy[1]), 2)
        self.labels[(stream, int(i))] = entry
        return entry

    def get(self, stream: str, i: int) -> dict | None:
        return self.labels.get((stream, int(i)))

    def remove(self, stream: str, i: int) -> None:
        self.labels.pop((stream, int(i)), None)

    def counts(self) -> dict[str, int]:
        out = {v: 0 for v in VISIBILITY}
        for entry in self.labels.values():
            out[entry["visibility"]] += 1
        out["total"] = len(self.labels)
        return out

    def save(self) -> None:
        entries = sorted(self.labels.values(), key=lambda e: (e["stream"], e["i"]))
        data = {"schema": SCHEMA, "counts": self.counts(), "labels": entries}
        temp = self.path.with_suffix(self.path.suffix + ".tmp")
        temp.write_text(
            json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8"
        )
        temp.replace(self.path)


def to_frame_xy(local, metadata: dict[str, Any], stream: str) -> tuple[float, float]:
    """Stored-frame pixel -> full-frame sensor pixel (ROI offset or overview scale)."""
    if stream == "overview":
        scale = float(metadata.get("scale", 4))
        # Box average: output pixel k covers input pixels [k*s, (k+1)*s).
        return ((local[0] + 0.5) * scale - 0.5, (local[1] + 0.5) * scale - 0.5)
    return (local[0] + metadata.get("x", 0), local[1] + metadata.get("y", 0))


def suggest_by_template(
    previous: np.ndarray,
    previous_xy,
    current: np.ndarray,
    *,
    patch: int = 10,
    search: int = 24,
    min_score: float = 0.6,
):
    """Where the patch around ``previous_xy`` moved to in ``current``.

    Returns (x, y, score) in ``current`` pixels, or None if the patch leaves
    the frame or the best normalised correlation is below ``min_score``.
    """
    x, y = int(round(previous_xy[0])), int(round(previous_xy[1]))
    h, w = previous.shape
    if not (patch <= x < w - patch and patch <= y < h - patch):
        return None
    template = previous[y - patch : y + patch + 1, x - patch : x + patch + 1].astype(
        np.float32
    )
    if template.std() < 2.0:  # flat patch: nothing to track
        return None
    x0, y0 = max(0, x - patch - search), max(0, y - patch - search)
    x1, y1 = min(w, x + patch + search + 1), min(h, y + patch + search + 1)
    window = current[y0:y1, x0:x1].astype(np.float32)
    if window.shape[0] <= template.shape[0] or window.shape[1] <= template.shape[1]:
        return None
    scores = cv2.matchTemplate(window, template, cv2.TM_CCOEFF_NORMED)
    _, best, _, (bx, by) = cv2.minMaxLoc(scores)
    if best < min_score:
        return None
    return (float(x0 + bx + patch), float(y0 + by + patch), float(best))
