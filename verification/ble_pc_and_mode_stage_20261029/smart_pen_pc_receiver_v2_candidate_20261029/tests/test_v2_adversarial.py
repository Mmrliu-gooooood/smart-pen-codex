import asyncio
import dataclasses
import json
from pathlib import Path
import shutil
import sqlite3
import tempfile
import threading
import unittest
from unittest.mock import patch

from pen_receiver.events import record_events
from pen_receiver.identity import EventIdentityGuard
from pen_receiver.journal import Binding, Journal, JournalError, META_SQL, RECORDS_SQL
from pen_receiver.protocol import Record, fragments, decode_ack
import test_journal as journal_tests
from test_journal import B, R
import test_receiver as receiver_tests
from test_receiver import R as VALID_R


class SchemaTests(unittest.TestCase):
    setUp=journal_tests.JournalTests.setUp
    tearDown=journal_tests.JournalTests.tearDown

    def test_extra_schema_objects_and_triggers_rejected(self):
        alterations=[
            'CREATE TRIGGER drop_record BEFORE INSERT ON records BEGIN SELECT RAISE(IGNORE); END',
            'CREATE TRIGGER delete_record AFTER INSERT ON records BEGIN DELETE FROM records; END',
            'CREATE TRIGGER rewrite_record AFTER INSERT ON records BEGIN UPDATE records SET seq=seq+1; END',
            'CREATE VIEW view_records AS SELECT * FROM records',
            'CREATE TABLE extra(x)',
            'CREATE INDEX alternate_idx ON records(seq)',
        ]
        for i,sql in enumerate(alterations):
            path=self.path/str(i);path.mkdir(mode=0o700)
            with Journal(path,B,create=True):pass
            db=sqlite3.connect(path/'records.sqlite3');db.execute(sql);db.close()
            before=(path/'records.sqlite3').read_bytes()
            with self.subTest(sql=sql), self.assertRaises(JournalError):Journal(path,B)
            self.assertEqual((path/'records.sqlite3').read_bytes(),before)

    def test_structural_and_unique_contract_not_only_table_names(self):
        alternatives=[
            RECORDS_SQL.replace(',\n            UNIQUE(device,session,seq)',''),
            RECORDS_SQL.replace('UNIQUE(device,session,seq)','UNIQUE(device,seq)'),
            RECORDS_SQL.replace('seq INTEGER NOT NULL','seq TEXT'),
            RECORDS_SQL.replace('arrival INTEGER PRIMARY KEY','arrival INTEGER'),
            RECORDS_SQL.replace('CHECK(length(raw)=48)','CHECK(length(raw)>=1)'),
            RECORDS_SQL.replace('raw BLOB','raw TEXT'),
        ]
        for i,sql in enumerate(alternatives):
            path=self.path/str(i);path.mkdir(mode=0o700)
            with Journal(path,B,create=True):pass
            db=sqlite3.connect(path/'records.sqlite3');db.execute('DROP TABLE records');db.execute(sql);db.close()
            with self.subTest(sql=sql), self.assertRaises(JournalError):Journal(path,B)

    def test_runtime_schema_changes_and_temp_shadow_rejected(self):
        for temp in [False,True]:
            path=self.path/str(temp);path.mkdir(mode=0o700)
            with Journal(path,B,create=True) as j:
                if temp:j.db.execute('CREATE TEMP TABLE records(x)')
                else:j.db.execute('CREATE TRIGGER drop_record BEFORE INSERT ON records BEGIN SELECT RAISE(IGNORE); END')
                with self.assertRaises(JournalError):j.accept(R.encode())
                self.assertTrue(j.faulted)
                self.assertEqual(j.db.execute('SELECT count(*) FROM main.records').fetchone(),(0,))

    def test_same_key_multiple_rows_fail_even_exact_read_helper(self):
        with Journal(self.path,B,create=True) as j:
            j.db.execute('DROP TABLE records')
            j.db.execute(RECORDS_SQL.replace(',\n            UNIQUE(device,session,seq)',''))
            for _ in range(2):j.db.execute('INSERT INTO records(device,session,seq,raw) VALUES(?,?,?,?)',(R.device,str(R.session),R.seq,R.encode()))
            with self.assertRaises(JournalError):j._exact_row((R.device,str(R.session),R.seq),R.encode())
        with self.assertRaises(JournalError):Journal(self.path,B)

    def test_v1_not_migrated_and_namespace_tamper_rejected(self):
        with Journal(self.path,B,create=True):pass
        db=sqlite3.connect(self.path/'records.sqlite3');db.execute('PRAGMA user_version=1');db.close()
        before=(self.path/'records.sqlite3').read_bytes()
        with self.assertRaises(JournalError):Journal(self.path,B,create=True)
        self.assertEqual((self.path/'records.sqlite3').read_bytes(),before)
        db=sqlite3.connect(self.path/'records.sqlite3');db.execute('PRAGMA user_version=2')
        meta=json.loads(db.execute('SELECT value FROM meta').fetchone()[0]);meta['source_namespace']='pen-source-v2:'+'0'*64
        db.execute('UPDATE meta SET value=?',(json.dumps(meta),));db.commit();db.close()
        with self.assertRaises(JournalError):Journal(self.path,B)

    def test_affected_row_and_noop_commit_guard(self):
        class Proxy:
            def __init__(self,db,kind):self.db,self.kind=db,kind
            def __getattr__(self,name):return getattr(self.db,name)
            def execute(self,sql,*args):
                if self.kind=='insert_ignore' and sql.startswith('INSERT INTO main.records'):
                    return self.db.execute('UPDATE main.records SET seq=seq WHERE 0')
                if self.kind=='noop_commit' and sql=='COMMIT':return self.db.execute('SELECT 1')
                return self.db.execute(sql,*args)
        for kind in ['insert_ignore','noop_commit']:
            path=self.path/kind;path.mkdir(mode=0o700)
            with Journal(path,B,create=True) as j:
                j.db=Proxy(j.db,kind)
                with self.assertRaises(JournalError):j.accept(R.encode())
                self.assertTrue(j.faulted)
            with Journal(path,B) as j:self.assertEqual(list(j.replay(R.session)),[])


class NamespaceTests(unittest.TestCase):
    setUp=journal_tests.JournalTests.setUp
    tearDown=journal_tests.JournalTests.tearDown

    def make(self,label,target,record=VALID_R):
        path=self.path/label;path.mkdir(mode=0o700)
        binding=Binding('same-local-label',target,42)
        with Journal(path,binding,create=True) as j:
            j.accept(record.encode())
            events=list(record_events(j.replay(record.session),j.metadata))
            namespace=j.metadata['source_namespace']
        return path,binding,events,namespace

    def test_different_targets_export_distinct_stable_namespaces(self):
        pa,ba,a,na=self.make('a','target-A')
        pb,bb,b,nb=self.make('b','target-B')
        self.assertNotEqual(a,b);self.assertNotEqual(na,nb)
        self.assertTrue(all(e['source_namespace']==na for e in a))
        self.assertTrue(all('record_sha256' in e for e in a))
        self.assertNotIn('target-A',json.dumps(a))
        with Journal(pa,ba) as j:self.assertEqual(j.metadata['source_namespace'],na)
        with self.assertRaises(JournalError):Journal(pa,bb)
        guard=EventIdentityGuard()
        for events in [a,b]:
            self.assertTrue(guard.accept(next(e for e in events if e['type']=='DIAGNOSTIC')))

    def test_clone_same_source_dedup_and_conflicting_merge_rejected(self):
        path,binding,a,namespace=self.make('a','target-A')
        clone=self.path/'clone';shutil.copytree(path,clone)
        with Journal(clone,binding) as j:
            self.assertEqual(j.metadata['source_namespace'],namespace)
            duplicate=list(record_events(j.replay(VALID_R.session),j.metadata))
        guard=EventIdentityGuard()
        first=next(e for e in a if e['type']=='DIAGNOSTIC')
        self.assertTrue(guard.accept(first))
        self.assertFalse(guard.accept(next(e for e in duplicate if e['type']=='DIAGNOSTIC')))
        changed=dataclasses.replace(VALID_R,x_um=VALID_R.x_um+1)
        db=sqlite3.connect(clone/'records.sqlite3');db.execute('UPDATE records SET raw=?',(changed.encode(),));db.commit();db.close()
        with Journal(clone,binding) as j:conflict=list(record_events(j.replay(changed.session),j.metadata))
        with self.assertRaises(ValueError):guard.accept(next(e for e in conflict if e['type']=='DIAGNOSTIC'))
        without=dict(first);del without['source_namespace']
        with self.assertRaises(ValueError):guard.accept(without)
        with self.assertRaises(ValueError):record_events([],{'binding':dataclasses.asdict(binding)}).__next__()


class ReceiverV2Tests(unittest.IsolatedAsyncioTestCase):
    setUp=receiver_tests.ReceiverTests.setUp
    tearDown=receiver_tests.ReceiverTests.tearDown
    run_receiver=receiver_tests.ReceiverTests.run_receiver
    full_then_ack=receiver_tests.ReceiverTests.full_then_ack

    async def test_trigger_database_rejected_before_radio_factory(self):
        with Journal(self.path,B,create=True):pass
        db=sqlite3.connect(self.path/'records.sqlite3')
        db.execute('CREATE TRIGGER drop_record BEFORE INSERT ON records BEGIN SELECT RAISE(IGNORE); END');db.close()
        with self.assertRaises(JournalError):await self.run_receiver(self.full_then_ack)
        self.assertEqual(self.clients,[])
        db=sqlite3.connect(self.path/'records.sqlite3')
        self.assertEqual(db.execute('SELECT count(*) FROM records').fetchone(),(0,));db.close()

    async def test_post_commit_readback_fault_never_ack(self):
        class Proxy:
            def __init__(self,db,empty):self.db,self.empty,self.committed=db,empty,False
            def __getattr__(self,name):return getattr(self.db,name)
            def execute(self,sql,*args):
                if self.committed and sql.startswith('SELECT device,session,seq,raw,typeof(raw)'):
                    if self.empty:return self.db.execute('SELECT 1 WHERE 0')
                    raise sqlite3.OperationalError('injected post-COMMIT readback IO error')
                result=self.db.execute(sql,*args)
                if sql=='COMMIT':self.committed=True
                return result
        for empty in [False,True]:
            class FaultJournal(Journal):
                def __init__(self,*args,**kwargs):
                    super().__init__(*args,**kwargs);self.db=Proxy(self.db,empty)
            with self.assertRaises((JournalError,sqlite3.OperationalError)):
                await self.run_receiver(self.full_then_ack,journal_factory=FaultJournal)
            self.assertEqual(self.clients[-1].writes,[])
            with Journal(self.path,B) as j:self.assertEqual(len(list(j.replay(VALID_R.session))),1)
        await self.run_receiver(self.full_then_ack)
        self.assertTrue(self.events[-1]['duplicate'])
        self.assertIn('source_namespace',self.events[-1]);self.assertIn('record_sha256',self.events[-1])

    async def test_callback_observation_time_not_dequeue_time(self):
        started,release=threading.Event(),threading.Event()
        clock=[0.0]
        class SlowFirst(Journal):
            def accept(self,raw):
                if Record.decode(raw).seq==0:
                    started.set()
                    if not release.wait(2):raise RuntimeError('test timeout')
                return super().accept(raw)
        later=dataclasses.replace(VALID_R,seq=1)
        async def script(c):
            for f in fragments(VALID_R.encode()):c.send(f)
            await asyncio.to_thread(started.wait,1)
            clock[0]=10;c.send(fragments(later.encode())[0])
            clock[0]=13
            for f in fragments(later.encode())[1:]:c.send(f)
            release.set()
            await c.ack_event.wait();c.ack_event.clear()
            await asyncio.sleep(.03)
            self.assertEqual([decode_ack(w)[1] for w in c.writes],[0])
            clock[0]=14
            for f in fragments(later.encode()):c.send(f)
            await c.ack_event.wait();c.drop()
        with patch('pen_receiver.receiver.monotonic',side_effect=lambda:clock[0]):
            await self.run_receiver(script,journal_factory=SlowFirst)
        self.assertEqual([decode_ack(w)[1] for w in self.clients[-1].writes],[0,1])
        self.assertTrue(any(e['type']=='REJECTED_FRAGMENT' for e in self.events))

    async def test_nonfinite_and_backward_callback_clock_latches_connection(self):
        for times in [(10.0,11.0,10.5),(10.0,float('nan')),(10.0,float('inf'))]:
            values=iter(times)
            async def script(c):
                for f in fragments(VALID_R.encode())[:len(times)]:c.send(f)
            with patch('pen_receiver.receiver.monotonic',side_effect=lambda:next(values)):
                from pen_receiver.receiver import ReceiverError
                with self.assertRaises(ReceiverError):await self.run_receiver(script)
            self.assertEqual(self.clients[-1].writes,[])

    async def test_new_fragment_zero_does_not_reset_callback_clock_guard(self):
        clock=[10.0]
        async def script(c):
            for f in fragments(VALID_R.encode()):c.send(f)
            await c.ack_event.wait()
            clock[0]=9.0
            c.send(fragments(dataclasses.replace(VALID_R,seq=1).encode())[0])
        with patch('pen_receiver.receiver.monotonic',side_effect=lambda:clock[0]):
            from pen_receiver.receiver import ReceiverError
            with self.assertRaises(ReceiverError):await self.run_receiver(script)
        self.assertEqual([decode_ack(x)[1] for x in self.clients[-1].writes],[0])


class ReassemblyClockTests(unittest.TestCase):
    def test_middle_backward_and_reset_do_not_hide_regression(self):
        from pen_receiver.protocol import Reassembler
        f=fragments(VALID_R.encode());a=Reassembler()
        a.accept(f[0],10);a.accept(f[1],11)
        with self.assertRaises(ValueError):a.accept(f[2],10.5)
        with self.assertRaises(ValueError):a.accept(f[0],10.75)
        a.reset()
        with self.assertRaises(ValueError):a.accept(f[0],10.9)
        a.accept(f[0],12);a.accept(f[1],12);self.assertEqual(a.accept(f[2],12),VALID_R.encode())
