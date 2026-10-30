# Software delivery and honest integration boundary

## Source audit (2026-10-27)
Audited original commit `0f8b569176c77dad34aaf83bb008eb118c9f1208`.
- **Current desk firmware** is the separate `digital_pen_ov5640/usb_camera` ESP-IDF project. `usb_camera/main/usb_camera_main.c:1–60` documents v5.3 USB Serial/JTAG `TRACK`, ROI/overview/snapshot images, DPU1 envelopes, per-stream counters and payload CRC32. Wi-Fi is not started. The older root `main/app_main.c` remains a separate Wi-Fi/HTTP camera project; it is not the latest USB transport.
- PC `anoto/codec_adapter.py` wraps `microdots.anoto_6x6_a4_fixed`; 6×6 complete direction windows carry a coordinate and section modulo63. `window_consensus.py` searches windows and orientations; defaults require two supporting windows, confidence0.75 and at most one missing direction. Missing directions are enumerated, not observed.
- `pose/page_locator.py` explicitly targets an overhead camera. Default crop14 cells, seed700 dots, global page growth and spline geometry are not a pen-camera embedded implementation.
- `PageLayout.from_manifest` supplies string page ID, expected section and geometry. **Arbitrary page ID is not decoded from the paper**. Provision a unique, versioned manifest/page-number registry before emitting protocol page numbers. Sections repeat modulo63; duplicate sections and reused patterns can be ambiguous.
- Source profiles: A spacing3.5278mm, offset1.0583mm, radius0.3528mm; B1.0/0.167/0.100mm; C0.300/0.050/0.050mm. Source recommends1200DPI for C, not proof of usable printed/optical pen performance.
- `engine/core.py` owns tip detection, page mapping, stroke tracking and optional image-based ink processing on PC. Reuse scoring/session/web layers, but do not confuse image-derived window origin with calibrated physical nib coordinates.

## Implemented, runnable subset
1. `firmware/codec`: real integer-only canonical 6×6 `a4_fixed` position/section decoder, derived from the vendored MIT reference with license retained. 804 bytes sequence data, no heap, bounded manifest dimensions6..4096. Four secondary sequence searches and CRT reconstruct each axis; section integration is bounded by manifest size. Rejects unknown directions and missing/ambiguous substrings. Inputs already canonical: no optical dot detection, lattice fitting, orientation recovery, confidence estimation or consensus. A single accepted window is **not** production-quality evidence. Rotation/tilt/nib calibration and multi-window consistency must precede VALID output.
2. `firmware/portable`: explicit byte-order packet codec, CRC, contact/validity gate and power-cut-tolerant append-only NOR slot format with commit marker. Hardware-independent C11, not flashable board firmware.
3. `software/pen_bridge.py`: stdlib Python binary ingest to durable SQLite, cumulative contiguous ACK and replay to JSONL stroke events. Works with files/pipes on Windows/POSIX; see `integration.md` for new synthetic BLE receiver and actual original-web replay/live adapter. No new phone app.

## Wire v1 (48 bytes, little-endian)
| Offset | Field |
|---:|---|
|0|`SP` magic (2 bytes)|
|2|version1 u8|
|3|flags: contact1, calibrated-valid2, gap4; other bits rejected|
|4|device u32|
|8|nonzero session u64, unique per boot/reset|
|16|sequence u32, starts0; never wrap in a session|
|20|monotonic capture timestamp microseconds u64|
|28|provisioned page u32; zero invalid when VALID|
|32,36|physical tip x/y signed micrometres i32|
|40|confidence0..1000 u16|
|42|reserved0 u16|
|44|IEEE/zlib CRC32 of bytes0..43 u32|

CRC detects accidental corruption, not malicious peers. Device identity/session authentication, BLE pairing/encryption and authorization are integration requirements. Define page frame and calibrate consistently (source page-grid y is upward); do not silently convert to screen-down y. Provision page registry independently of CRC packets. Store every event, including releases, invalid samples and gaps. Never synthesize a line across uncertainty.

Gate contract: zero-initialize `pen_gate` at each session; supply a **fresh** sample/flags each observation. Debounce press, release immediately; invalid optics/calibration clears VALID immediately and marks recovery GAP. Threshold/debounce are configurable engineering placeholders, not measured defaults. Upstream must insert a release/GAP on stalled sensing; no timer task is provided. Sequence numbers count durable records, not observations. After append failure, stop the faulted recording session. A sync failure after writing the marker is uncertain: reconcile by a successful sync/readback of the same record, or reset to a new unique session; never retry the same sequence with different payload blindly. Reuse next sequence only if the prior write is provably uncommitted. Emit GAP for any lost observation and retain session identity across transport reconnect. No automatic firmware-side reconciliation is provided. Reset gets a new nonzero session; reserve/provision collision-resistant identity before first record.

## Offline durability and capacity
NOR backend must read/program erasedFF storage, only program1→0 and make `sync()` truly durable. Body48 bytes is synced before final DONE marker4 bytes; each slot64 bytes. Torn/corrupt slots are skipped, never repaired into fabricated points. Open scans storage to next occupied slot. Storage full returns−2; writes/sync failure−1, never success. Firmware must stop accepting unrecordable strokes, notify user and keep an explicit loss boundary. API deliberately has **no erase/garbage collection**; host ACK does not currently reclaim flash. Do not erase a page until all its records have authenticated durable ACK and a power-cut-safe erase/checkpoint policy has been implemented/tested.

At100 samples/s: wire48B =414.72MB/day, NOR64B =552.96MB/day continuously active;16MiB NOR≈43.7min active. At10% writing duty a24h elapsed target still needs≈55.3MB plus metadata. No24h runtime/storage claim is made. Cost-first microSD has capacity but requires a separate, validated filesystem/flush and power-cut strategy. No SPI/NOR/microSD driver is included. The log latches faults until a successful sync+rescan; higher-layer sequence reconciliation remains required.

SQLite uses WAL/FULL transaction commit before ACK. ACK is only highest contiguous durable sequence starting0; late/repeated packets are idempotent, conflicting duplicates rejected. Replay emits boundaries for missing sequence, page/session switch, time regression, >100ms interval, GAP, invalid/confidence-low or contact-up. The100ms/confidence750 defaults are conservative configurable policy, not a measured optimal pen setting. Lost seq0 means no cumulative ACK; do not discard it or silently advance the frontier.

## Hardware integration still required
Camera DMA/ROI and dot extraction, multi-window/orientation decoder, nib calibration across tilt/height, contact sensor pin/ADC calibration, sensor clocks/power sequencing, production-rate BLE/backpressure/radio validation (synthetic bench framing and authenticated ACK source now added), board flash/storage backend, secure signed OTA rollback/anti-rollback and recovery, sleep/wake, charge/battery safeguards, native Windows radio validation and production live-web performance/visual validation (host client + original API live journal subscription now provided). Pins intentionally not invented. Keep camera debug transport separate from coordinate path; never attempt to send raw video continuously over BLE.

The deliverable is a tested host-side/portable foundation, **not ready-to-flash full pen firmware**. No device, printed paper, lens, battery, BLE interoperability, power-loss on physical flash, OTA or handwriting accuracy testing occurred.

## Verification
From repository root:
```
python -m unittest discover -s tests -p 'test_*.py' -v
cc -std=c11 -Wall -Wextra -Werror -pedantic -Ifirmware/portable firmware/portable/pen.c tests/test_portable.c -o /tmp/pen-test
/tmp/pen-test
```
Python tests require Python3.11+ and `cc` for C crosswire/codec tests; bridge itself is stdlib only. Codec fixtures:128 windows, four sections,710×1000 grid including corners, generated and checked against vendored Python reference before freezing. Crosswire:532 vectors,48 byte-corruption positions and semantic-invalid recomputed CRC frames. These test logical coordinates, not optical accuracy. NOR tests simulate torn writes/sync failure/reboot/full; no actual flash tested.

## Additional tested scaffolding
`firmware/vision/canonical.c` accepts ONLY an exactly aligned6×6-cell grayscale image with known pitch8..64pixels, canonical orientation, dark dot on white cell and no real-world ink/occlusion. It thresholds cell moments and rejects centroids outside a narrow expected-offset band.16 synthetic images pass through pixel→direction→actual C codec. This is plumbing/compute scaffolding, not a camera-ready dot detector: missing grid acquisition, subpixel model, perspective/tilt, overlap/ink rejection and multi-window consensus are hard gates. Never use its success alone to set calibrated VALID.

`software/page_registry.py` enforces unique nonzero numeric page IDs and unique canonical section pairs(0..62 each), manifest bounds and positive finite pitch. Maximum3969 unique section pairs in this restricted provisioned registry; this is not a claim about all possible Anoto address capacity. Unknown, aliases and duplicates are rejected. Duplicate physical prints of a registered section remain indistinguishable. Firmware must test candidates and require exactly one accepted manifest; automatic on-device registry lookup is not wired yet. Protocol CRC has no manifest revision hash; deployments must bind registry/version to device session externally or extend protocol before mixed-profile use.

Press debounce can lose initial stroke onset. Raw-contact timestamp and pending-point buffering remain integration work; do not claim nib-down/start accuracy. Portable C tests pass with ASan+UBSan using `ASAN_OPTIONS=detect_leaks=0`; default LeakSanitizer is blocked by the sandbox ptrace environment, not a clean leak-test result.
