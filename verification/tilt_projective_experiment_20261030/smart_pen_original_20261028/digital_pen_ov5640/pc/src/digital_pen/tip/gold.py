"""Precise re-labeling of pen tips for evaluation ("gold" labels, Task 10).

The Task 9 labels were clicked at 4x zoom with a tracking suggestion; their
noise (about 1 px) is close to the 1 mm gate (about 2.6 px). The gold set
re-labels a fixed sample of test frames more carefully: 8x zoom, sub-pixel
clicks with 1/8 px nudges, neighbouring frames and the session's final ink
on demand. Evaluation sets are labeled twice in two independently shuffled
passes (pass B never shows pass A), which measures the labeler's own
repeatability; training sets (precise targets for retraining) once.

gold-labels.json (schema tip-gold-v1):
  items   the fixed sample: session folder, frame index, the Task 9 label
          (hidden while labeling), the crop shown, contact flag
  passes  {"A": {item_id: entry}, "B": {...}} (or only "A"), entry = {status: "tip" |
          "unsure", x, y (ROI-frame pixels), time_utc}
  order   the shuffled item order of each pass
Writes are atomic (temporary file + replace).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import cv2
import numpy as np

SCHEMA = "tip-gold-v1"
PASSES = ("A", "B")


def select_items(labels, total: int, crop: int, seed: int = 0) -> list[dict]:
    """Stratified sample of visible-tip labels, about ``total``, per session.

    ``labels``: dicts with session, i, local (x, y), contact, shape (h, w).
    The crop shown is centred near the old label with a random offset, so the
    tip is not always in the middle (the old position is not given away).
    """
    rng = np.random.default_rng(seed)
    tips = [label for label in labels if label["local"] is not None]
    by_session: dict[str, list[dict]] = {}
    for label in tips:
        by_session.setdefault(label["session"], []).append(label)
    items = []
    for session in sorted(by_session):
        group = by_session[session]
        count = max(1, round(total * len(group) / len(tips)))
        for k in sorted(rng.choice(len(group), min(count, len(group)), replace=False)):
            label = group[k]
            h, w = label["shape"]
            size = min(crop, h, w)
            centre = np.asarray(label["local"]) + rng.uniform(-0.2, 0.2, 2) * size
            x0 = int(np.clip(round(centre[0] - size / 2), 0, w - size))
            y0 = int(np.clip(round(centre[1] - size / 2), 0, h - size))
            items.append(
                {
                    "id": f"{session.split('_')[0]}#{label['i']}",
                    "session": session,
                    "i": int(label["i"]),
                    "old": [float(v) for v in label["local"]],
                    "contact": label.get("contact", "unknown"),
                    "crop": [x0, y0, size, size],
                }
            )
    return items


class GoldStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.data = json.loads(self.path.read_text(encoding="utf-8"))
        if self.data.get("schema") != SCHEMA:
            raise ValueError(f"{self.path}: unknown schema {self.data.get('schema')!r}")
        self.items = {item["id"]: item for item in self.data["items"]}
        self.passes = tuple(name for name in PASSES if name in self.data["passes"])

    @classmethod
    def create(
        cls, path: Path, items: list[dict], seed: int = 0, passes=PASSES, **info
    ) -> GoldStore:
        if not passes or any(name not in PASSES for name in passes):
            raise ValueError(f"passes must be a subset of {PASSES}")
        rng = np.random.default_rng(seed + 1)
        ids = [item["id"] for item in items]
        order = {name: [ids[k] for k in rng.permutation(len(ids))] for name in passes}
        data = {
            "schema": SCHEMA,
            "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            **info,
            "items": items,
            "order": order,
            "passes": {name: {} for name in passes},
        }
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        _write(path, data)
        return cls(path)

    def entry(self, name: str, item_id: str) -> dict | None:
        return self.data["passes"][name].get(item_id)

    def set(self, name: str, item_id: str, status: str, xy=None) -> dict:
        if status not in ("tip", "unsure") or item_id not in self.items:
            raise ValueError("bad status or item")
        if status == "tip" and xy is None:
            raise ValueError("a tip needs a position")
        entry = {
            "status": status,
            "time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        if status == "tip":
            entry["x"] = round(float(xy[0]), 3)
            entry["y"] = round(float(xy[1]), 3)
        self.data["passes"][name][item_id] = entry
        return entry

    def remove(self, name: str, item_id: str) -> None:
        self.data["passes"][name].pop(item_id, None)

    def order(self, name: str) -> list[str]:
        return list(self.data["order"][name])

    def progress(self, name: str) -> tuple[int, int]:
        return len(self.data["passes"][name]), len(self.items)

    def current_pass(self) -> str | None:
        """The first pass not finished (A before B), or None when all are."""
        for name in self.passes:
            done, total = self.progress(name)
            if done < total:
                return name
        return None

    def save(self) -> None:
        _write(self.path, self.data)


def _write(path: Path, data) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    temp.replace(path)


def final_ink(frames: list[np.ndarray]) -> np.ndarray:
    """Ink mask (uint8 0/1) from hand-free frames of one fixed ROI.

    Median of the frames, black-hat (dark details), then connected components
    smaller than a printed dot cluster are dropped, leaving the strokes.
    """
    background = np.median(np.stack(frames).astype(np.float32), 0)
    blackhat = (
        cv2.morphologyEx(background, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
        - background
    )
    mask = (blackhat > max(12, np.percentile(blackhat, 97) * 0.6)).astype(np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    keep = np.zeros(count, bool)
    keep[1:] = stats[1:, cv2.CC_STAT_AREA] >= 25
    return keep[labels].astype(np.uint8)


def gold_tips(store: GoldStore) -> dict[str, tuple[float, float]]:
    """Item id -> gold tip: the mean over passes, only where every pass gave a tip."""
    out = {}
    for item_id in store.items:
        entries = [store.entry(name, item_id) for name in store.passes]
        if all(e is not None and e["status"] == "tip" for e in entries):
            out[item_id] = (
                float(np.mean([e["x"] for e in entries])),
                float(np.mean([e["y"] for e in entries])),
            )
    return out


def session_ink(roi, samples) -> np.ndarray:
    """Final ink of a recorded session: the last frames after the last sample
    (the hand is moved away before the session ends)."""
    last = max(s["roi_range"][1] for s in samples if s["status"] == "ok")
    n = len(roi)
    idx = list(range(max(last + 1, n - 40), n)) or [n - 1]
    return final_ink([roi.frame(i) for i in idx])


def display_to_frame(point, crop, zoom: int) -> tuple[float, float]:
    """Display pixel of the zoomed crop -> ROI-frame pixel (pixel centres at
    integers, the convention of cv2.resize and the Task 9 labels)."""
    return (
        (point[0] + 0.5) / zoom - 0.5 + crop[0],
        (point[1] + 0.5) / zoom - 0.5 + crop[1],
    )


def frame_to_display(xy, crop, zoom: int) -> tuple[float, float]:
    return (
        (xy[0] - crop[0] + 0.5) * zoom - 0.5,
        (xy[1] - crop[1] + 0.5) * zoom - 0.5,
    )
