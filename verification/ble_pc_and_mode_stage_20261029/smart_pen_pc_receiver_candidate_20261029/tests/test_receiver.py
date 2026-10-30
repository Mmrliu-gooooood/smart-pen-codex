import asyncio
from contextlib import suppress
import dataclasses
from pathlib import Path
import sqlite3
import tempfile
import threading
from types import SimpleNamespace
import unittest

from pen_receiver.journal import Binding, Journal
from pen_receiver.protocol import ACK, EXPECTED_INFO, INFO, SERVICE, TX, Record, decode_ack, fragments
from pen_receiver.receiver import ReceiverError, receive

B = Binding('bench-one', 'explicit-test-target', 42)
R = Record(7, 42, 2**64-1, 0, 10, 9, -1234, 5678, 1000)


async def yes(): return True
async def no(): return False


class MockClient:
    def __init__(self, target, *, pair, timeout, disconnected_callback):
        self.target, self.pair, self.timeout = target, pair, timeout
        self.disconnect_cb = disconnected_callback
        self.is_connected = False
        self.services = [SimpleNamespace(uuid=SERVICE, characteristics=[
            SimpleNamespace(uuid=TX, properties=['notify']),
            SimpleNamespace(uuid=ACK, properties=['write']),
            SimpleNamespace(uuid=INFO, properties=['read'])])]
        self.info = EXPECTED_INFO
        self.writes = []
        self.notifications = None
        self.runner = None
        self.ack_event = asyncio.Event()
        self.script = None
        self.write_hook = None
        self.probe_error = None
        self.reads = 0

    async def __aenter__(self):
        self.is_connected = True
        return self
    async def __aexit__(self, *args):
        self.drop()
        if self.runner:
            self.runner.cancel()
            with suppress(asyncio.CancelledError): await self.runner
    def drop(self):
        self.is_connected = False
        self.disconnect_cb(self)
    async def read_gatt_char(self, characteristic, *, use_cached):
        assert characteristic.uuid == INFO and use_cached is False
        self.reads += 1
        if self.reads == 1 and self.probe_error: raise self.probe_error
        return self.info
    async def start_notify(self, characteristic, callback):
        assert characteristic.uuid == TX
        self.notifications = callback
        self.runner = asyncio.create_task(self.script(self))
    async def stop_notify(self, characteristic): assert characteristic.uuid == TX
    def send(self, payload): self.notifications(None, bytearray(payload))
    async def write_gatt_char(self, characteristic, data, *, response):
        assert characteristic.uuid == ACK and response is True
        if self.write_hook: await self.write_hook(data)
        self.writes.append(bytes(data))
        self.ack_event.set()


class ReceiverTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)
        self.clients = []
        self.events = []
    def tearDown(self): self.tmp.cleanup()

    async def run_receiver(self, script, configure=lambda c: None, **kwargs):
        def factory(*args, **kw):
            c = MockClient(*args, **kw); c.script=script; configure(c)
            self.clients.append(c)
            return c
        options=dict(radio_authorized=True, os_pairing_authorized=True,
                     confirm_local_approval=yes, client_factory=factory, create=True, emit=self.events.append)
        options.update(kwargs)
        return await asyncio.wait_for(receive(self.path,B,**options),3)

    async def full_then_ack(self, client):
        for f in fragments(R.encode()): client.send(f)
        await client.ack_event.wait()
        client.drop()

    async def test_durable_before_exact_ack(self):
        async def check(data):
            self.assertEqual(decode_ack(data),(R.session,R.seq))
            db=sqlite3.connect(self.path/'records.sqlite3')
            self.assertEqual(db.execute('SELECT raw FROM records').fetchone()[0],R.encode())
            db.close()
        await self.run_receiver(self.full_then_ack,lambda c:setattr(c,'write_hook',check))
        self.assertEqual(len(self.clients[-1].writes),1)
        self.assertTrue(self.clients[-1].pair)
        self.assertTrue(all(e.get('UI_allowed',False) is False for e in self.events))

    async def test_defaults_never_construct_client(self):
        def factory(*args,**kwargs): self.fail('radio factory called')
        with self.assertRaises(ReceiverError):
            await receive(self.path,B,client_factory=factory)
        self.assertFalse((self.path/'records.sqlite3').exists())

    async def test_ack_loss_then_partial_replay_cannot_ack(self):
        async def lost(data): raise OSError('mock ACK lost/disconnected')
        with self.assertRaises(OSError):
            await self.run_receiver(self.full_then_ack,lambda c:setattr(c,'write_hook',lost))
        old=self.clients[-1]
        async def partial(c):
            c.send(fragments(R.encode())[2])
            c.send(fragments(R.encode())[0])
            await asyncio.sleep(.03)
            c.drop()
        await self.run_receiver(partial)
        self.assertEqual(self.clients[-1].writes,[])
        async def with_old_callbacks(c):
            # Late fragment/connection callbacks from old client cannot operate
            # on this client, even when session and seq are identical.
            for f in fragments(R.encode()): old.send(f)
            old.drop()
            await asyncio.sleep(.02)
            self.assertEqual(c.writes,[])
            await self.full_then_ack(c)
        await self.run_receiver(with_old_callbacks)
        self.assertTrue(self.events[-1]['duplicate'])
        with Journal(self.path,B) as j: self.assertEqual(len(list(j.replay(R.session))),1)

    async def test_corruption_loss_order_then_complete_retry(self):
        async def script(c):
            f=fragments(R.encode())
            for v in [f[0],f[2],f[1],b'bad',f[0],f[1],f[1],f[2]]: c.send(v)
            corrupt=bytearray(R.encode());corrupt[-1]^=1
            for i in range(3):c.send(f[i][:4]+corrupt[i*16:(i+1)*16])
            await asyncio.sleep(.03)
            self.assertEqual(c.writes,[])
            await self.full_then_ack(c)
        await self.run_receiver(script)
        self.assertEqual(len(self.clients[-1].writes),1)

    async def test_session_seq16_collision_and_out_of_order_records(self):
        records=[R,dataclasses.replace(R,seq=65536),dataclasses.replace(R,seq=2),
                 dataclasses.replace(R,session=1,seq=0)]
        async def script(c):
            for r in records:
                c.ack_event.clear()
                for f in fragments(r.encode()):c.send(f)
                await c.ack_event.wait()
            c.drop()
        await self.run_receiver(script)
        self.assertEqual([decode_ack(x) for x in self.clients[-1].writes],[(r.session,r.seq) for r in records])

    async def test_wrong_device_stops_no_ack(self):
        async def script(c):
            for f in fragments(dataclasses.replace(R,device=43).encode()):c.send(f)
        with self.assertRaises(ReceiverError):await self.run_receiver(script)
        self.assertEqual(self.clients[-1].writes,[])

    async def test_overflow_stops_without_ack(self):
        async def script(c):
            for _ in range(30):c.send(fragments(R.encode())[0])
        with self.assertRaises(ReceiverError):await self.run_receiver(script,queue_size=3)
        self.assertEqual(self.clients[-1].writes,[])

    async def test_commit_failure_no_ack(self):
        class FailedJournal(Journal):
            def accept(self,raw): raise sqlite3.OperationalError('mock commit/fsync error')
        with self.assertRaises(sqlite3.OperationalError):
            await self.run_receiver(self.full_then_ack,journal_factory=FailedJournal)
        self.assertEqual(self.clients[-1].writes,[])

    async def test_disconnect_during_commit_keeps_data_without_ack(self):
        started, release=threading.Event(),threading.Event()
        class SlowJournal(Journal):
            def accept(self,raw):
                started.set()
                if not release.wait(2):raise RuntimeError('test timeout')
                return super().accept(raw)
        async def script(c):
            for f in fragments(R.encode()):c.send(f)
            await asyncio.to_thread(started.wait,1)
            c.drop()
            release.set()
        await self.run_receiver(script,journal_factory=SlowJournal)
        self.assertEqual(self.clients[-1].writes,[])
        with Journal(self.path,B) as j:self.assertEqual(list(j.replay(R.session)),[R])

    async def test_cancel_during_commit_waits_before_close(self):
        started,release=threading.Event(),threading.Event()
        class SlowJournal(Journal):
            def accept(self,raw):
                started.set()
                if not release.wait(2):raise RuntimeError('test timeout')
                return super().accept(raw)
        task=asyncio.create_task(self.run_receiver(self.full_then_ack,journal_factory=SlowJournal))
        await asyncio.to_thread(started.wait,1)
        task.cancel(); release.set()
        with self.assertRaises(asyncio.CancelledError):await task
        with Journal(self.path,B) as j:self.assertEqual(list(j.replay(R.session)),[R])
        self.assertEqual(self.clients[-1].writes,[])

    async def test_info_and_gatt_are_not_authorization(self):
        for info in [b'PEN SYNTHETIC',b'PEN/1 RECORD48 FRAG3 ACK20 SENSOR',b'']:
            with self.subTest(info=info), self.assertRaises(ReceiverError):
                await self.run_receiver(self.full_then_ack,lambda c:setattr(c,'info',info))
        with self.assertRaises(ReceiverError):
            await self.run_receiver(self.full_then_ack,confirm_local_approval=no)
        def bad(c):c.services[0].characteristics[1].properties=['write-without-response']
        with self.assertRaises(ReceiverError):await self.run_receiver(self.full_then_ack,bad)
        self.assertTrue(all(not c.writes for c in self.clients))

    async def test_initial_auth_denial_requires_fresh_info_after_local_confirmation(self):
        class AuthError(Exception):code=5
        await self.run_receiver(self.full_then_ack,lambda c:setattr(c,'probe_error',AuthError()))
        self.assertEqual(self.clients[-1].reads,2)
        self.assertTrue(any(e['type']=='LOCAL_APPROVAL_REQUIRED' for e in self.events))
