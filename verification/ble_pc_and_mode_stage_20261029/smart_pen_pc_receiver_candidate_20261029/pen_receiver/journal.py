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
        self.db.execute("CREATE TABLE meta (id INTEGER PRIMARY KEY CHECK(id=1), value TEXT NOT NULL)")
        self.db.execute("""CREATE TABLE records (
            arrival INTEGER PRIMARY KEY, device INTEGER NOT NULL,
            session TEXT NOT NULL, seq INTEGER NOT NULL, raw BLOB NOT NULL CHECK(length(raw)=48),
            UNIQUE(device,session,seq))""")
        metadata = {"schema": 1, "binding": asdict(binding), "info": EXPECTED_INFO.decode("ascii"),
                    "source": "dev_usb_no_sensor", "host_security_attested": False}
        self.db.execute("INSERT INTO meta VALUES(1,?)", (json.dumps(metadata, sort_keys=True),))
        self.db.execute("PRAGMA user_version=1")
        self.db.execute("COMMIT")

    def _validate(self, binding):
        if self.db.execute("PRAGMA quick_check").fetchone() != ("ok",):
            raise JournalError("journal integrity check failed; no auto-repair")
        if self.db.execute("PRAGMA user_version").fetchone() != (1,):
            raise JournalError("unsupported existing journal schema")
        tables = self.db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
        if tables != [("meta",), ("records",)]:
            raise JournalError("unexpected journal schema")
        metadata_rows = self.db.execute("SELECT id,value FROM meta").fetchall()
        if len(metadata_rows) != 1 or metadata_rows[0][0] != 1:
            raise JournalError("journal metadata missing/ambiguous")
        self.metadata = json.loads(metadata_rows[0][1])
        self.binding = Binding(**self.metadata["binding"])
        self.binding.validate()
        expected = {"schema": 1, "binding": asdict(self.binding), "info": EXPECTED_INFO.decode("ascii"),
                    "source": "dev_usb_no_sensor", "host_security_attested": False}
        if self.metadata != expected or binding is not None and binding != self.binding:
            raise JournalError("peer/target/device/source binding mismatch; no automatic migration")
        for device, session, seq, raw in self.db.execute("SELECT device,session,seq,raw FROM records"):
            record = Record.decode(bytes(raw))
            if (device, session, seq) != (self.binding.device, str(record.session), record.seq) or record.device != device:
                raise JournalError("journal row identity mismatch")

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
                old = self.db.execute("SELECT raw FROM records WHERE device=? AND session=? AND seq=?", key).fetchone()
                if old and bytes(old[0]) != raw:
                    raise JournalError("conflicting duplicate: preserve journal, stop reception")
                if not old:
                    self.db.execute("INSERT INTO records(device,session,seq,raw) VALUES(?,?,?,?)", (*key, raw))
                self.db.execute("COMMIT")
                return not bool(old)
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
            rows = self.db.execute("SELECT raw FROM records WHERE device=? AND session=? ORDER BY seq",
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
