"""Engine service: source + engine in a thread, events broadcast (Task 12).

``EngineService.start()`` runs the source through the engine in a background
thread. Output events go to every subscriber's bounded asyncio queue (a slow
browser loses events rather than growing memory); each event gets
``sent`` (PC monotonic seconds when queued) and frame-derived timing.

Live mode (``sync=False``): page snapshot checks, the coarse overview
search of a lost pen and the ink vectorization run in worker threads, so the
frame loop never waits for them; ROI and snapshot requests from the engine
go back to the source.
Replay mode (``sync=True``): everything runs in order in the engine thread,
so outputs are reproducible.
"""

from __future__ import annotations

import asyncio
import json
import queue
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor

import cv2
import numpy as np

from digital_pen.engine.core import Engine


class EngineService:
    def __init__(self, engine: Engine, source, *, sync: bool = True, roi_start=None):
        self.engine = engine
        self.source = source
        self.sync = sync
        self.roi_start = roi_start or engine.start_roi()
        self.subscribers: set[tuple[asyncio.AbstractEventLoop, asyncio.Queue]] = set()
        self.last_health: dict | None = None
        self.running = False
        self.finished = False
        self.error: str | None = None
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self.sent = 0
        self.lost = 0
        self._calls: queue.Queue = queue.Queue()
        self.after_scan = None  # callable, set by the server (AI comment)

    # -- subscribers ----------------------------------------------------------------

    def subscribe(self, maxsize: int = 512) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=maxsize)
        with self._lock:
            self.subscribers.add((asyncio.get_running_loop(), q))
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        with self._lock:
            self.subscribers = {s for s in self.subscribers if s[1] is not q}

    def publish(self, event: dict) -> None:
        event["sent"] = round(time.monotonic(), 6)
        if event.get("type") == "health":
            self.last_health = event
        with self._lock:
            targets = list(self.subscribers)
        for loop, q in targets:
            loop.call_soon_threadsafe(self._offer, q, event)
        self.sent += 1

    def _offer(self, q: asyncio.Queue, event: dict) -> None:
        try:
            q.put_nowait(event)
        except asyncio.QueueFull:
            self.lost += 1

    # -- engine-thread calls -----------------------------------------------------------

    def call(self, fn) -> Future:
        """Run ``fn()`` on the engine thread between events (the engine is not
        thread-safe); directly when the engine is not running."""
        future: Future = Future()
        if self.running and self._thread is not None and self._thread.is_alive():
            self._calls.put((fn, future))
        else:
            self._invoke(fn, future)
        return future

    @staticmethod
    def _invoke(fn, future: Future) -> None:
        try:
            future.set_result(fn())
        except Exception as error:  # noqa: BLE001 - handed to the caller
            future.set_exception(error)

    def _drain_calls(self) -> None:
        while True:
            try:
                fn, future = self._calls.get_nowait()
            except queue.Empty:
                return
            self._invoke(fn, future)

    # -- photo finalization -----------------------------------------------------------

    def request_scan(self) -> None:
        """Take the final photo in the background: a UXGA still from the
        board (live), else the latest page snapshot; then the scan. Progress
        goes out as ``scan`` events."""
        threading.Thread(target=self._scan_then, name="scan", daemon=True).start()

    def _scan_then(self) -> None:
        """The scan, then ``after_scan`` (the automatic AI comment, Task 17)
        whether or not the photo worked: without one it uses the strokes."""
        try:
            self._scan_job()
        finally:
            if self.after_scan is not None:
                self.after_scan()

    def _scan_job(self) -> None:
        self.publish({"type": "scan", "status": "capturing"})
        image, source, error = None, None, None
        still = getattr(self.source, "still", None)
        if still is not None and self.running:
            try:
                image, source = still().result(timeout=120), "uxga"
            except Exception as failure:  # noqa: BLE001 - fall back below
                error = f"{type(failure).__name__}: {failure}"
        if image is None and self.engine.last_page_image is not None:
            image, source = self.engine.last_page_image, "svga"
        if image is None:
            self.publish({"type": "scan", "status": "failed", "error": error})
            return
        record = getattr(self.source, "record", None)
        if record is not None:
            cv2.imwrite(str(record / f"still-{source}.png"), image)
        try:
            scan = self.engine.make_scan(image)
        except Exception as failure:  # noqa: BLE001 - reported to the page
            self.publish(
                {
                    "type": "scan",
                    "status": "failed",
                    "error": f"{type(failure).__name__}: {failure}",
                }
            )
            return
        meta = self.engine.session.set_scan(scan, source)
        self.publish(
            {"type": "scan", "status": "done", "fallback_error": error, **meta}
        )
        self.rebuild_strokes()
        self.publish_score()  # again, now from the real ink

    def scan_photo(self, image) -> dict:
        """An uploaded photo of the sheet becomes the session's scan (call
        from a worker thread; raises if the page is not found in it)."""
        self.publish({"type": "scan", "status": "capturing", "source": "photo"})
        try:
            scan = self.engine.make_scan(image, photo=True)
        except Exception as failure:
            self.publish(
                {
                    "type": "scan",
                    "status": "failed",
                    "error": f"{type(failure).__name__}: {failure}",
                }
            )
            raise
        meta = self.engine.session.set_scan(scan, "photo")
        self.publish({"type": "scan", "status": "done", **meta})
        self.rebuild_strokes()
        self.publish_score()
        return meta

    def rebuild_strokes(self) -> int:
        """Strokes rebuilt from the new photo + tip path (if the engine can),
        sent as a ``session`` event so the page redraws them."""
        rebuild = getattr(self.engine, "rebuild_strokes", None)
        if rebuild is None:
            return 0
        try:
            n = rebuild()
        except Exception as failure:  # noqa: BLE001 - the tip strokes stay
            print(f"stroke rebuild failed: {type(failure).__name__}: {failure}")
            return 0
        if n:
            self.publish({"type": "session", "session": self.engine.session.to_json()})
        return n

    def publish_score(self) -> dict | None:
        """Score the practice character and send it (None if not practice)."""
        session = self.engine.session
        if session.mode != "practice" or not session.target:
            return None
        scorer = getattr(self.engine, "score_session", None)
        if scorer is None:
            return None
        try:
            event = scorer()
        except ValueError:
            return None
        self.publish(event)
        self._save_sample(event)
        return event

    def _save_sample(self, event: dict) -> None:
        """Recording (--record): keep each final practice score with its
        photo under samples/, for rating by hand (Task 14 gate)."""
        record = getattr(self.source, "record", None)
        if record is None or event.get("shape_from") != "ink":
            return
        session = self.engine.session
        with session._lock:
            gray = None if session.scan is None else session.scan["gray"]
        if gray is None:
            return
        folder = record / "samples"
        folder.mkdir(parents=True, exist_ok=True)
        n = len(list(folder.glob("*.json")))
        stem = f"{n:03d}-{event['char']}"
        # cv2.imwrite cannot take non-ASCII paths on Windows (the character)
        ok, png = cv2.imencode(".png", np.rot90(gray, session.rotation // 90))
        if ok:
            (folder / f"{stem}.png").write_bytes(png.tobytes())
        data = {"score": event, "session": session.to_json()}
        (folder / f"{stem}.json").write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8"
        )

    # -- running ----------------------------------------------------------------------

    def start(self) -> None:
        if hasattr(self.source, "start"):
            self.source.start(self.roi_start)
        self.running = True
        self._thread = threading.Thread(target=self._run, name="engine", daemon=True)
        self._thread.start()

    def join(self, timeout: float | None = None) -> None:
        if self._thread is not None:
            self._thread.join(timeout)

    def stop(self) -> None:
        self.running = False
        self.source.close()
        self.join(10)

    def _run(self) -> None:
        engine = self.engine
        pages = ThreadPoolExecutor(max_workers=1) if not self.sync else None
        searches = ThreadPoolExecutor(max_workers=1) if not self.sync else None
        inks = ThreadPoolExecutor(max_workers=1) if not self.sync else None
        ink_jobs: list = []  # (job, future), committed in order
        page_job = search_job = None
        try:
            for kind, image, meta, arrival in self.source.events():
                if not self.running:
                    break
                self._drain_calls()
                if page_job is not None and page_job.done():
                    for event in page_job.result():
                        self.publish(event)
                    page_job = None
                if search_job is not None and search_job.done():
                    det, smeta = search_job.result()
                    result = engine.pipeline.apply_overview(det, smeta)
                    if result is not None and result.roi is not None:
                        engine.roi_requests.append(result.roi)
                    search_job = None
                while ink_jobs and ink_jobs[0][1].done():
                    job, future = ink_jobs.pop(0)
                    for event in engine.commit_ink(job, future.result()):
                        self.publish(event)
                if not self.sync and kind == "page":
                    if page_job is None:
                        page_job = pages.submit(engine.check_page, image, meta)
                    continue
                if not self.sync and kind == "overview":
                    # a still track on a static scene is dropped; lost, or
                    # still on one spot for a while (it may be a mark on the
                    # paper while the pen is elsewhere): search the overview
                    engine.pipeline.note_overview(image, meta)
                    if search_job is None and engine.pipeline.needs_overview(meta):
                        search_job = searches.submit(
                            _search, engine, image.copy(), meta
                        )
                    continue
                for event in engine.on_event(kind, image, meta):
                    if event["type"] == "tip":
                        event["arrival"] = round(arrival, 6)
                    self.publish(event)
                while engine.roi_requests:
                    self.source.set_roi(engine.roi_requests.pop(0))
                while getattr(engine, "ink_jobs", None):
                    job = engine.ink_jobs.pop(0)
                    ink_jobs.append((job, inks.submit(engine.ink.compute, job)))
                while engine.snap_requests:
                    engine.snap_requests -= 1
                    self.source.snap()
                engine.health.dropped = getattr(self.source, "dropped", 0)
            for event in engine.flush():
                self.publish(event)
            source_error = getattr(self.source, "error", None)
            print(f"stream ended (source error: {source_error})", flush=True)
            self.publish({"type": "end", "error": source_error})
        except Exception as error:  # noqa: BLE001 - reported to clients
            self.error = f"{type(error).__name__}: {error}"
            self.publish({"type": "end", "error": self.error})
        finally:
            for pool in (pages, searches, inks):
                if pool is not None:
                    pool.shutdown(wait=True)
            self.running = False
            self.finished = True
            self._drain_calls()


def _search(engine: Engine, image, meta):
    """Coarse overview search in a worker; touches no tracker state."""
    return engine.pipeline.search_overview(image, meta), meta
