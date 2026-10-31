# Disabled host capture→application adapter candidate

2026-10-31. **Host-only SYNTHETIC candidate; NOT ADOPTED into active firmware. NOFAB / NOPOWER.** No GPIO, PCB, power hook, production profile, camera mode, calibration or active source changed. Provider stays NULL and capture profile registry stays empty. No SDK rebuild, hardware execution, purchases or external writes.

The user's stable existing camera is OV5640 imaging visible black dots (confirmed06:01UTC). That is an empirical visible-first baseline, not SC031GS electrical/optical qualification and not IR evidence. This adapter does not accept OV5640 JPEG/RGB frames or mislabel them as SC031GS RAW8. Offline sample analysis/conversion would require an explicit separate source/format contract. No further setup question was asked.

## What is implemented
`src/adapter.c` bridges unchanged archived SC031GS capturev2 into the exact current `pen_app_input` ABI through a host sink callback. It does not create a `pen_board_provider`. Dependency hashes bind the accepted capture fixes and current application sources; upstream is esp32-camera f37e65608f709bd94846dee01d947f02ae07c0b0 plus archived patch, not pristine upstream. Capture v2 remains separate from the active application.

- Explicit compile gate `PEN_ADAPTER_HOST_TEST` defaults0; separate runtime opt-in. No initialization/power action in adapter init.
- Eight-event fixed queue. Producers can supply events out of order before a certified watermark. Drain sorts timestamps, equal-time edges before frame before idle; equal-time edges preserve arrival order. Never retimes a frame to poll time.
- Late event at/below sealed watermark, overflow, bad level, sink failure or lease loss causes terminal fault, stops capture/releases held frame, clears queue and calls mandatory error sink. The consumer must stop recording/surface failure, not silently continue. No fake GAP/coordinate is fabricated to hide loss.
- At most one captured synthetic frame lease; zero-copy softwareROI with original640stride. Successful enqueue transfers the lease. Sink is called while held; release exactly once after it returns. Invalid input can stop capture/release the attempted lease; API header documents this distinction from PA_STATE/no-transfer rejection.
- ROI origin only available for the exact current frame pointer while dispatch owns a valid capture lease. Sidecar contains full dimensions, origin, frame/source identity. No origin-to-tip geometry is invented.
- Zero-initialized storage required. Active/reentrant/faulted reinit rejected; fault is terminal. Ordinary nonfault stop is idempotent; no warm camera restart implemented.

## Deliberately missing product behavior
The caller must provide an actual safe producer watermark, initial contact/IRQ levels, capture acquisition and error scheduling. An empty queue or wall clock does not prove all earlier frames/edges arrived. This code is single-owner, not ISR/thread safe. It does not implement pressure hardware, event acquisition threads, BLE, board actions, real storage transactions outside the synchronous pipeline, or sleep/maintenance policy. `usb_sleep_allowed=0`; no sleep authorization. `storage_pending=0` is confined to the host synchronous test model, not a claim about real pending work.

`pa_idle` delivers a no-frame observation for timers/timeouts; pipeline stale/GAP policy is unchanged. It does not force an immediate synthetic observation or gap independently of the configured pipeline. No reuse of old pixels/VALID is possible. Capture timeout/fault handling itself remains the unchanged capturev2 implementation.

Actual consumer test calls unchanged pipeline/store/recorder/contact/decoder code. Input remains SYNTHETIC and camera_qualified0, mapperNULL. Its rejecting test mapper is invoked manually to verify sidecar availability—not by the disqualified pipeline and not as physical mapping proof. No VALID coordinate is produced. A future real mapper needs calibrated geometry and a separately reviewed binding policy.

XCLK10MHz is requested/configured clock, NOT PCLK or measured25fps. No clock change occurs here. Software ROI is not resize/sensor200mode/120fps/6mmFOV. Timestamp is capture software boot time, not exposure midpoint. No exposure microseconds/PLL changes. Actual backend's one-init-per-boot and unqualified PSRAM runtime remain blockers.

## Reproduce
From this directory: `python run_tests.py`. Requires existing adjacent `../recovery_20261031`, Python and GCC; no network/device/SDK needed. `verify_dependencies.py` fails if source dependencies changed. Executables use temporary directories and are removed. `ASAN_OPTIONS=detect_leaks=0` is explicit: ASan/UBSan, not leak-sanitizer qualification.

`verification/09_final_suite.log`: four suites × normal/NDEBUG/ASan+UBSan =12 passing configurations. Failure suite296 explicit assertions per configuration (not296 independent physical cases). Includes six event permutations, cutoff/ties, reentry/reinit, overflow with held frame, bad/source/frame/time identities, copied/stale ROI binding, secondROI, cleanup and sink failures, compile-defaultOFF/providerNULL/profile-empty, real application integration.

Fresh unchanged capture regression:8 authored groups PASS in `capture_regression.log`; source manifest192 files PASS. Fresh existing application regression:3 unittest entrypoints PASS in `application_regression.log`; sanitizer env used where supported by each original harness, not a blanket claim all internals are sanitized. No whole-repo native/SDK/hardware regression run.

TDD evidence: logs01/02/03/04/05/08 preserve six expected failing executions and their green successors. Failed historic logs are evidence, not current failures. `REVIEW.md` distinguishes independent standards/spec review, fixes and remaining limits. `MANIFEST.json` hashes all delivered files; `DEPENDENCIES.json` binds external source paths.
