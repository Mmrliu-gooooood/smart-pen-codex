# BLE bench and existing Windows/web integration

## Explicit boundary
The BLE service is **SYNTHETIC BENCH ONLY**, separate UUID from any future production service. Firmware emits VALID=0/CONTACT=0/GAP=1, device0x42454e43, page0xffffffff; the existing web app must show no handwriting for these samples. Bench proves transport plumbing, not nib coordinates. Host refuses this service unless `--allow-synthetic-bench` and an explicit address/device are provided. Use a separate bench database. Windows pairing, actual BLE radio and hardware flash durability have not been tested here.

## Transport contract (frozen)
Service `7c3f0001-7ad1-4d6f-963a-72b30000beef`; TX0002 notifications, ACK0003 write-with-response, INFO0004 read.
48-byte SP packet splits into three20-byte notifications: magicB1 (u8), fragment index0..2 (u8), transfer ID=sequence low16 (u16LE),16-byte payload. Strict in-order assembly, no interleaving, maximum2s; clear partial data on reconnect/error. No ACK for corruption/missing fragment. Firmware retains immutable current packet across reconnect until exact matching ACK, retransmits; a reboot uses a new session. This bench is stop-and-wait, not high-rate performance proof.
ACK20 bytes: `AK`, version1 u8, reserved0 u8, sessionu64, sequenceu32, CRC32 over first16 bytes. No device field: approved BLE identity + expected packetdevice bind the connection. ACK only after host SQLite FULL commit and contiguous frontier. Firmware must verify link encrypted/authenticated/bonded and configured approved peer identity plus exact session/currentsequence. CRC alone is not authorization. No ACK-driven erase occurs in bench.

## Windows bench receiver
Install Python3.11+, `bleak==3.0.2`. Pair the configured board via Windows/passkey displayed on board UART, according to bench README. Receiver explicitly requests pairing; platform policy may additionally require OS settings.
```
python software/windows_ble.py --address YOUR_APPROVED_BLE_ADDRESS --device 1111838275 --db bench.sqlite --allow-synthetic-bench
```
Device1111838275 is0x42454e43. Receiver exits on disconnect; rerun same command/database to resume same boot session. Notification overflow is an error, not silent ACK. Never auto-approve unfamiliar device addresses. This code uses Bleak's official `BleakClient(pair=True)`, `start_notify`, and `write_gatt_char(...,response=True)` interfaces; [API](https://bleak.readthedocs.io/en/latest/api/client.html), [Windows backend](https://bleak.readthedocs.io/en/latest/backends/windows.html). Python mock tests exercise durable-commit-before-ACK with a second SQLite connection; they do not emulate Windows radio security.

## Reuse actual existing upper application
`software/upstream_web.py` imports the **unchanged original** `digital_pen.engine.server.create_app`, `EngineService`, `WritingSession` and original scoring method. It does not fork a new frontend or implement camera processing. One selected device/boot-session/page is loaded from the durable journal into original sessions, exports and WebSocket schema; other pages never overlay. Original undo/start/finish/score APIs remain present. Camera photo/scan feature is unavailable rather than faked. Default mode is startup replay. Explicit `--live --view-id NAME` enables incremental durable-journal→original live canvas events, described below; physical BLE/camera accuracy is still untested.

Pin/check out the original source at`0f8b569176c77dad34aaf83bb008eb118c9f1208`, install its PC dependencies and engine extras. Add its `digital_pen_ov5640/pc/src` to PYTHONPATH (PowerShell):
```
$env:PYTHONPATH="C:\path\digital_pen\digital_pen_ov5640\pc\src"
python software/upstream_web.py --db records.sqlite --device 42 --session 123 --page 1 --static-dir C:\path\digital_pen\digital_pen_ov5640\web\dist
```
Build original web/dist through its existing npm workflow first. Server binds127.0.0.1:8765 only. `/api/pen/provenance` reports selected source/session/page and lack of physical validation. Do not expose the original API remotely: it was designed localhost-only and includes AI settings endpoints. Replay database/page selection remains explicit.

## Verified integration
With original PC dependencies available:
```
# POSIX example; Windows set corresponding environment variables.
DIGITAL_PEN_SOURCE=/path/to/original/digital_pen_ov5640/pc/src python -m unittest discover -s tests -p test_upstream_web.py -v
python -m unittest discover -s tests -p test_windows_ble.py -v
```
Real upstream FastAPI TestClient successfully exercised durable records→two separated strokes on page1 (page2 excluded), `/api/session`, SVG export, `/ws` hello and original undo event. Original module imports include OpenCV; test clearly skips when dependencies/source are absent. In this environment it was run and passed, not skipped. Existing UI was not visually/browser tested; Windows Bluetooth was not hardware tested.

## Full verification gate (no silent skips)
Use`python software/setup_host.py --venv PATH_TO_NEW_LOCAL_VENV` to create an explicit isolated environment and install pinned host dependencies. It rejects existing directories; no global packages are changed. Then use its Python:
```
python software/verify_host.py --upstream-pc-src /path/to/original/digital_pen_ov5640/pc/src
```
This gate fails if a required module/source/C compiler is missing or if **any** unittest skips. `cc` is needed for C/Python ABI checks; Windows users can use WSL/developer toolchain for this gate while the BLE client runs natively. Ordinary unittest discovery may skip upstream-only tests; never report that as the full integration gate.

## Live durable-journal view
Run the BLE receiver into a journal and the existing-web adapter against the same path:
```
python software/upstream_web.py --db records.sqlite --device 42 --session 123 --page 1 --live --view-id my-page-1 --static-dir PATH_TO_ORIGINAL_WEB_DIST
```
Do not use these fixture IDs for the bench: its invalid synthetic samples deliberately produce **no ink**. Production valid records require actual calibrated hardware. `--session` is a boot session, not a UI writing session. A device reboot/new page requires explicitly selecting a new boot/page and a new view ID; it is never silently overlaid on old paper.

The tail uses the existing(device,session,seq) index, seeks strictly after persisted cursor and no farther than the contiguous durable ACK frontier. It reads at most128 records each50ms(default), coalesces current `tip`/`open` updates per batch, and emits original `stroke` records at contact/loss boundaries. No EOF-per-poll finalization or whole-history rescan occurs. An inactive partial stroke closes after500ms transport silence(default); clock/sequence/page/validity/confidence/GAP discontinuities also close it. Previously observed points remain, with no interpolated bridge. Open paths cap4096 points; exceeding the cap creates a documented continuity boundary, not unbounded memory. These rates/timeouts are conservative software defaults, not measured radio/accuracy guarantees.

Cursor, active path, metadata and newly completed strokes commit to SQLite in one transaction before corresponding WebSocket events publish. Normal polls only insert newly completed strokes; they never rewrite old stroke history. An async actor lock serializes tail changes and original REST mutations; infrequent UI mutations reconcile the visible stroke rows. Clear/start fence off all already-durable records so old backlog cannot reappear. Undo removes the last completed stroke and discards an open preview conservatively. Finish finalizes the current preview as an explicit user boundary, then consumes but does not draw subsequent records until start.

Persistent `pen_views`/`pen_view_strokes` tables are a projection only: the raw journal remains untouched. Browser reconnect gets original `hello` plus current `open`; it does not stop the actor. Process restart restores cursor and edits, closes any prior active path as known restart loss, then continues after the cursor. Reusing a view ID for another device/session/page is rejected. An OS advisory lease rejects simultaneous projectors for the same view; lockfiles are harmless retained metadata. Windows lock branch is implemented but only POSIX lease behavior has been exercised here. Rawdata deletion/retention is not managed by this view.

WebSocket subscriber queues stay bounded. If a queue fills, obsolete event backlog is replaced with authoritative original `session` and current `open` snapshots rather than silently omitting finalized strokes. UI stroke IDs remain stable; reconnect and replay do not duplicate rendered strokes. Durable-projection failure stops the tail and emits an `end` error rather than retrying partial state blindly.

Five tests use the real original FastAPI/WebSocket app while another SQLite connection appends valid **test fixtures**: live tip/open/update/contact-end order, no early stroke completion, page/session filtering, duplicate record, undo/clear/start/finish, browser reconnect, process restart, queue resync, view lease and timeout loss. No frontend screenshot or physical radio test is implied.
