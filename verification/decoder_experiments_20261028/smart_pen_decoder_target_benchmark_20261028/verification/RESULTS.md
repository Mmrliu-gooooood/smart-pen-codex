# Build-only verification, 2026-10-29 UTC

No board connected, no flash/RAM load/device read command executed, no upload or GitHub writes.

- Frozen source manifest: FROZEN_SOURCE_SHA256SUMS, all 31 entries verified locally.
- ESP-IDF v5.4, real Xtensa ESP32-S3 build: default disabled PASS; explicitly enabled PASS.
- Independent enabled reconstruction into build-repro: byte-for-byte binary match (repro-hashes.txt).
- Latest enabled image: 216096 bytes, SHA256 `8c56bdbe92b3f55906b2de6f9d6d735ef5b6781b974a2f2d208de1e13775a617`.
- Image inspection: internal DRAM/IRAM plus small RTC segment; no IROM/DROM. See image-info-enabled.txt. Experimental RAM load feasibility is build evidence only, not physical startup evidence or execution consent.
- Static source + linked symbol deny checks PASS: no camera/LED/GPIO hardware provider, radio init, NVS mutators, Flash/partition writes, OTA or eFuse writers. SDK UART0 and secondary USB console output are explicitly exceptions to inert pads; see README_ZH.md.
- Seven frozen pixel fixtures: three 200px full-FOV expected NOFIT; three upstream-continuous cropped successful windows; blank NOFIT. Ten host cold/warm checks PASS, including preserving failure output/clearing prior and successful oracle coordinates. Host functional evidence only, no timing used as target performance.
- RLE fixture round-trip and PGM SHA256 checks PASS.
- Eleven serial parser unit tests PASS, including many malformed variants. Synthetic parser input is not a real serial capture. Parser supports repeats1..10, validates exact sample set, latency integer/finite constraints and independent manifest oracle; `identity_verified=false`, `overall_pass=null` always: schema1 cannot authenticate board/build or user log. No overall device acceptance. CLI returns2 even on functionally consistent logs because identity is unverified; status1 means observed functional failures, malformed/incomplete captures are rejected. Internal run, explicit PSRAM skip when absent, header ordering and preceding successful cold for each warm are mandatory.
- On-target decode microseconds, heap/stack watermarks, correctness and actual initialized PSRAM comparison: NOT RUN. Default pure-RAM profile cannot initialize PSRAM; optional guarded codepath is not a built/validated PSRAM board profile.
- Main stack is configured 16KiB, Gray8 allocation 40000 bytes plus caller workspace; compiler .su describes per-function static frames, not full runtime stack. Runtime_config prints target sizeof workspace; host reports21888. Heap allocation failure reports skip instead of decoding through NULL.
- Current full200px failure baseline stays frozen; new continuous-paper candidate lives elsewhere and must not be silently substituted.

The SDK automatically prints generic flash suggestions at end of a build. Those lines are NOT project instructions. README explicitly forbids using them for this RAM image. Keep binaries/backups private; no bundled device command, no automatic flash loader.
