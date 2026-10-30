"""Event sources for the engine: recorded runs and the live USB stream.

A source provides ``full_frame`` (the start frame for locating the page) and
yields ``(kind, image, metadata, arrival_s)`` with kind "roi", "overview" or
"page", in device-frame order.

RecordedRun replays a folder written by ``track_pen.py --save-frames`` or a
Task 9 session folder (both: roi.u8/jsonl, overview.u8/jsonl, pages.jsonl
with pages/*.png, start-full.png). ``realtime=True`` paces the events like
the recording; otherwise they come as fast as the engine takes them, which
keeps a replay deterministic.

LiveSource runs the TRACK stream of the board in a reader thread. ROI frames
go through a small queue; when the engine falls behind, the oldest ROI frame
is dropped (never let a backlog build up: the newest frame is what matters
for the ROI and the latency). Device commands (ROI moves, snapshot requests)
are queued and sent by the reader thread between events, so the TRACK
session is only ever used from one thread. ``still()`` asks the reader for
one UXGA (1600x1200) still: it ends the TRACK session, switches mode (with
autofocus), captures, switches back and starts tracking again (photo
finalization, about half a minute). With ``record=DIR`` the reader
also saves every event in the RecordedRun layout, so a live run can be
replayed later.
"""

from __future__ import annotations

import json
import queue
import threading
import time
from concurrent.futures import Future
from pathlib import Path

import cv2
import numpy as np

from digital_pen.capture.recorder import StreamReader, StreamWriter


class RecordedRun:
    def __init__(self, folder: Path, realtime: bool = False):
        self.folder = Path(folder)
        self.realtime = realtime
        self.full_frame = cv2.imread(
            str(self.folder / "start-full.png"), cv2.IMREAD_GRAYSCALE
        )
        if self.full_frame is None:
            raise FileNotFoundError(self.folder / "start-full.png")
        self.dropped = 0

    def events(self):
        roi = StreamReader(self.folder, "roi")
        overview = StreamReader(self.folder, "overview")
        pages = []
        path = self.folder / "pages.jsonl"
        if path.exists():
            pages = [
                json.loads(x)
                for x in path.read_text(encoding="utf-8").splitlines()
                if x.strip()
            ]
        order = [(e["id"], 0, "roi", k) for k, e in enumerate(roi.index)]
        order += [(e["id"], 1, "overview", k) for k, e in enumerate(overview.index)]
        order += [(p["id"], 2, "page", k) for k, p in enumerate(pages)]
        order.sort(key=lambda e: (e[0], e[1]))
        start_wall = time.perf_counter()
        start_device = None
        for _, _, kind, k in order:
            if kind == "page":
                meta = pages[k]
                image = cv2.imread(
                    str(self.folder / meta["file"]), cv2.IMREAD_GRAYSCALE
                )
                if image is None:
                    continue
            else:
                reader = roi if kind == "roi" else overview
                image, meta = np.asarray(reader.frame(k)), dict(reader.index[k])
            if self.realtime and "timestamp_us" in meta:
                t = meta["timestamp_us"] * 1e-6
                start_device = t if start_device is None else start_device
                wait = (t - start_device) - (time.perf_counter() - start_wall)
                if wait > 0:
                    time.sleep(wait)
            yield kind, image, meta, time.monotonic()

    def set_roi(self, roi) -> None:  # recorded: the ROI cannot move
        return None

    def snap(self) -> None:
        return None

    def close(self) -> None:
        return None


class LiveSource:
    """TRACK stream over USB, read in a background thread."""

    def __init__(
        self,
        port: str,
        track_settings: dict,
        roi_size: int = 128,
        queue_size: int = 4,
        record: Path | None = None,
    ):
        from digital_pen.camera import UsbCameraClient

        self.port = port
        self.recoveries = 0  # link reconnects after a failed still/restart
        self.client = UsbCameraClient(port)
        self.client.__enter__()
        status = self.client.status()
        if (status.get("version"), status.get("revision", 0)) < (5, 3):
            raise RuntimeError(f"needs usb_camera firmware v5.3+: {status}")
        if status.get("size") != "svga" or status.get("format") != "gray":
            status = self.client.set_mode("svga", "gray", 10)
        self.status = status
        self.full_frame = self.client.capture().frame.image
        self.track_settings = dict(track_settings)
        self.roi_size = roi_size
        self.frames: queue.Queue = queue.Queue(maxsize=queue_size)
        self.others: queue.Queue = queue.Queue()
        self.commands: queue.Queue = queue.Queue()
        self.dropped = 0
        self.session = None
        self.error = None
        self._stop = threading.Event()
        self._thread = None
        self.record = Path(record) if record is not None else None
        self._writers: dict[str, StreamWriter] = {}
        self._pages_log = None
        if self.record is not None:
            (self.record / "pages").mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(self.record / "start-full.png"), self.full_frame)

    def recapture(self) -> np.ndarray:
        """A new start frame (e.g. when the page was not found: hand on it)."""
        self.full_frame = self.client.capture().frame.image
        if self.record is not None:
            cv2.imwrite(str(self.record / "start-full.png"), self.full_frame)
        return self.full_frame

    def _save(self, event) -> None:
        if event.kind in ("roi", "overview"):
            if event.kind not in self._writers:
                self._writers[event.kind] = StreamWriter(self.record, event.kind)
            self._writers[event.kind].write(
                event.image, event.metadata, event.arrival_s
            )
        elif event.kind == "page":
            if self._pages_log is None:
                self._pages_log = (self.record / "pages.jsonl").open(
                    "a", encoding="utf-8"
                )
            k = sum(1 for _ in (self.record / "pages").glob("page-*.png"))
            name = f"pages/page-{k:04d}.png"
            cv2.imwrite(str(self.record / name), event.image)
            meta = {
                key: event.metadata[key]
                for key in ("id", "timestamp_us", "x", "y")
                if key in event.metadata
            }
            self._pages_log.write(json.dumps({"i": k, "file": name, **meta}) + "\n")
            self._pages_log.flush()

    def start(self, roi) -> None:
        self._roi = tuple(roi)
        self.session = self.client.track(
            tuple(roi), keepalive_ms=3000, **self.track_settings
        )
        self._thread = threading.Thread(
            target=self._read, name="track-reader", daemon=True
        )
        self._thread.start()

    def _read(self) -> None:
        try:
            while True:
                still = self._track()
                if still is None or self._stop.is_set():
                    if still is not None:
                        still.set_exception(RuntimeError("source closed"))
                    break
                try:
                    still.set_result(self._capture_still())
                except Exception as error:  # noqa: BLE001 - handed to the caller
                    still.set_exception(error)
                    self.recoveries += 1
                    self._reconnect()  # the link may be out of step now
                self._restart_track()
        except Exception as error:  # noqa: BLE001 - reported to the consumer
            self.error = f"{type(error).__name__}: {error}"
        finally:
            self.frames.put(None)

    def _reconnect(self) -> None:
        """Open the port again and wait for the board (a failed mode switch
        or capture can leave the link out of step); back to SVGA gray."""
        from digital_pen.camera import UsbCameraClient

        try:
            self.client.__exit__(None, None, None)
        except Exception:  # noqa: BLE001 - the old link may be gone
            pass
        time.sleep(1.0)
        self.client = UsbCameraClient(self.port)
        self.client.__enter__()
        status = self.client.status()
        if status.get("size") != "svga" or status.get("format") != "gray":
            self.client.set_mode("svga", "gray", 10)

    def _restart_track(self, attempts: int = 3) -> None:
        for attempt in range(attempts):
            try:
                self.session = self.client.track(
                    self._roi, keepalive_ms=3000, **self.track_settings
                )
                return
            except Exception:
                if attempt == attempts - 1:
                    raise
                self.recoveries += 1
                self._reconnect()

    def _capture_still(self) -> np.ndarray:
        self.client.set_mode("uxga", "gray", 10)
        try:
            frame = self.client.capture()
            return frame.frame.image if hasattr(frame, "frame") else frame.image
        finally:
            self.client.set_mode("svga", "gray", 10)

    def _track(self) -> Future | None:
        """Run the TRACK session until it ends; returns a pending still
        request if that is why it ended."""
        still = None
        for event in self.session:
            while not self.commands.empty():
                command, value = self.commands.get_nowait()
                if command == "roi":
                    self._roi = tuple(value)
                    self.session.set_roi(value)
                elif command == "snap":
                    self.session.snap()
                elif command == "still" and self.session.end is None:
                    still = value
                    self.session.stop()
            if self._stop.is_set() and self.session.end is None:
                self.session.stop()
            if event.image is None:
                continue
            if self.record is not None:
                self._save(event)
            item = (event.kind, event.image, event.metadata, event.arrival_s)
            if event.kind == "roi":
                try:
                    self.frames.put_nowait(item)
                except queue.Full:
                    try:
                        self.frames.get_nowait()  # drop the oldest frame
                        self.dropped += 1
                    except queue.Empty:
                        pass
                    self.frames.put_nowait(item)
            else:
                self.others.put(item)
        return still

    def events(self):
        while True:
            while not self.others.empty():
                yield self.others.get_nowait()
            item = self.frames.get()
            if item is None:
                while not self.others.empty():
                    yield self.others.get_nowait()
                return
            yield item

    def set_roi(self, roi) -> None:
        self.commands.put(("roi", tuple(roi)))

    def snap(self) -> None:
        self.commands.put(("snap", None))

    def still(self) -> Future:
        """Request one UXGA still (resolved with the gray image)."""
        future: Future = Future()
        self.commands.put(("still", future))
        return future

    def close(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=8)
        if self.session is not None and self.session.end is None:
            try:
                self.session.close()
            except Exception:  # noqa: BLE001 - the link may be gone
                pass
        self.client.__exit__(None, None, None)
        for writer in self._writers.values():
            writer.close()
        if self._pages_log is not None:
            self._pages_log.close()
