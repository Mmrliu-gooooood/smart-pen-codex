# Continuous target benchmark build-only results — 2026-10-29 UTC

## Status and identity

No physical ESP32-S3 was connected, read, loaded, flashed, erased, or timed. No upload/GitHub write. Default disabled and enabled pure-RAM configurations compile/link with real ESP-IDF v5.4 / Xtensa GCC14.2 / esptool4.12. Final binary 290480 bytes; SHA256:
`9845055ad9f77341dd2bb34949710f6302d8ccc8852123489c18cbe3353d9560`.

Independent build directory yields identical binary (repro-hashes.txt). Source/header/fixture/provenance/tool freeze is FROZEN_SOURCE_SHA256SUMS; all entries verify. Candidate code matches its independent-reviewed V2 snapshot; the legacy core and codec match frozen historical source, including function body unchanged. CMake renames only the old public entrypoint to prevent symbol collision. Candidate and old application trees unchanged.

## Functional and oracle checks

- Six full 200×200 fixtures: three ideal continuous upstream 5/6/7mm phase0 successes, one 45°NO_GRID, independent deep-border-ink case063 DETECTION, one 9mm density stress DETECTION (outside requested5–7mm operating range).
- Same frozen pixels reach both decoder calls. Original core rejects all six with -2. Wrapper succeeds on three and rejects the other three with the specified statuses. Twelve host functional replays pass raw status/coordinate/36direction/crop/edge/transform oracles, untouched input, failure output-preservation. No host latency is reported as MCU performance.
- RLE pixel-byte round-trip, file and raw-pixelSHA256 all pass. Decoder receives no coordinate/angle/transform/answer hint. Original priorNULL; wrapper is cold-only, no warm benchmark.
- Independent rendering geometry checks all 108 positive-case grid centers and upstream direction symbols. Max frame errors 0.100982/0.060461/0.374925px under respective 1.2/1.0/0.857143px bounds; inverse numerical round-trip passes. This is synthetic truth, NOT actual physical/nib accuracy.
- Thirteen parser tests pass with many malformed variants. Mandatory whole-record sequence, header source/fixture/scope, full-libc probe, exact repeat/fixture/decoder sample identities, finite integer timing, independent output oracle, no geometry on failure, memory samples and PSRAM skip. Functional consistent logs still return exit 2, identity_verified=false and overall_pass=null; there is no overall device pass/authentication.

## Real target build/link checks, not execution

- Effective config: RAM-only + PURE_RAM_APP, benchmark default off, main stack 16KiB, configured CPU 240MHz, reproducible build, no PSRAM/radio.
- Important old-build correction: the old frozen benchmark used nano printf with PRId64. It is historical only and not recommended for execution. Here nano is disabled in effective config, forbidden by compile-time#error, link map contains no libc_nano.a. Full libc.a libc_a-vfprintf.o, _vfprintf_r, _dtoa_r and snprintf are linked into IRAM. See full-libc-link-excerpt.txt/effective-config-excerpt.txt.
- Actual target code runs snprintf 64-bit+double and strcmp before samples; on failure returns fatal. Mandatory separate format_probe repeats values for host parser. That target selftest has NOT been executed. Host mock tests cannot validate target libc runtime.
- image_info: only internalDRAM/IRAM + 28-byte RTC data load segments. No IROM/DROM mapped segments. Some ELF section names still contain'.flash' but their load addresses are internal, so section names alone are not a flash-operation claim.
- Linked deny checks find no camera/LED/GPIO providers, Wi-Fi/BT initialization, NVS writes, flash/partition writes, OTA, eFuse writes. SDK UART0 +secondaryUSB console output is an explicit pad-activity exception; requires real-board wiring review.
- ABI compile-only static_assert with the actual Xtensa compiler: old workspace 21888 bytes; continuous workspace 31104 bytes. Allocated in internal heap, not task stack; image 40000 additional bytes. Total input/workspace 71104 bytes excludes all RTOS/libc/fixture/static/stack allocations. Allocation failure is fatal rather than a false benchmark success.
- Compiler static stack frames are in compiler-stack-usage.txt; these are not peak call-chain nor measured runtime high-water. ELF size section totals include alias/dummy regions and cannot be converted directly to remaining heap. Actual allocation viability, stack and heap require device logs.

## Deliberate limitations

No PSRAM or hardware profile established; pure RAM cannot initialize PSRAM. No user 16MiB assumption, partition rewrite, unconditional erase, or auto-device script. Board identification, permission to interrupt old digital_pen firmware, private full-capacity backups and verified restore plan precede any manually planned RAM execution.

Candidate remains limited: fractional FOV 17/36, in-plane rotation 60/96 in finite ideal synthetic sweep. The benchmark does not enlarge qualification coverage, bypass application safety gates, produce physical nib VALID, or prove realtime FPS. SDK build logs print generic flash commands; README explicitly forbids using those suggestions for this RAM image.

## Reproduction

See README_ZH.md. Normal host/build checks are standalone using included frozen inputs. freeze_legacy_oracles.py is a local recalculation helper; freeze_independent_geometry.py is a provenance-extraction helper requiring the original candidate source tree and is NOT part of ordinary rebuild/verification. check_static.py requires locally generated build/nm/image_info/map artifacts, not a sibling source repository. The local legacy/candidate snapshot hashes freeze provenance.
