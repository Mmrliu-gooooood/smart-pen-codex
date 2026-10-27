# ESP32-S3 synthetic BLE bench target

**Not pen firmware; not hardware tested.** `firmware/bench_idf` is an ESP-IDF/NimBLE transport integration project referencing the portable packet codec. It neither initializes a camera nor decodes paper, measures pressure, logs to flash or performs OTA. No pin mapping is guessed.

## Fail-closed test identity
- Default configuration does not start BLE: explicit `PEN_SYNTHETIC_BENCH` menuconfig opt-in and a valid manually provisioned central identity address are required.
- GAP name `PEN-SYNTHETIC-BENCH`, INFO characteristic explicitly `SYNTHETIC_BENCH_ONLY;device=42454e43;NO_VALID_COORDINATES`.
- Every sample has device `0x42454e43`, page `0xffffffff`, confidence0, GAP set, VALID and CONTACT **clear**. Normal stroke consumers must not draw it.
- Random nonzero64-bit boot session; sequence0 first. One immutable packet in RAM remains across disconnect and is retransmitted every250ms until its exact ACK. No sequence wrap. A reset starts a fresh session and loses any unacknowledged RAM record; this is **not offline persistence**.

## Service and transport
Service `7c3f0001-7ad1-4d6f-963a-72b30000beef`:
- TX notify: `7c3f0002-7ad1-4d6f-963a-72b30000beef`
- ACK write-with-response: `7c3f0003-7ad1-4d6f-963a-72b30000beef`
- INFO read: `7c3f0004-7ad1-4d6f-963a-72b30000beef`

A48-byte SP packet becomes three20-byte notifications: `B1 | index u8(0,1,2) | transfer_id u16LE | payload16`. Transfer ID is sequence low16, not an integrity/security primitive; full packet CRC/session/sequence are authoritative. Host must enforce exact ordering/count,2s assembly timeout, clear on reconnect and accept only expected device identity.

ACK20 bytes: `AK | version1 | reserved0 | session u64LE | through_seq u32LE | CRC32(first16)`. Host sends only after durable journal commit. Firmware checks exact length, header, CRC, session, and not-future sequence; stale ACK is idempotent. Exact current ACK advances to next synthetic sample. ACK is observable only: **never erases storage**. Both notification and ACK paths require approved peer identity plus encrypted, authenticated, bonded security state. User must enter a fresh random console-displayed pairing passkey on the approved PC. Existing bonds are never silently deleted or replaced; NVS init errors do not auto-erase NVS.

This is a bench authorization mechanism, not a finished production provisioning/pairing UX. Trusted UART/console access is required. Identity address provisioning must use the central's identity, not its changing private OTA address. Address allowlisting alone is not security; authenticated encrypted bond is additionally mandatory. A malicious but approved host could falsely ACK its own data; cryptography cannot prove storage persistence, so trust the host application. No firmware secrets are printed except the intended transient bench pairing passkey.

## Build
Reference API target: official ESP-IDF v5.4. Use an isolated ESP-IDF installation, do not reuse unknown desk sdkconfig.
```
. /path/to/esp-idf/export.sh
cd firmware/bench_idf
idf.py set-target esp32s3
idf.py menuconfig   # explicit bench opt-in + approved peer identity/type
idf.py build
```
Default disabled mode is safe to compile. Do not flash unspecified hardware or assume this validates any camera/charging design. Even a successful compile only establishes API/link compatibility, not BLE interoperability, pairing security behavior or device performance.

Official API provenance:
- [Espressif ESP-IDF v5.4 Bluetooth guide](https://docs.espressif.com/projects/esp-idf/en/v5.4/esp32s3/api-reference/bluetooth/index.html)
- [Official v5.4 NimBLE peripheral example](https://github.com/espressif/esp-idf/tree/v5.4/examples/bluetooth/nimble/bleprph)

Before production select a maintained ESP-IDF patch release and reassess security advisories; the v5.4 pin here is a reproducible integration target, not a recommendation to deploy an old release unchanged.

Portable bench wire checks (host C compiler, no SDK needed):
```
cd firmware/bench_idf
cc -std=c11 -Wall -Wextra -Werror -pedantic -Imain -I../portable \
  main/bench_wire.c ../portable/pen.c host_test.c -o /tmp/pen-bench-wire
/tmp/pen-bench-wire
```
These passed authentication-state rejection, stale/current/future/session ACK handling, corruption at every ACK byte and fragment layout. They do not simulate the BLE controller or OS pairing dialog.

## Actual compile evidence — 2026-10-27
Both configurations **built and linked successfully for ESP32-S3**, using real vendor headers/libraries/compiler (not API stubs):

| Configuration | App binary bytes | SHA-256 |
|---|---:|---|
| Default disabled |225440|`6bc86ad07225a04bfb02a21fb3dd033ab1b816204a0bf084524b76293cdc341e`|
| Explicit synthetic enabled, dummy approved peer |558800|`67f01fcc464d8f7d3a46a3f8ba26e287f076a89f793158ce680e1c1f5a55b6a4`|

Enabled binary uses0x886d0 bytes of the default1MiB application partition (47% free). This includes framework overhead, not measured RAM/power/runtime. Binary hashes identify this build only; build timestamps/absolute paths may change hashes on another system. Binaries/build trees are **not delivered or committed**; source and this small report are the deliverables. No flash or monitor command was run.

- SDK tag `v5.4`, peeled source commit `67c1de1eebe095d554d281952fde63c16ee2dca0`, recursively pinned submodules.
- Compiler `xtensa-esp-elf-gcc (crosstool-NG esp-14.2.0_20241119) 14.2.0`.
- Python3.12.14; CMake3.31.10; Ninja1.13.2.
- SDK location `/workspace/shared/esp-idf-v5.4`; tools `/workspace/shared/esp-idf-tools` (outside delivery repository).
- Fresh build directories `/tmp/pen-idf-build` and `/tmp/pen-idf-build-enabled`.
- Default and enabled logs ended `Project build complete`; no compiler warning/error was reported for these source files. An initial configure attempt failed to locate Ninja; explicitly setting the installed Ninja executable resolved it. This is a resolved build-environment issue, not a device validation.

Commands used after cloning the official tag and running `install.sh esp32s3` (all tools installed under workspace):
```bash
export IDF_TOOLS_PATH=/workspace/shared/esp-idf-tools
. /workspace/shared/esp-idf-v5.4/export.sh
export PATH="$IDF_TOOLS_PATH/python_env/idf5.4_py3.12_env/bin:$PATH"
# The isolated environment also has: python -m pip install 'cmake<4' ninja
cd /workspace/shared/smart_pen_20261027/delivery/firmware/bench_idf
idf.py -B /tmp/pen-idf-build -D IDF_TARGET=esp32s3 \
  -D CMAKE_MAKE_PROGRAM="$IDF_TOOLS_PATH/python_env/idf5.4_py3.12_env/bin/ninja" build
```
The enabled compile copied generated default `sdkconfig` to `/tmp/pen_bench_enabled.config` and changed only:
```
CONFIG_PEN_SYNTHETIC_BENCH=y
CONFIG_PEN_APPROVED_PEER="02:00:00:00:00:01"
```
That address is a **dummy compile fixture, not an approved real user's device**, and was never used for connection. Build command:
```bash
idf.py -B /tmp/pen-idf-build-enabled \
  -D SDKCONFIG=/tmp/pen_bench_enabled.config -D IDF_TARGET=esp32s3 \
  -D CMAKE_MAKE_PROGRAM="$IDF_TOOLS_PATH/python_env/idf5.4_py3.12_env/bin/ninja" build
```
`tests/test_bench_wire.py` additionally cross-checks the C implementation against the Python bridge for fragment bytes and ACK security/session/CRC boundaries. Real Windows identity/RPA resolution, pairing dialogs, reconnect notifications, NVS power-loss and radio behavior remain hardware acceptance tests. In particular, pre-pairing rejection of an unrecognized identity is fail-closed but can prevent initial pairing when the OS presents a private address before identity resolution; resolve with a controlled provisioning flow, **not by weakening the authorization checks**.
