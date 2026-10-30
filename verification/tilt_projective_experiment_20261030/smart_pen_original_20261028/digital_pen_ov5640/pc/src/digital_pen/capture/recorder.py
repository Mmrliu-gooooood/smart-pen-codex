"""Raw recording of a TRACK stream for the handwriting dataset (Task 9).

One session = one directory written while the stream runs:

  roi.u8 / roi.jsonl            ROI frames: raw 8-bit rows appended back to
  overview.u8 / overview.jsonl  back (no compression) plus one index line per
                                frame (byte offset, shape, device metadata,
                                PC arrival time)
  pages/page-NNNN.png           page snapshots (lossless PNG) + pages.jsonl
  events.jsonl                  operator marks (paper moved, ROI moved, ...)
  errors.jsonl                  integrity errors reported by the client
  samples.json                  prompted samples: label, time span, frame ranges
  session.json                  session info, counts, device end summary

Frames are flushed as they arrive, so an interrupted session keeps
everything recorded up to that point.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import cv2
import numpy as np

SCHEMA = "handwriting-session-v1"
# Device metadata kept per frame in the index.
FRAME_KEYS = (
    "n",
    "id",
    "timestamp_us",
    "sent_us",
    "age_us",
    "x",
    "y",
    "roi_seq",
    "snap",
    "scale",
)


def _jsonl(path: Path):
    return path.open("a", encoding="utf-8")


class StreamWriter:
    """Appends frames of one kind to ``<name>.u8`` and ``<name>.jsonl``."""

    def __init__(self, directory: Path, name: str):
        self._data = (directory / f"{name}.u8").open("ab")
        self._index = _jsonl(directory / f"{name}.jsonl")
        self._offset = self._data.tell()
        self.count = 0

    def write(
        self, image: np.ndarray, metadata: dict[str, Any], arrival_s: float
    ) -> int:
        image = np.ascontiguousarray(image, dtype=np.uint8)
        self._data.write(image.tobytes())
        entry = {
            "i": self.count,
            "offset": self._offset,
            "shape": list(image.shape),
            "arrival_s": round(arrival_s, 6),
        }
        entry.update({k: metadata[k] for k in FRAME_KEYS if k in metadata})
        self._index.write(json.dumps(entry) + "\n")
        self._offset += image.nbytes
        self.count += 1
        if self.count % 20 == 0:
            self.flush()
        return self.count - 1

    def flush(self) -> None:
        self._data.flush()
        self._index.flush()

    def close(self) -> None:
        self.flush()
        self._data.close()
        self._index.close()


class StreamReader:
    """Random access to a recorded stream (memory-mapped)."""

    def __init__(self, directory: Path, name: str):
        directory = Path(directory)
        index_path = directory / f"{name}.jsonl"
        self.index: list[dict[str, Any]] = []
        if index_path.exists():
            with index_path.open(encoding="utf-8") as handle:
                self.index = [json.loads(line) for line in handle if line.strip()]
        data_path = directory / f"{name}.u8"
        size = data_path.stat().st_size if data_path.exists() else 0
        # Drop index lines whose bytes never reached the disk (interrupted).
        self.index = [
            e for e in self.index if e["offset"] + int(np.prod(e["shape"])) <= size
        ]
        self._data = (
            np.memmap(data_path, np.uint8, "r") if size else np.zeros(0, np.uint8)
        )

    def __len__(self) -> int:
        return len(self.index)

    def frame(self, i: int) -> np.ndarray:
        entry = self.index[i]
        h, w = entry["shape"]
        return np.asarray(
            self._data[entry["offset"] : entry["offset"] + h * w]
        ).reshape(h, w)


@dataclass
class Sample:
    id: int
    label: str
    kind: str
    prompt: str
    start_s: float
    roi: list[int]
    end_s: float | None = None
    status: str = "open"  # open | ok | discarded
    roi_range: list[int] = field(default_factory=lambda: [-1, -1])
    overview_range: list[int] = field(default_factory=lambda: [-1, -1])
    start_device_us: int | None = None
    end_device_us: int | None = None
    notes: str = ""


class SessionRecorder:
    """Writes one session; feed it every TrackEvent with :meth:`add`."""

    def __init__(self, directory: Path, info: dict[str, Any]):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=False)
        (self.directory / "pages").mkdir()
        self.info = {
            "schema": SCHEMA,
            "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            **info,
        }
        self._t0 = time.monotonic()
        self.roi = StreamWriter(self.directory, "roi")
        self.overview = StreamWriter(self.directory, "overview")
        self._pages = _jsonl(self.directory / "pages.jsonl")
        self._events = _jsonl(self.directory / "events.jsonl")
        self._errors = _jsonl(self.directory / "errors.jsonl")
        self.page_count = 0
        self.error_count = 0
        self.samples: list[Sample] = []
        self.end: dict[str, Any] | None = None
        self.last_roi_device_us: int | None = None
        self._write_session()

    # -- time -------------------------------------------------------------------

    def now(self) -> float:
        return time.monotonic() - self._t0

    def _rel(self, arrival_s: float) -> float:
        return arrival_s - self._t0 if arrival_s > 0 else self.now()

    # -- stream -----------------------------------------------------------------

    def add(self, event) -> None:
        """Record one TrackEvent (roi / overview / page / error / reply / end)."""
        arrival = self._rel(event.arrival_s)
        meta = event.metadata
        if event.kind == "roi":
            index = self.roi.write(event.image, meta, arrival)
            self.last_roi_device_us = meta.get("timestamp_us")
            self._extend("roi_range", index)
        elif event.kind == "overview":
            index = self.overview.write(event.image, meta, arrival)
            self._extend("overview_range", index)
        elif event.kind == "page":
            name = f"page-{self.page_count:04d}.png"
            cv2.imwrite(str(self.directory / "pages" / name), event.image)
            entry = {
                "i": self.page_count,
                "file": f"pages/{name}",
                "arrival_s": round(arrival, 6),
                **{
                    k: meta[k]
                    for k in ("snap", "id", "timestamp_us", "x", "y", "width", "height")
                    if k in meta
                },
            }
            self._pages.write(json.dumps(entry) + "\n")
            self._pages.flush()
            self.page_count += 1
        elif event.kind == "error":
            self.error_count += 1
            self._errors.write(
                json.dumps(
                    {
                        "t_s": round(arrival, 6),
                        "error": event.error,
                        "n": meta.get("n"),
                        "kind": meta.get("kind"),
                    }
                )
                + "\n"
            )
            self._errors.flush()
        elif event.kind == "end":
            self.end = meta

    def _extend(self, key: str, index: int) -> None:
        sample = self.samples[-1] if self.samples else None
        if sample is None or sample.status != "open":
            return
        span = getattr(sample, key)
        if span[0] < 0:
            span[0] = index
        span[1] = index

    # -- operator ---------------------------------------------------------------

    def begin_sample(self, label: str, kind: str, prompt: str, roi) -> Sample:
        if self.samples and self.samples[-1].status == "open":
            self.end_sample()
        sample = Sample(
            id=len(self.samples),
            label=label,
            kind=kind,
            prompt=prompt,
            start_s=round(self.now(), 6),
            roi=[int(v) for v in roi],
            start_device_us=self.last_roi_device_us,
        )
        self.samples.append(sample)
        self._write_samples()
        return sample

    def end_sample(self, notes: str = "") -> Sample | None:
        sample = self.samples[-1] if self.samples else None
        if sample is None or sample.status != "open":
            return None
        sample.end_s = round(self.now(), 6)
        sample.end_device_us = self.last_roi_device_us
        sample.status = "ok"
        sample.notes = notes
        self._write_samples()
        return sample

    def discard_last(self) -> Sample | None:
        """Mark the most recent sample as discarded (its frames stay on disk)."""
        for sample in reversed(self.samples):
            if sample.status != "discarded":
                if sample.status == "open":
                    sample.end_s = round(self.now(), 6)
                sample.status = "discarded"
                self._write_samples()
                return sample
        return None

    def mark(self, event: str, **fields) -> None:
        entry = {
            "t_s": round(self.now(), 6),
            "event": event,
            "device_us": self.last_roi_device_us,
            **fields,
        }
        self._events.write(json.dumps(entry, default=float) + "\n")
        self._events.flush()

    # -- files ------------------------------------------------------------------

    def _write_atomic(self, name: str, data: Any) -> None:
        path = self.directory / name
        temp = path.with_suffix(path.suffix + ".tmp")
        temp.write_text(json.dumps(data, indent=1, default=float), encoding="utf-8")
        temp.replace(path)

    def _write_samples(self) -> None:
        self._write_atomic("samples.json", [asdict(s) for s in self.samples])

    def _write_session(self, **extra) -> None:
        self._write_atomic(
            "session.json",
            {
                **self.info,
                **extra,
                "counts": {
                    "roi": self.roi.count,
                    "overview": self.overview.count,
                    "pages": self.page_count,
                    "errors": self.error_count,
                    "samples_ok": sum(s.status == "ok" for s in self.samples),
                    "samples_discarded": sum(
                        s.status == "discarded" for s in self.samples
                    ),
                },
                "device_end": self.end,
            },
        )

    def close(self, **extra) -> None:
        if self.samples and self.samples[-1].status == "open":
            self.end_sample(notes="closed with the session")
        self.roi.close()
        self.overview.close()
        for handle in (self._pages, self._events, self._errors):
            handle.close()
        self._write_samples()
        self._write_session(
            ended_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            duration_s=round(self.now(), 3),
            **extra,
        )


def load_session(directory: Path) -> dict[str, Any]:
    """session.json, samples.json and stream readers of a recorded session."""
    directory = Path(directory)
    pages = []
    if (directory / "pages.jsonl").exists():
        with (directory / "pages.jsonl").open(encoding="utf-8") as handle:
            pages = [json.loads(line) for line in handle if line.strip()]
    return {
        "session": json.loads((directory / "session.json").read_text(encoding="utf-8")),
        "samples": json.loads((directory / "samples.json").read_text(encoding="utf-8")),
        "roi": StreamReader(directory, "roi"),
        "overview": StreamReader(directory, "overview"),
        "pages": pages,
    }
