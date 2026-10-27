"""Incremental durable journal projection into the unchanged upper-app session.

Actor contract: call only under the app's async mutation lock. SQLite connection
belongs to its lifespan event-loop thread. Data journal never gets edited.
"""
import json
import hashlib
import os
from pathlib import Path
from contextlib import contextmanager
import sqlite3
import time
from pen_bridge import Packet

class LiveView:
    def __init__(self, db, view_id, device, boot_session, page, session,
                 idle_seconds=.5, batch_size=128, max_points=4096):
        from digital_pen.engine.session import SessionStroke
        self.db=sqlite3.connect(db)
        self.db.execute('PRAGMA journal_mode=WAL');self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('CREATE TABLE IF NOT EXISTS pen_views (id TEXT PRIMARY KEY, config TEXT NOT NULL, state TEXT NOT NULL)')
        self.db.execute('CREATE TABLE IF NOT EXISTS pen_view_strokes (view_id TEXT NOT NULL, id INTEGER NOT NULL, data TEXT NOT NULL, PRIMARY KEY(view_id,id))')
        self.db.commit()
        self.id=view_id;self.device=device;self.boot_session=boot_session;self.page=page
        self.session=session;self.idle_seconds=idle_seconds;self.batch_size=batch_size;self.max_points=max_points
        self.cursor=-1;self.previous=None;self.times=[];self.points=[];self.pending=[];self.events=[]
        self.last_arrival=time.monotonic();self.config=json.dumps([device,str(boot_session),page])
        row=self.db.execute('SELECT config,state FROM pen_views WHERE id=?',(view_id,)).fetchone()
        if row:
            if row[0]!=self.config:raise ValueError('view ID belongs to another device/session/page')
            state=json.loads(row[1]);self.cursor=state['cursor'];self.previous=state['previous']
            self.times=state['times'];self.points=state['points']
            for k,v in state['session'].items():setattr(session,k,v)
            session.strokes=[SessionStroke(**json.loads(r[0])) for r in self.db.execute('SELECT data FROM pen_view_strokes WHERE view_id=? ORDER BY id',(view_id,))]
            # Process restart is a known continuity loss, not a silent join.
            self.boundary('restart')
        self.save()
        self.events=[]

    def open_event(self):return {'type':'open','t':self.times[-1] if self.times else 0,'strokes':[list(self.points)] if self.points else []}
    def boundary(self, reason):
        if self.points:
            stroke=self.session.add(self.times,self.points)
            if stroke:
                self.pending.append(stroke)
                self.events.append({'type':'stroke',**stroke.as_dict(),'boundary_reason':reason})
        self.times=[];self.points=[];self.previous=None

    def consume(self,p):
        eligible=p.page==self.page and p.flags&3==3 and p.confidence>=750 and not self.session.finished
        prev=self.previous
        continuous=(prev is not None and eligible and not p.flags&4 and
                    p.seq==prev['seq']+1 and p.page==prev['page'] and
                    0<p.timestamp_us-prev['timestamp_us']<=100000)
        if self.points and (not continuous or len(self.points)>=self.max_points):
            self.boundary('contact_or_loss')
        if eligible:
            self.times.append(p.timestamp_us/1e6);self.points.append([p.x_um/1000,p.y_um/1000])
        self.previous={'seq':p.seq,'page':p.page,'timestamp_us':p.timestamp_us}
        self.cursor=p.seq

    def poll(self,now=None):
        now=time.monotonic() if now is None else now
        frontier=self.db.execute('SELECT through_seq FROM frontiers WHERE device=? AND session=?',(self.device,str(self.boot_session))).fetchone()
        through=frontier[0] if frontier else -1
        rows=self.db.execute('SELECT raw FROM packets WHERE device=? AND session=? AND seq>? AND seq<=? ORDER BY seq LIMIT ?',
                (self.device,str(self.boot_session),self.cursor,through,self.batch_size)).fetchall()
        last=None
        for (raw,) in rows:
            last=Packet.decode(raw);self.consume(last)
        if rows:self.last_arrival=now
        elif self.points and now-self.last_arrival>=self.idle_seconds:self.boundary('transport_timeout')
        if rows or self.events:
            if last:self.events.append({'type':'tip','t':last.timestamp_us/1e6,'frame_id':last.seq,
                    'mm':self.points[-1] if self.points else None,'status':'track' if self.points else 'lost'})
            self.events.append(self.open_event())
            self.save() # persistent projection/cursor before websocket publication
        events=self.events;self.events=[]
        return events

    def save(self, reconcile=False):
        keys=('mode','target','started_utc','finished','line_mm','rotation','generation','_next_id')
        state={'cursor':self.cursor,'previous':self.previous,'times':self.times,'points':self.points,
               'session':{k:getattr(self.session,k) for k in keys}}
        with self.db:
            if reconcile:
                # REST mutations are infrequent; normal polls only insert new strokes.
                self.db.execute('DELETE FROM pen_view_strokes WHERE view_id=?',(self.id,))
                strokes=self.session.strokes
            else:strokes=self.pending
            for s in strokes:
                self.db.execute('INSERT OR REPLACE INTO pen_view_strokes VALUES(?,?,?)',(self.id,s.id,json.dumps(s.as_dict())))
            self.db.execute('INSERT OR REPLACE INTO pen_views VALUES(?,?,?)',(self.id,self.config,json.dumps(state)))
        self.pending=[]

    def discard_open(self):
        self.times=[];self.points=[];self.previous=None
        self.events=[]
    def close(self):self.db.close()

@contextmanager
def view_lease(db, view_id):
    """One projector for a persistent view; OS lock releases after process death."""
    path=Path(db).resolve()
    suffix=hashlib.sha256(view_id.encode()).hexdigest()[:24]
    lock_path=path.with_name(path.name+'.view-'+suffix+'.lock')
    with open(lock_path,'a+b') as f:
        if f.tell()==0:f.write(b'0');f.flush()
        f.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(f.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError as error:
            raise RuntimeError('persistent view already open in another projector') from error
        try:yield
        finally:
            f.seek(0)
            if os.name=='nt':msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
            else:fcntl.flock(f.fileno(),fcntl.LOCK_UN)
