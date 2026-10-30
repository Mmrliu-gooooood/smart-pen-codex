# Camera v2 independent bounded correctness review

Reviewed 2026-10-29 UTC. This is a software-only review, not approval to connect, power, flash or use any camera. The purchased custom module is SC035HGS; this candidate only contains the SC031GS driver. Unknown profiles remain rejected and the reviewed-profile registry remains empty.

## Inputs and preservation

The source archive SHA256 is d706e419c81e0c5967670fb9c88a26b957baa47ddba33ca5605eeb2cee2ae5f8. All 206 regular archive members match the source directory byte-for-byte; the candidate's 192-file source manifest passes. Tests and SDK builds run in this isolated review directory or temporary directories. Original v1 and v2 sources and logs are not changed.

## Scope and conclusion

The v1 reset-table boundary bug is corrected in v2: the reset table now has a terminal entry; each writer call supplies the actual compile-time array count; the writer verifies the terminal entry and all preceding entries before any mock bus write, then uses a count-bounded loop. It propagates nonzero write errors and stops. VGA and 200-table call sites pair the selected array and count. The existence or testing of the 200 table does not qualify a physical 200×200 mode.

Fresh original host regressions passed under ASan and UBSan: portable capture, SC031GS driver, checked SCCB reads, table writer, actual esp_camera init/probe/reset chain, HAL cleanup, IDF backend and ROI/lease edge tests. This includes the actual reset path previously omitted, all 109 initialization write-failure positions, and all 6 checked-read failure positions. Hardware, FreeRTOS and bus behavior are mocked. LeakSanitizer is disabled, so this is not leak proof.

The additional independent test uses explicit CHECK statements that remain active with NDEBUG. It covers every exact-allocation prefix of all three tables, insertion of an early terminator at every preceding position, all 255 invalid terminal values, exact successful write address/value ordering, and positive nonzero failure propagation at every write. It passes 26,829 checks in each of ASan/UBSan O1 and NDEBUG O2 builds. Counts include mock-bus assertions and must not be presented as 26,829 independent scenarios.

## Static review boundaries

- The actual wrapper always constructs VGA/Gray8 and verifies ID/window/clock configuration. Its registry is empty; both SDK fixture main functions only log and do not invoke start.
- The common upstream esp_camera_init entry is not a general untrusted-configuration API: it dereferences config and cam_config indexes resolution before the sensor set_framesize bounds check. Current wrapper uses a non-null fixed valid VGA configuration. Do not expose raw configuration, direct enum-driven camera initialization, or treat this package as general hardened camera SDK support without additional checks.
- Internal table counts must remain actual array counts, not externally supplied arbitrary pointer/length pairs. The prevalidation itself reads within the caller-provided actual array boundary.
- init_status is currently a no-op returning zero for SC031GS. This review does not approve adding other sensors while retaining the broader upstream ignored-return pattern.
- HAL timestamp follows low-level start/manual VSYNC and is a software boot-time sample. It is not an exposure midpoint or a measured first-DMA event and cannot establish pressure/image alignment.
- Source-level pin range and GPIO-valid checks are necessary but cannot establish a physical board's reserved Flash/PSRAM pins, power domain, level compatibility or safe-off sequencing. Those remain reviewed-profile prerequisites.
- Both builds deliberately disable PSRAM initialization and have no profile. Their successful link does not establish available runtime memory, electrical safety, PCLK rate, frame correctness, actual camera identity, latency, accuracy, battery runtime or manufacturability.

## Outcome

Fresh ESP-IDF v5.4 builds completed successfully in both disabled and enabled-compile configurations. The narrow reset-table and error-propagation correctness fix passes independent host checks and fresh SDK compile/link checks. No physical readiness is granted. Keep original v1 withdrawn, keep v2 default OFF, and keep the whole pen NOFAB. The larger application integration, actual supported camera module/pinout, PSRAM configuration, measured clocks, exposure, pressure synchronization, mapper and physical tests remain open.
