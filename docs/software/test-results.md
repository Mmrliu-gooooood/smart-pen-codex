# Software verification record — 2026-10-27

Source audit pin: `0f8b569176c77dad34aaf83bb008eb118c9f1208`.

## Executed (not merely proposed)
- Fresh isolated venv created by `software/setup_host.py`, requirements from `software/requirements-host.txt`; no global installation.
- `host_verify_venv/bin/python software/verify_host.py --upstream-pc-src ../source/digital_pen_ov5640/pc/src`: **46 tests PASS, zero skipped**, including eight acceptance and eight rigid calibration geometry tests contributed by other workstreams; strict portableC executable PASS. Subsequent additions may increase count; rerun rather than relying on this snapshot.
- Five live original-app tests additionally pass incremental append/order, contact/loss finalization, undo/clear/start/finish, page/session filter, browser/process restart, bounded queue resync, exclusive view lease and timeout loss.
- Actual original FastAPI app: journal→selectedpage strokes→`/api/session`, `/api/export.svg`, `/ws` hello, original undo event PASS. This was not a substitute mock server.
- Windows BLE Python client with mock transport: malformed partial transfer ignored, next fullpacket committed, independent SQLite connection observes durable frontier BEFORE ACK write, explicit synthetic opt-in enforced PASS.
- ESP-IDF bench C/Python fragments and ACK security-state tests PASS (including unauthorized/unencrypted/unauthenticated/unbonded/not-sent rejection, stale/current/future/session mismatch and20-byte corruption).
- Explicit sequence rollover, clock regression and equal-time boundaries PASS.
- C/Python wire agreement532 vectors;48 corruption positions and five semantic-invalid recalculated-CRC frames rejected.128 source-generated canonical codec vectors across four sections and gridedges PASS.
- Sixteen synthetic known-grid grayscale images→C direction extractor→C decoder PASS; solidblack/white reject. **Not real image validation.**
- Portable NOR simulator: all52 possible byte cutoffs before complete body+marker, tornbody, failed body-sync, failed postmarker-sync, fault latch, reopen/rescan, no overwrite/full PASS. Header/CRC rejects corrupted records.
- ASan+UBSan portable executable PASS with `ASAN_OPTIONS=detect_leaks=0`. Default LeakSanitizer failed because sandbox ptrace is unsupported; no leak-check claim.

- Actual official ESP-IDFv5.4 ESP32-S3 builds PASS: defaultdisabled225440B; explicit-enabled synthetic BLE558800B. SDK/toolchain pins, reproducible commands and hashes in `bench_idf.md`. No board was flashed.

## Not tested / not delivered as production
No physical camera/pen/lens/printedpaper, BLE radio/Windows pairing, actual flash power-cut, OTA update/rollback, battery runtime, continuous24h recording, handwriting accuracy or frontend visual browser testing. Decoder is canonical image-free subset; image harness knows grid in advance. Existingweb live journal integration has logical API/WebSocket tests, not visual/browser or physicalBLE validation. ESP-IDF bench build record is maintained separately in `bench_idf.md`; it emits invalid synthetic packets, not real pen strokes.

The fullgate intentionally fails missing dependencies/source/compiler or skipped tests. Ordinary `unittest discover` can skip the originalapp test when dependencies are absent and must not be described as a full integration pass.
