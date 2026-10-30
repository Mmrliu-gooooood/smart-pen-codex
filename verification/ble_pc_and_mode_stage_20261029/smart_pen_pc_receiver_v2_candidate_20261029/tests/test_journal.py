import dataclasses
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pen_receiver.journal import Binding, Journal, JournalError
from pen_receiver.protocol import Record

B = Binding('bench-one', 'explicit-test-target', 42)
R = Record(0, 42, 2**64-1, 0, 10, 0, 0, 0, 0)


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)
    def tearDown(self): self.tmp.cleanup()

    def test_commit_duplicate_reopen_gaps_and_sessions(self):
        with Journal(self.path, B, create=True) as j:
            self.assertTrue(j.accept(R.encode()))
            self.assertFalse(j.accept(R.encode()))
            j.accept(dataclasses.replace(R, seq=2).encode())
            j.accept(dataclasses.replace(R, session=1).encode())
        with Journal(self.path, B) as j:
            self.assertFalse(j.accept(R.encode()))
            self.assertEqual([r.seq for r in j.replay(R.session)], [0,2])
            self.assertEqual(len(list(j.replay(1))), 1)
        if os.name == 'posix': self.assertEqual((self.path/'records.sqlite3').stat().st_mode & 0o777, 0o600)

    def test_conflict_latches_and_preserves(self):
        with Journal(self.path, B, create=True) as j:
            j.accept(R.encode())
            with self.assertRaises(JournalError): j.accept(dataclasses.replace(R, timestamp_us=11).encode())
            with self.assertRaises(JournalError): j.accept(R.encode())
        with Journal(self.path, B) as j:
            self.assertEqual(list(j.replay(R.session)), [R])

    def test_binding_identity_and_single_writer(self):
        with Journal(self.path, B, create=True) as j:
            with self.assertRaises(OSError): Journal(self.path, B)
            with self.assertRaises(JournalError): j.accept(dataclasses.replace(R, device=43).encode())
        for binding in [dataclasses.replace(B,target='different'), dataclasses.replace(B,peer_scope='different'),
                        dataclasses.replace(B,device=43)]:
            with self.assertRaises(JournalError): Journal(self.path,binding)

    def test_empty_corrupt_foreign_missing_never_recreated(self):
        path = self.path/'records.sqlite3'
        with self.assertRaises(JournalError): Journal(self.path,B)
        for content in [b'', b'corrupt']:
            path.write_bytes(content); path.chmod(0o600)
            with self.assertRaises((JournalError, sqlite3.Error)): Journal(self.path,B,create=True)
            self.assertEqual(path.read_bytes(), content)
        path.unlink()
        db=sqlite3.connect(path); db.execute('CREATE TABLE foreign_table(x)'); db.close(); path.chmod(0o600)
        with self.assertRaises(JournalError): Journal(self.path,B,create=True)

    @unittest.skipUnless(os.name == 'posix', 'POSIX permission semantics')
    def test_permissions_links_and_unwritable(self):
        self.path.chmod(0o755)
        with self.assertRaises(JournalError): Journal(self.path,B,create=True)
        self.path.chmod(0o500)
        with self.assertRaises(JournalError): Journal(self.path,B,create=True)
        self.path.chmod(0o700)
        target=self.path/'target'; target.write_bytes(b'x'); target.chmod(0o600)
        (self.path/'records.sqlite3').symlink_to(target)
        with self.assertRaises(JournalError): Journal(self.path,B,create=True)
        (self.path/'records.sqlite3').unlink()
        os.link(target,self.path/'records.sqlite3')
        with self.assertRaises(JournalError): Journal(self.path,B,create=True)

    def test_real_sqlite_full_no_success_then_recover(self):
        with Journal(self.path,B,create=True) as j:
            j.accept(R.encode())
            pages=j.db.execute('PRAGMA page_count').fetchone()[0]
            j.db.execute(f'PRAGMA max_page_count={pages}')
            failed=False
            for seq in range(1,1000):
                try: j.accept(dataclasses.replace(R,seq=seq).encode())
                except sqlite3.OperationalError as exc:
                    self.assertIn('full',str(exc)); failed=True; break
            self.assertTrue(failed)
            with self.assertRaises(JournalError): j.accept(R.encode())
        with Journal(self.path,B) as j:
            self.assertEqual(next(j.replay(R.session)),R)
            self.assertNotIn(seq, [r.seq for r in j.replay(R.session)])

    def test_process_crash_before_after_commit(self):
        with Journal(self.path,B,create=True) as j: j.accept(R.encode())
        code='''import os,sys
from pen_receiver.journal import Journal,Binding
from pen_receiver.protocol import Record
j=Journal(sys.argv[1],Binding('bench-one','explicit-test-target',42))
r=Record(0,42,1,9,10,0,0,0,0)
if sys.argv[2]=='after': j.accept(r.encode())
else:
 j.db.execute('BEGIN IMMEDIATE')
 j.db.execute('INSERT INTO records(device,session,seq,raw) VALUES(?,?,?,?)',(42,'1',9,r.encode()))
os._exit(23)
'''
        for when, expected in [('before',0),('after',1)]:
            p=subprocess.run([sys.executable,'-c',code,str(self.path),when],check=False)
            self.assertEqual(p.returncode,23)
            with Journal(self.path,B) as j: self.assertEqual(len(list(j.replay(1))),expected)

    def test_commit_exception_before_and_after_commit(self):
        class Proxy:
            def __init__(self, db, after):self.db,self.after=db,after
            def __getattr__(self,name):return getattr(self.db,name)
            def execute(self,sql,*args):
                if sql=='COMMIT':
                    if self.after:self.db.execute(sql,*args)
                    raise sqlite3.OperationalError('injected commit/fsync uncertainty')
                return self.db.execute(sql,*args)
        for after in [False,True]:
            sub=self.path/str(after);sub.mkdir(mode=0o700)
            with Journal(sub,B,create=True) as j:
                j.db=Proxy(j.db,after)
                with self.assertRaises(sqlite3.OperationalError):j.accept(R.encode())
                with self.assertRaises(JournalError):j.accept(R.encode())
            with Journal(sub,B) as j:
                self.assertEqual(len(list(j.replay(R.session))),int(after))
                self.assertEqual(j.accept(R.encode()),not after)

    def test_initialization_disk_failure_not_replaced(self):
        class FailingInit(Journal):
            def _initialize(self,binding):raise sqlite3.OperationalError('injected initialization disk full')
        with self.assertRaises(sqlite3.OperationalError):FailingInit(self.path,B,create=True)
        before=(self.path/'records.sqlite3').read_bytes()
        with self.assertRaises((sqlite3.Error,JournalError)):Journal(self.path,B,create=True)
        self.assertEqual((self.path/'records.sqlite3').read_bytes(),before)

    def test_database_permission_rejection(self):
        with Journal(self.path,B,create=True):pass
        path=self.path/'records.sqlite3'
        if os.name=='posix':
            path.chmod(0o644)
            with self.assertRaises(JournalError):Journal(self.path,B)
            path.chmod(0o600)
        side=self.path/'records.sqlite3-journal';side.symlink_to(path)
        with self.assertRaises(JournalError):Journal(self.path,B)

    def test_durability_pragma_readback(self):
        with Journal(self.path,B,create=True) as j:
            self.assertEqual(j.db.execute('PRAGMA synchronous').fetchone(),(3,))
            self.assertEqual(j.db.execute('PRAGMA journal_mode').fetchone(),('delete',))
            self.assertEqual(j.db.execute('PRAGMA fullfsync').fetchone(),(1,))

    def test_corrupt_committed_raw_fails_startup(self):
        with Journal(self.path,B,create=True) as j:j.accept(R.encode())
        db=sqlite3.connect(self.path/'records.sqlite3')
        db.execute('UPDATE records SET raw=?',(bytes(48),));db.commit();db.close()
        with self.assertRaises(ValueError):Journal(self.path,B)
