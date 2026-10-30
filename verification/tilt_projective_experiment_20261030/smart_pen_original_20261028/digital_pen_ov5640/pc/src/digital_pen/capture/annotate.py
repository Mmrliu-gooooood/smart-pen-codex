"""Labeling logic for pen tips in a recorded session (no window system).

Candidates are every ``every``-th frame of a stream inside the session's
accepted samples. For each candidate the annotator offers a suggestion:
the last labeled tip within ``max_gap`` candidates, followed into this frame
by template matching (positions are carried in full-frame pixels, so a moved
ROI is handled).
"""

from __future__ import annotations

from pathlib import Path

from digital_pen.capture.labels import LabelStore, suggest_by_template, to_frame_xy
from digital_pen.capture.recorder import load_session


def candidate_frames(samples, reader, stream: str, every: int) -> list[tuple[int, int]]:
    """(frame index, sample id) for every ``every``-th frame of each ok sample."""
    key = "roi_range" if stream == "roi" else "overview_range"
    out = []
    for sample in samples:
        first, last = sample[key]
        if sample["status"] != "ok" or first < 0:
            continue
        last = min(last, len(reader) - 1)
        out += [(i, sample["id"]) for i in range(first, last + 1, max(1, every))]
    return out


class Annotator:
    def __init__(
        self,
        session_dir: Path,
        stream: str = "roi",
        every: int = 5,
        labeler: str = "",
        max_gap: int = 3,
    ):
        self.directory = Path(session_dir)
        self.data = load_session(self.directory)
        self.stream = stream
        self.reader = self.data[stream]
        self.store = LabelStore(self.directory / f"labels-{stream}.json", labeler)
        self.candidates = candidate_frames(
            self.data["samples"], self.reader, stream, every
        )
        self.max_gap = max_gap
        self.contact = "unknown"
        self.position = 0
        # Start at the first unlabeled candidate.
        for k, (i, _) in enumerate(self.candidates):
            if self.store.get(stream, i) is None:
                self.position = k
                break
        else:
            self.position = max(0, len(self.candidates) - 1)
        self._suggestion_cache: dict[int, tuple | None] = {}

    # -- navigation -------------------------------------------------------------

    @property
    def done(self) -> bool:
        return not self.candidates

    def current(self):
        """(frame index, sample id, image, metadata) of the current candidate."""
        i, sample = self.candidates[self.position]
        return i, sample, self.reader.frame(i), self.reader.index[i]

    def step(self, delta: int) -> None:
        if self.candidates:
            self.position = min(max(0, self.position + delta), len(self.candidates) - 1)

    # -- suggestions ------------------------------------------------------------

    def suggestion(self):
        """(local x, local y, score, source frame) or None for the current frame."""
        if not self.candidates:
            return None
        i, sample, image, meta = self.current()
        if i in self._suggestion_cache:
            return self._suggestion_cache[i]
        result = None
        for back in range(1, self.max_gap + 1):
            k = self.position - back
            if k < 0:
                break
            j, other_sample = self.candidates[k]
            if other_sample != sample:
                break
            label = self.store.get(self.stream, j)
            if label is None:
                continue
            if label["visibility"] != "tip":
                break
            prev_meta = self.reader.index[j]
            # Previous tip in full-frame pixels -> this frame's local pixels.
            fx, fy = label["x"], label["y"]
            if self.stream == "roi":
                prev_local = (fx - prev_meta.get("x", 0), fy - prev_meta.get("y", 0))
                shift = (
                    prev_meta.get("x", 0) - meta.get("x", 0),
                    prev_meta.get("y", 0) - meta.get("y", 0),
                )
            else:
                prev_local = tuple(label["local"])
                shift = (0, 0)
            found = suggest_by_template(self.reader.frame(j), prev_local, image)
            if found is not None:
                result = (found[0] + shift[0], found[1] + shift[1], found[2], j)
            break
        self._suggestion_cache[i] = result
        return result

    # -- labeling ---------------------------------------------------------------

    def _label(self, visibility: str, local=None, method: str = "click") -> dict:
        i, sample, _, meta = self.current()
        frame_xy = to_frame_xy(local, meta, self.stream) if local is not None else None
        entry = self.store.set(
            self.stream,
            i,
            visibility,
            local=local,
            frame_xy=frame_xy,
            contact=self.contact if visibility == "tip" else "unknown",
            method=method,
            sample=sample,
        )
        self._suggestion_cache.clear()
        return entry

    def click(self, local_x: float, local_y: float) -> dict:
        entry = self._label("tip", (local_x, local_y), "click")
        self.step(1)
        return entry

    def accept(self) -> dict | None:
        found = self.suggestion()
        if found is None:
            return None
        entry = self._label("tip", (found[0], found[1]), "track")
        self.step(1)
        return entry

    def mark(self, visibility: str) -> dict:
        entry = self._label(visibility, method="key")
        self.step(1)
        return entry

    def set_contact(self, contact: str) -> None:
        """Sticky contact flag for the next tips; also updates the current label."""
        self.contact = contact
        i, *_ = self.current()
        label = self.store.get(self.stream, i)
        if label is not None and label["visibility"] == "tip":
            label["contact"] = contact

    def delete(self) -> None:
        i, *_ = self.current()
        self.store.remove(self.stream, i)
        self._suggestion_cache.clear()

    def save(self) -> None:
        self.store.save()

    def progress(self) -> tuple[int, int]:
        labeled = sum(
            self.store.get(self.stream, i) is not None for i, _ in self.candidates
        )
        return labeled, len(self.candidates)
