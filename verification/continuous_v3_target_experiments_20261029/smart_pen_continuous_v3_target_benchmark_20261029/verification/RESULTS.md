# V3 independent target benchmark — build-only 2026-10-29 UTC

**No device connection, RAM execution, flash read/write/erase or upload.** No S3 speed/heap-runtime claim. Final source/fixture/tool freeze is FROZEN_SOURCE_SHA256SUMS; V3 production core binding is SOURCE_BINDINGS.json, based on independently reviewed V3 snapshot1636084759c3ebfc358574f669ea5292b11ae4421145401e7c2ccaed12664ccf. The old V2 benchmark/candidate remain unchanged.

## Evidence completed

- Real ESP-IDF v5.4, Xtensa GCC14.2: default-disabled and enabled PURE_RAM builds pass. Independent build directory reproduces enabled binary byte-for-byte. Binary **275,344 B**, SHA256 **e8dd4f36bf318d9cbd13df2d690b025b31b0a39a76d7a3651b1f91696e05a86c**. Binaries remain local, excluded from delivery selection.
- Nine fixed full200px fixtures, **18 host functional comparisons**: old frozen core rejects nine; V3 succeeds on5 and rejects4 with expected status, crop/36directions/transforms/seed/iteration/model oracles. No host timing published as target performance.
- Five positive fixtures, **180 independent upstream rendering-grid centers**, direction symbols and inverse transforms verified. The two recovery examples are5.1mm scale and45°rotation. This is ideal synthetic truth, not actual printing/sensor/nib accuracy.
- Actual production-limit overflow fixture: `refine_stats=[864,65,0,0]`, status-4, failure output untouched. Max64 seed capacity unchanged; observed65 is the detected-overflow counter, not65 stored seeds. No-window-3 stats[26901,9,31,5]; deep ink/density preprocessor rejects have no refiner call and zero stats.
- **16 parser unit tests** pass (numerous malformed variants): mandatory instrumentation identity/scope, exact input/source binding, full-libc probe, every ordered sample and memory record, finite integer latency, output/transform/stats contract, overflow and trace call consistency. Only complete logs analyzed; consistent logs remain identity_verified=false, overall_pass=null and exit2.
- Lossless palette-RLE replay checked pixel-by-pixel and SHA256 for all9 PGMs. Runtime decode uses identical raw images, never oracle-derived geometry.
- True target ABI static_assert: core21888 +seed1536 +crop9216 =**32640B**; target header separately locks64-seed bound. Heap workspace shared sequentially between old/V3, plus40000B input; no second workspace and no stack-sized allocation.
- Effective config disablesnano; full libc.a vfprintf/dtoa/snprintf symbols inIRAM, no libc_nano.a inmap. Startup format selftest has not been physically run; host testing is not target libc validation.
- **Actual Xtensa disassembly** in target-callgraph.txt confirms continuous wrapper call8→`__wrap_pen_roi_decode_refined_transform`→real function. The benchmark-only shim captures outputs without changing core inputs/result/threshold. Capture-call mismatch or expected-search withzero coarse stats isfatal, and no complete follows. V3 timing includes its diagnostic copy overhead; oldcore is not instrumented. Not a clean uninstrumented algorithm-speed comparison.
- Image load segments are internalDRAM/IRAM +smallRTC, noIROM/DROM. Static deny checks show no camera/LED/GPIO/radio/storage/OTA/eFuse mutators. SDK UART0/USB console remain explicit pin-activity exceptions.

## Resource interpretation and limits

Palette arrays105864B +palettes125B are internalDRAM, not external Flash. Main stack16KiB plusRTOS/libc/fixture/static costs. ELF text135314/data139925/bss-labelled121688 includes dummy/alias sections; not a naive physical peak sum. See RAM_ACCOUNTING.md and compiler-stack-usage.txt. Build fit does not prove the72640B heap pair will succeed or actual stack margins. Allocation/capture failure producesfatal, no complete and no accepted partial statistics.

V3's recovery of19 previously diagnosed valid-scale and16 valid-rotation cases is evidence of bounded synthetic improvement, not all-geometry/physical qualification. Twenty no-complete-window cases must remain rejected. This small9-fixture target workload does not substitute for the full independent candidate suite.

## Minimal source and reproducibility

DELTA_FROM_V2.json distinguishes reused and changed/added source files; no old large snapshots/builds/review histories were copied. V3_BENCH_DELIVERY_ALLOWLIST.json selects source and compact current evidence, excludes all binaries, build directories and full disassembly. Full local build logs remain available but need not be duplicated downstream.

After normal build, tools/collect_build_evidence.sh regenerates nm/image_info/map excerpts, callgraph and ABI proof using local artifacts only. tools/check_static.py then validates production bindings and actual machine calls. One-time oracle-source extraction helpers are explicitly not ordinary runtime/build inputs. Core files and all9 input PGMs are byte-matched to the frozen candidate; generated matrices are exclusively post-return validation metadata.

Before any physical run: board identification, user agreement to interrupt existing firmware, private full-capacity backups and a known restoration plan. Never infer empty firmware or16MiB physicalFlash from the supplied N16R8 label. No unconditional erase/write/load script. README_ZH.md contains the unchanged safety gates.
