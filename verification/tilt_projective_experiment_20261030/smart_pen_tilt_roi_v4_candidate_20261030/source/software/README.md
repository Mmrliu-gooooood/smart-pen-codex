# Portable host bridge (Python 3.10+, standard library)

This is a tested **protocol / persistence / replay seam**, not a complete pen
application. It does not connect BLE, decode images, authenticate devices, or
modify the existing desktop/web UI. Feed it only complete SP v1 records from a
transport adapter (see `windows_ble.py`). The CRC detects accidental corruption, not forgery.

From repository root:

```sh
python -m unittest discover -s tests -p test_host.py
python -m software.pen_bridge --db pen.sqlite ingest < records.sp
python -m software.pen_bridge --db pen.sqlite replay --device 1 --session 42 > strokes.jsonl
```

`ingest` outputs one JSON `durable_ack` after each successful SQLite FULL commit.
`through_seq: null` means **no sequence may be cumulatively deleted**; otherwise
only the same device/session's records through that sequence are acknowledged.
Records received after a hole are retained but do not advance the cumulative
ACK. Retrying identical records is safe. Different content for an existing key
fails closed. Preserve device identity and assign a new nonzero session ID on
every boot/reset; sequence starts at zero and must not wrap within a session.
Session IDs are JSON strings to avoid JavaScript 53-bit integer truncation.
ACK frontiers and records commit atomically, so a restart does not lose ACK state.

Storage durability assumes SQLite and the operating system honor `fsync`, and
healthy nonvolatile storage. Host tests are not a physical power-cut test. Do not
copy a live database without SQLite's backup API (WAL may contain recent data).
Do not delete the DB while device records are being retired. Coordinate records
and journals can contain sensitive handwriting; the reference DB is unencrypted.

`replay` emits `start`, `point`, `end` JSONL, in sequence order for an explicitly
selected device/session. Points use page millimetres (+x right, +y up); the
frontend must deliberately convert to its canvas axes. A gap flag, missing or
repeated sequence, changed device/session/page, invalid coordinate, contact-up,
confidence below 750/1000, non-increasing clock, or interval over 100 ms ends the
old stroke. No interpolation crosses these boundaries. Thresholds are conservative
software defaults, not measured pen performance. Replay ends any active stroke
rather than pretending contact continues. Missing records arriving later require
regenerating replay; the command deliberately does not render live unordered ink.

The CLI JSONL schema is a minimal replay boundary. `upstream_web.py` now adapts
records to the actual original session/API/WebSocket schemas, including an
explicit `--live --view-id NAME` incremental journal mode with durable edits and
bounded polling. `windows_ble.py` is an explicit synthetic bench BLE receiver,
not production hardware validation. See `../docs/software/integration.md` for
commands, tested behavior, pairing/security and remaining limitations. Never
pass a JSON ACK straight to flash deletion without checking identity/session
scope and implementing a power-cut-safe reclamation policy.
