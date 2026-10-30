"""Private, single-owner SQLite rollback journal; failures latch until reopen.

EXTRA commit is the software durability boundary, conditional on OS/filesystem/
storage honoring sync. No deletion, repair, truncate or reset API is provided.
"""
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import threading

from .protocol import EXPECTED_INFO, Record
from .identity import source_namespace


@dataclass(frozen=True)
class Binding:
    peer_scope: str
    target: str
    device: int

    def validate(self):
        if not re.fullmatch(r"[A-Za-z0-9._-]{1,64}", self.peer_scope):
            raise ValueError("peer_scope must be a local 1..64 character label")
        if not isinstance(self.target, str) or not 1 <= len(self.target) <= 128 or any(ord(c) < 32 for c in self.target):
            raise ValueError("explicit target required")
        if type(self.device) is not int or not 0 <= self.device < 2**32:
            raise ValueError("expected device must be uint32")


class JournalError(RuntimeError):
    pass


def _check_path(path, directory=False):
    st = path.lstat()
    if stat.S_ISLNK(st.st_mode) or not (stat.S_ISDIR(st.st_mode) if directory else stat.S_ISREG(st.st_mode)):
        raise JournalError("journal paths must be real directories/regular files, not links")
    if not directory and st.st_nlink != 1:
        raise JournalError("hard-linked journal file rejected")
    if os.name == "posix":
        if st.st_uid != os.getuid() or stat.S_IMODE(st.st_mode) & 0o077:
            raise JournalError("journal directory/files must be owned by this user and private (0700/0600)")
        need = 0o700 if directory else 0o600
        if stat.S_IMODE(st.st_mode) & need != need:
            raise JournalError("journal path lacks owner read/write/search permissions")


def private_directory(path, windows_private_dir_confirmed=False):
    """No mkdir/chmod fallback; callers provision a private local directory."""
    path = Path(os.path.abspath(os.fspath(path)))
    for component in (path, *path.parents):
        if component.is_symlink():
            raise JournalError("symlink in journal path rejected")
    _check_path(path, directory=True)
    if os.name == "nt" and not windows_private_dir_confirmed:
        raise JournalError("Windows DACL is not attested: explicitly confirm a private local directory")
    if os.name not in ("posix", "nt"):
        raise JournalError("unsupported filesystem platform")
    return path


def _sync_directory(path):
    if os.name == "posix":
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


META_SQL = "CREATE TABLE meta (id INTEGER PRIMARY KEY CHECK(id=1), value TEXT NOT NULL)"
RECORDS_SQL = """CREATE TABLE records (
            arrival INTEGER PRIMARY KEY, device INTEGER NOT NULL,
            session TEXT NOT NULL, seq INTEGER NOT NULL, raw BLOB NOT NULL CHECK(length(raw)=48),
            UNIQUE(device,session,seq))"""
EXPECTED_OBJECTS = [
    ('index', 'sqlite_autoindex_records_1', 'records', None),
    ('table', 'meta', 'meta', META_SQL),
    ('table', 'records', 'records', RECORDS_SQL),
]
EXPECTED_COLUMNS = {
    'meta': [(0, 'id', 'INTEGER', 0, None, 1, 0), (1, 'value', 'TEXT', 1, None, 0, 0)],
    'records': [(0, 'arrival', 'INTEGER', 0, None, 1, 0),
                (1, 'device', 'INTEGER', 1, None, 0, 0),
                (2, 'session', 'TEXT', 1, None, 0, 0),
                (3, 'seq', 'INTEGER', 1, None, 0, 0),
                (4, 'raw', 'BLOB', 1, None, 0, 0)],
}


class Journal:
    def __init__(self, directory, binding=None, *, create=False, windows_private_dir_confirmed=False):
        self.db = None
        self.lock_fd = None
        self.faulted = False
        self.mutex = threading.Lock()
        self.requested_binding = binding
        self.directory = private_directory(directory, windows_private_dir_confirmed)
        if binding is not None:
            binding.validate()
        if create and binding is None:
            raise JournalError("creation requires explicit peer/device binding")
        _sync_directory(self.directory.parent)
        self.path = self.directory / "records.sqlite3"
        try:
            self._lock()
            for name in ("records.sqlite3", "records.sqlite3-journal", "records.sqlite3-wal", "records.sqlite3-shm"):
                p = self.directory / name
                if p.exists() or p.is_symlink():
                    _check_path(p)
            new = not self.path.exists()
            if new:
                if not create:
                    raise JournalError("journal missing; never silently create during replay/recovery")
                fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
                try:
                    os.fsync(fd)
                finally:
                    os.close(fd)
                _sync_directory(self.directory)
            elif self.path.stat().st_size == 0:
                raise JournalError("existing empty journal rejected; preserve for investigation")
            self.db = sqlite3.connect(self.path, timeout=0, isolation_level=None, check_same_thread=False)
            self.db.execute("PRAGMA trusted_schema=OFF")
            if not new:
                self._validate(binding)  # refuse foreign/corrupt DB before persistent mode changes
            self.db.execute("PRAGMA synchronous=EXTRA")
            self.db.execute("PRAGMA fullfsync=ON")
            mode_sql = "PRAGMA journal_mode=DELETE" if new else "PRAGMA journal_mode"
            if self.db.execute(mode_sql).fetchone()[0].lower() != "delete":
                raise JournalError("required rollback journal mode unavailable")
            if self.db.execute("PRAGMA synchronous").fetchone()[0] != 3:
                raise JournalError("EXTRA synchronous mode unavailable")
            if new:
                self._initialize(binding)
                _sync_directory(self.directory)
            self._validate(binding)
        except BaseException:
            self.close()
            raise

    def _lock(self):
        path = self.directory / "receiver.lock"
        try:
            fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
            self.lock_fd = fd
            os.write(fd, b"0")
            os.fsync(fd)
            _sync_directory(self.directory)
        except FileExistsError:
            _check_path(path)
            fd = os.open(path, os.O_RDWR | getattr(os, "O_NOFOLLOW", 0))
        self.lock_fd = fd
        if os.name == "posix":
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        else:
            import msvcrt
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)

    def _initialize(self, binding):
        self.db.execute("BEGIN IMMEDIATE")
        self.db.execute(META_SQL)
        self.db.execute(RECORDS_SQL)
        metadata = {"schema": 2, "binding": asdict(binding),
                    "source_namespace": source_namespace(asdict(binding)), "info": EXPECTED_INFO.decode("ascii"),
                    "source": "dev_usb_no_sensor", "host_security_attested": False}
        self.db.execute("INSERT INTO main.meta VALUES(1,?)", (json.dumps(metadata, sort_keys=True),))
        self.db.execute("PRAGMA user_version=2")
        self.db.execute("COMMIT")

    def _validate_schema(self):
        # Compare all objects, not just table names. Exact SQL is intentionally
        # fail-closed: no equivalent-schema guessing or implicit migration.
        if self.db.execute("PRAGMA main.user_version").fetchone() != (2,):
            raise JournalError("unsupported journal schema; v1 requires separate reviewed migration")
        objects = self.db.execute("SELECT type,name,tbl_name,sql FROM main.sqlite_master ORDER BY type,name").fetchall()
        if objects != EXPECTED_OBJECTS or self.db.execute("SELECT name FROM temp.sqlite_master").fetchall():
            raise JournalError("unexpected schema object/SQL (including triggers/views/indexes)")
        for name, columns in EXPECTED_COLUMNS.items():
            if self.db.execute(f"PRAGMA main.table_xinfo({name})").fetchall() != columns:
                raise JournalError("journal column/PK/NOT NULL/generated-column mismatch")
            if self.db.execute(f"PRAGMA main.foreign_key_list({name})").fetchall():
                raise JournalError("unexpected foreign key")
        if self.db.execute("PRAGMA main.index_list(meta)").fetchall():
            raise JournalError("unexpected metadata index")
        if self.db.execute("PRAGMA main.index_list(records)").fetchall() != [(0, 'sqlite_autoindex_records_1', 1, 'u', 0)]:
            raise JournalError("missing/nonunique/partial/extra record identity index")
        if self.db.execute("PRAGMA main.index_xinfo(sqlite_autoindex_records_1)").fetchall() != [
                (0, 1, 'device', 0, 'BINARY', 1), (1, 2, 'session', 0, 'BINARY', 1),
                (2, 3, 'seq', 0, 'BINARY', 1), (3, -1, None, 0, 'BINARY', 0)]:
            raise JournalError("record uniqueness key/order/collation mismatch")

    def _validate(self, binding):
        self._validate_schema()
        if self.db.execute("PRAGMA main.integrity_check").fetchall() != [("ok",)]:
            raise JournalError("journal integrity/constraint/index check failed; no auto-repair")
        metadata_rows = self.db.execute("SELECT id,value FROM main.meta").fetchall()
        if len(metadata_rows) != 1 or metadata_rows[0][0] != 1:
            raise JournalError("journal metadata missing/ambiguous")
        self.metadata = json.loads(metadata_rows[0][1])
        self.binding = Binding(**self.metadata["binding"])
        self.binding.validate()
        expected = {"schema": 2, "binding": asdict(self.binding),
                    "source_namespace": source_namespace(asdict(self.binding)), "info": EXPECTED_INFO.decode("ascii"),
                    "source": "dev_usb_no_sensor", "host_security_attested": False}
        if self.metadata != expected or binding is not None and binding != self.binding:
            raise JournalError("peer/target/device/source binding mismatch; no automatic migration")
        if self.db.execute("SELECT 1 FROM main.records GROUP BY device,session,seq HAVING count(*)!=1 LIMIT 1").fetchone():
            raise JournalError("duplicate record identities")
        for device, session, seq, raw in self.db.execute("SELECT device,session,seq,raw FROM main.records"):
            if not isinstance(raw, bytes):
                raise JournalError("record payload is not SQLite BLOB")
            record = Record.decode(bytes(raw))
            if (device, session, seq) != (self.binding.device, str(record.session), record.seq) or record.device != device:
                raise JournalError("journal row identity mismatch")

    def _exact_row(self, key, raw, *, allow_missing=False):
        rows = self.db.execute("SELECT device,session,seq,raw,typeof(raw) FROM main.records "
                               "WHERE device=? AND session=? AND seq=? LIMIT 2", key).fetchall()
        if not rows and allow_missing:
            return False
        if len(rows) != 1 or rows[0][:3] != key or rows[0][4] != 'blob' or rows[0][3] != raw:
            raise JournalError("missing/duplicate/conflicting exact journal row; ACK forbidden")
        return True

    def accept(self, raw):
        """Return new/duplicate only after COMMIT. Exact record, never frontier ACK."""
        with self.mutex:
            if self.faulted or self.db is None or self.requested_binding is None:
                raise JournalError("journal closed/faulted/not bound for reception")
            try:
                raw = bytes(raw)
                record = Record.decode(raw)
                if record.device != self.binding.device:
                    raise JournalError("unexpected record device identity")
                key = (record.device, str(record.session), record.seq)
                self.db.execute("BEGIN IMMEDIATE")
                # Schema check is inside the write transaction, preventing a
                # competing writer adding a trigger between check and INSERT.
                self._validate_schema()
                metadata_rows = self.db.execute("SELECT id,value FROM main.meta").fetchall()
                if (len(metadata_rows) != 1 or metadata_rows[0][0] != 1
                        or json.loads(metadata_rows[0][1]) != self.metadata):
                    raise JournalError("source metadata changed during reception")
                old = self._exact_row(key, raw, allow_missing=True)
                if not old:
                    before = self.db.total_changes
                    cursor = self.db.execute("INSERT INTO main.records(device,session,seq,raw) VALUES(?,?,?,?)", (*key, raw))
                    if (cursor.rowcount != 1 or self.db.execute("SELECT changes()").fetchone() != (1,)
                            or self.db.total_changes - before != 1):
                        raise JournalError("INSERT did not affect exactly one row")
                self._exact_row(key, raw)  # catch ignored/rewritten INSERT before commit
                self.db.execute("COMMIT")
                if self.db.in_transaction:
                    raise JournalError("COMMIT did not finish transaction")
                self._exact_row(key, raw)  # fresh post-COMMIT read; failure is no ACK
                return not old
            except BaseException:
                self.faulted = True
                try:
                    self.db.rollback()
                except sqlite3.Error:
                    pass
                raise

    def replay(self, session):
        if type(session) is not int or not 1 <= session < 2**64:
            raise ValueError("nonzero uint64 session required")
        with self.mutex:
            if self.faulted or self.db is None:
                raise JournalError("journal unavailable")
            rows = self.db.execute("SELECT raw FROM main.records WHERE device=? AND session=? ORDER BY seq",
                                   (self.binding.device, str(session)))
            for (raw,) in rows:
                yield Record.decode(bytes(raw))

    def close(self):
        if self.db is not None:
            self.db.close()
            self.db = None
        if self.lock_fd is not None:
            os.close(self.lock_fd)
            self.lock_fd = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
