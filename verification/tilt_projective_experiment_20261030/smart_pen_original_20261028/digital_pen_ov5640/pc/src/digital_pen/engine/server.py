"""HTTP / WebSocket API of the pen engine (Task 12), localhost only.

  GET  /api/status               health, session summary, service state
  WS   /ws                       {"type":"hello", session} then live events
  POST /api/session/start        {"mode": "practice"|"free"|"draw", "target",
                                  "rotation": 0|90|180|270 (optional)}
  POST /api/session/rotation     {"rotation": 0|90|180|270}, strokes kept
  POST /api/session/finish       final ink correction, {"type":"session"}, then
                                 the final photo: {"type":"scan", status ...}
  POST /api/session/scan         take the final photo again (e.g. pen moved away)
  POST /api/scan/upload          a phone photo of the sheet (body: image bytes)
  GET  /ai/providers | /ai/status   AI gateway (Task 16); the key is never sent back
  POST /ai/config | DELETE /ai/config | POST /ai/test
  POST /ai/evaluate | /ai/guess  written feedback / draw-and-guess by the model
  POST /api/score                local score of the practice character (Task 14);
                                 also sent as {"type":"score"} after finish/scan
  GET  /api/guess/topics         draw-and-guess game topics (Task 18)
  POST /api/guess/offline        offline classifier top-5 for the drawing
  GET  /api/scan.png             the scan of the real ink (RGBA, page mm box)
  POST /api/session/undo         also drops that stroke's ink pieces
  POST /api/session/clear
  GET  /api/session              the session with its strokes (JSON)
  GET  /api/export.svg | .png | .json
  GET  /                         the web page (web/dist), when it is built

Run it through pc/apps/engine.py, which binds 127.0.0.1 only.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import cv2
import numpy as np
from fastapi import (
    Body,
    FastAPI,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from digital_pen.ai import PRESETS, AIError, ChatClient, SettingsStore
from digital_pen.ai import tasks as ai_tasks
from digital_pen.engine.service import EngineService
from digital_pen.guess import EASY, ZH
from digital_pen.guess import default as guess_model


def create_app(
    service: EngineService,
    static_dir: Path | None = None,
    ai_store: SettingsStore | None = None,
    ai_transport=None,
) -> FastAPI:
    app = FastAPI(title="digital pen engine", version="1")
    store = ai_store or SettingsStore()
    session = service.engine.session
    page_info = getattr(service.engine, "page_info", None)
    page = page_info() if page_info is not None else None

    def publish_session() -> dict:
        data = session.to_json()
        service.publish({"type": "session", "session": data})
        return data

    @app.get("/api/status")
    def status():
        return {
            "running": service.running,
            "finished": service.finished,
            "error": service.error,
            "source_error": getattr(service.source, "error", None),
            "source_recoveries": getattr(service.source, "recoveries", 0),
            "health": service.last_health,
            "session": session.summary(),
            "events_sent": service.sent,
            "events_lost": service.lost,
        }

    @app.post("/api/session/start")
    def start(payload: dict = Body(default={})):  # noqa: B008 - FastAPI idiom
        try:
            summary = session.start(
                payload.get("mode", "free"),
                payload.get("target"),
                payload.get("rotation"),
            )
        except ValueError as error:
            raise HTTPException(400, str(error)) from error
        publish_session()
        return summary

    @app.post("/api/session/rotation")
    def set_rotation(payload: dict = Body(default={})):  # noqa: B008 - FastAPI idiom
        try:
            summary = session.set_rotation(payload.get("rotation"))
        except ValueError as error:
            raise HTTPException(400, str(error)) from error
        publish_session()
        return summary

    @app.post("/api/session/finish")
    def finish():
        finalize = getattr(service.engine, "finalize_session", None)
        changed = 0
        if finalize is not None:
            try:
                changed = service.call(finalize).result(timeout=5)
            except TimeoutError:
                changed = None
        summary = session.finish()
        publish_session()
        service.publish_score()  # from the tip path now; from the ink later
        if hasattr(service.engine, "make_scan"):
            service.request_scan()  # photo finalization, in the background
        return {**summary, "corrected": changed}

    @app.post("/api/session/undo")
    def undo():
        stroke = session.undo()
        service.publish({"type": "undo", "id": None if stroke is None else stroke.id})
        undo_ink = getattr(service.engine, "undo_ink", None)
        if stroke is not None and undo_ink is not None:
            try:
                event = service.call(lambda: undo_ink(stroke.t0, stroke.t1)).result(5)
            except TimeoutError:
                event = None
            if event is not None:
                service.publish(event)
        return {"undone": None if stroke is None else stroke.id, **session.summary()}

    @app.post("/api/session/clear")
    def clear():
        session.clear()
        service.publish({"type": "clear"})
        return session.summary()

    @app.get("/api/session")
    def get_session():
        return JSONResponse(session.to_json())

    @app.get("/api/export.json")
    def export_json():
        return Response(
            session.to_json_bytes(),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=strokes.json"},
        )

    @app.post("/api/score")
    def score_now():
        scorer = getattr(service.engine, "score_session", None)
        if scorer is None:
            raise HTTPException(400, "this engine cannot score")
        try:
            event = scorer()
        except ValueError as error:
            raise HTTPException(400, str(error)) from error
        service.publish(event)
        return event

    @app.get("/api/guess/topics")
    def guess_topics():
        return [{"key": k, "label": ZH[k]} for k in EASY]

    @app.post("/api/guess/offline")
    def guess_offline():
        """Top-5 guesses of the offline classifier for the current drawing
        (Task 18); a few milliseconds, no network."""
        model = guess_model()
        if model is None:
            return {"available": False, "guesses": []}
        lines = session.upright_polylines()
        return {"available": True, "guesses": model.guess(lines, k=5) if lines else []}

    @app.post("/api/session/scan")
    def retake():
        if not hasattr(service.engine, "make_scan"):
            raise HTTPException(400, "this engine cannot take photos")
        service.request_scan()
        return {"requested": True}

    @app.post("/api/scan/upload")
    async def upload(request: Request):
        """A phone photo of the sheet (raw image bytes as the body)."""
        data = await request.body()
        if len(data) > 25 * 2**20:
            raise HTTPException(413, "photo larger than 25 MB")
        image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise HTTPException(400, "not an image")
        if not hasattr(service.engine, "make_scan"):
            raise HTTPException(400, "this engine cannot scan photos")
        try:
            return await run_in_threadpool(service.scan_photo, image)
        except Exception as error:  # noqa: BLE001 - reported to the page
            raise HTTPException(422, f"page not found in the photo: {error}") from error

    @app.get("/api/scan.png")
    def scan_png():
        data = session.scan_png()
        if data is None:
            raise HTTPException(404, "no scan yet")
        return Response(
            data, media_type="image/png", headers={"Cache-Control": "no-store"}
        )

    @app.get("/api/export.svg")
    def export_svg():
        return Response(session.to_svg(), media_type="image/svg+xml")

    @app.get("/api/export.png")
    def export_png():
        return Response(session.to_png(), media_type="image/png")

    @app.websocket("/ws")
    async def events(ws: WebSocket):
        await ws.accept()
        q = service.subscribe()
        try:
            await ws.send_json(
                {
                    "type": "hello",
                    "session": session.to_json(),
                    "page": page,
                    "health": service.last_health,
                }
            )
            while True:
                event = await q.get()
                await ws.send_json(event)
        except (WebSocketDisconnect, asyncio.CancelledError, RuntimeError):
            pass
        finally:
            service.unsubscribe(q)

    # -- AI gateway (Task 16): the user's own model account, by API key -------

    def ai_failure(error: AIError) -> HTTPException:
        status = 503 if error.kind == "not_configured" else 502
        return HTTPException(status, {"message": str(error), "kind": error.kind})

    def ai_client() -> ChatClient:
        return ChatClient(store.load(), transport=ai_transport)

    @app.get("/ai/providers")
    def ai_providers():
        return PRESETS

    @app.get("/ai/status")
    def ai_status():
        return store.load().public()

    @app.post("/ai/config")
    def ai_config(payload: dict = Body(default={})):  # noqa: B008 - FastAPI idiom
        try:
            settings = store.update(**payload)
        except ValueError as error:
            raise HTTPException(400, str(error)) from error
        return settings.public()

    @app.delete("/ai/config")
    def ai_forget():
        store.delete()
        return store.load().public()

    @app.post("/ai/test")
    def ai_test():
        try:
            return {"ok": True, "reply": ai_tasks.ping(ai_client())}
        except AIError as error:
            raise ai_failure(error) from error

    def evaluate_now(target: str) -> dict:
        """Written feedback on the practice character: the final photo (or
        the strokes) plus the local score go to the model. Progress and the
        result go out as ``ai_evaluation`` events (pending / done / failed);
        raises AIError after publishing the failure."""
        settings = store.load()
        source = "scan" if session.scan is not None else "strokes"
        service.publish({"type": "ai_evaluation", "status": "pending", "char": target})
        scorer = getattr(service.engine, "score_session", None)
        score = None
        if scorer is not None:
            try:
                score = scorer()
            except ValueError:
                score = None
        try:
            result = ai_tasks.evaluate(
                ChatClient(settings, transport=ai_transport),
                session.to_png(),
                target,
                score,
            )
        except AIError as error:
            service.publish(
                {
                    "type": "ai_evaluation",
                    "status": "failed",
                    "char": target,
                    "error": str(error),
                }
            )
            raise
        event = {
            "type": "ai_evaluation",
            "status": "done",
            "char": target,
            "model": settings.model,
            "source": source,
            **result,
        }
        service.publish(event)
        return event

    auto = {"done_for": None}

    def auto_evaluate() -> None:
        """Once per practice character, after the photo finalization (Task
        17): only with a configured model; runs on the scan thread."""
        target = session.target
        if session.mode != "practice" or not target or not store.load().configured:
            return
        key = session.generation  # changes on start and clear
        if auto["done_for"] == key:
            return
        auto["done_for"] = key
        try:
            evaluate_now(target)
        except AIError:
            pass  # already on the page; the local feedback stands

    service.after_scan = auto_evaluate

    @app.post("/ai/evaluate")
    def ai_evaluate():
        target = session.target
        if session.mode != "practice" or not target:
            raise HTTPException(400, "AI 评语只用于练字模式")
        try:
            return evaluate_now(target)
        except AIError as error:
            raise ai_failure(error) from error

    @app.post("/ai/guess")
    def ai_guess():
        if not session.strokes and session.scan is None:
            raise HTTPException(400, "还没有画")
        try:
            result = ai_tasks.guess(ai_client(), session.to_png())
        except AIError as error:
            raise ai_failure(error) from error
        event = {"type": "ai_guess", **result}
        service.publish(event)
        return event

    if static_dir is not None and (static_dir / "index.html").exists():
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="web")
    return app
