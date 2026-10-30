"""Reuse the actual existing Windows/web engine API for durable coordinate replay.

Requires original digital_pen PC package on PYTHONPATH. No camera is constructed.
One selected device/session/page per view; no automatic cross-page overlay.
"""
import argparse
import asyncio
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from types import SimpleNamespace
from pen_bridge import Journal,stroke_events

def build_app(db, device, boot_session, page, static_dir=None, *, live=False, view_id=None, poll_seconds=.05, idle_seconds=.5):
    if live and (not view_id or not .01 <= poll_seconds <= 1 or idle_seconds < .1):
        raise ValueError("live requires view_id, poll .01..1s and idle >=.1s")
    from digital_pen.engine.core import Engine
    from digital_pen.engine.session import WritingSession
    from digital_pen.engine.service import EngineService
    from digital_pen.engine.server import create_app
    class CoordinateEngine:
        score_session=Engine.score_session # original scoring, unchanged
        def __init__(self):self.session=WritingSession()
    engine=CoordinateEngine()
    # Service is used only as existing publisher/REST adapter, never .start().
    service=EngineService(engine,SimpleNamespace(error=None,recoveries=0),roi_start=(0,0,1,1))
    engine.session.start('free')
    if not live:
        active_page=None;times=[];points=[]
        with Journal(db) as journal:
            for event in stroke_events(journal.replay(device,boot_session)):
                if event['type']=='start':
                    active_page=event['page'];times=[];points=[]
                elif event['type']=='point' and active_page==page:
                    times.append(event['timestamp_us']/1e6)
                    points.append([event['x_mm'],event['y_mm']])
                elif event['type']=='end' and points:
                    stroke=engine.session.add(times,points)
                    if stroke:service.publish({'type':'stroke',**stroke.as_dict()})
                    times=[];points=[]
    app=create_app(service,static_dir=Path(static_dir) if static_dir else None)
    # Helpful explicit provenance outside unchanged original event schema.
    @app.get('/api/pen/provenance')
    def provenance():
        return {'source':'durable-coordinate-live' if live else 'durable-coordinate-replay','camera':False,'device':device,
                'boot_session':str(boot_session),'page':page,
                'physical_accuracy_verified':False,'live_journal_subscription':live,
                'view_id':view_id if live else None}
    if live:
        from live_view import LiveView, view_lease
        lock=asyncio.Lock()
        publish=service.publish
        deferred=None
        def buffered_publish(event):
            if deferred is not None:deferred.append(event)
            else:publish(event)
        service.publish=buffered_publish
        old_offer=service._offer
        def bounded_offer(queue,event):
            if queue.full():
                service.lost+=1
                while not queue.empty():queue.get_nowait()
                # Replace obsolete backlog with authoritative state, not missing ink.
                queue.put_nowait({'type':'session','session':engine.session.to_json()})
                if queue.maxsize>1:queue.put_nowait(app.state.pen_view.open_event())
            else:old_offer(queue,event)
        service._offer=bounded_offer
        subscribe=service.subscribe
        def subscribe_with_open(maxsize=512):
            queue=subscribe(maxsize)
            queue.put_nowait(app.state.pen_view.open_event())
            return queue
        service.subscribe=subscribe_with_open

        @asynccontextmanager
        async def lifespan(_):
            with view_lease(db,view_id):
                # Create raw journal tables if this is the first process to start.
                with Journal(db):pass
                view=LiveView(db,view_id,device,boot_session,page,engine.session,idle_seconds)
                app.state.pen_view=view
                service.running=True
                async def tail():
                    while True:
                        try:
                            async with lock:
                                for event in view.poll():publish(event)
                        except Exception as error:
                            service.running=False
                            service.error=f'live projection stopped: {error}'
                            publish({'type':'end','error':service.error})
                            return # fail closed; no partial cursor retry/duplicate rendering
                        await asyncio.sleep(poll_seconds)
                task=asyncio.create_task(tail())
                try:yield
                finally:
                    task.cancel()
                    with suppress(asyncio.CancelledError):await task
                    service.running=False
                    view.close()
        app.router.lifespan_context=lifespan

        @app.middleware('http')
        async def serialize_mutations(request,call_next):
            nonlocal deferred
            if request.method not in ('POST','DELETE','PUT','PATCH'):
                return await call_next(request)
            async with lock:
                view=app.state.pen_view
                deferred=[]
                try:
                    if request.url.path=='/api/session/finish':
                        view.boundary('user_finish')
                        view.save()
                        deferred.extend(view.events);view.events=[]
                        deferred.append(view.open_event())
                    response=await call_next(request)
                    if response.status_code<400:
                        if request.url.path in ('/api/session/start','/api/session/clear','/api/session/undo'):
                            view.discard_open()
                            if request.url.path!='/api/session/undo':
                                row=view.db.execute('SELECT through_seq FROM frontiers WHERE device=? AND session=?',(device,str(boot_session))).fetchone()
                                if row:view.cursor=max(view.cursor,row[0])
                            deferred.append(view.open_event())
                        view.save(reconcile=True)
                    events=deferred;deferred=None
                    for event in events:publish(event)
                    return response
                finally:deferred=None
    app.state.pen_service=service
    return app

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db',required=True);p.add_argument('--device',type=int,required=True)
    p.add_argument('--session',type=int,required=True);p.add_argument('--page',type=int,required=True)
    p.add_argument('--live',action='store_true');p.add_argument('--view-id')
    p.add_argument('--static-dir');p.add_argument('--port',type=int,default=8765)
    a=p.parse_args()
    import uvicorn
    uvicorn.run(build_app(a.db,a.device,a.session,a.page,a.static_dir,live=a.live,view_id=a.view_id),host='127.0.0.1',port=a.port)
if __name__=='__main__':main()
