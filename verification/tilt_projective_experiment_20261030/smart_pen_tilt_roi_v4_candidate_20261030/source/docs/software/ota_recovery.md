# Controlled OTA / recovery adapter — 2026-10-28

## Implemented, not a claim of a qualified pen
`firmware/update` contains a real ESP-IDF application-update component, a portable admission/streaming policy, and host fault tests. Its `begin/write/finish` functions call the official OTA APIs; no placeholder network response claims an update occurred. The component does **not** provide a public HTTP/BLE update server, keys, bootloader flashing, eFuse provisioning, a camera driver, or hardware diagnostic results. Default Kconfig is disabled. No device was flashed, updated, rebooted or purchased during this work.

### Admission and stream
- Requires explicit `PEN_OTA_ALLOW_INSTALL`, SDK signed-on-update verification and bootloader rollback. A build with hardware anti-rollback enabled is rejected by this adapter: marking an image valid can update the hardware secure version, which would be an irreversible eFuse operation outside the present authorization. No eFuse function is called and no security config is silently enabled.
- Rejects unqualified default project/hardware strings. The running signed application project name must match the provisioned project; each hardware revision must have a distinct signed project-name identifier. The adapter enforces PROJECT == HARDWARE == manifest.project == manifest.hardware; the signed image descriptor must carry that exact identifier. An unsigned hardware string cannot alias another signed project. Both current running and boot-selected partitions must agree; current state must already be VALID. A pending candidate cannot install another image.
- Chooses only a different inactive application partition. Requires actual `ota_0`, `ota_1` and two-sector `otadata` infrastructure supplied by the integrating application. Does not alter the partition table or erase bootloader, NVS, raw-record storage or the running app. The first production/recovery image must be deliberately provisioned in a known-good OTA slot; a factory-only bench image is not silently converted.
- Manifest includes complete signed-image byte length, SHA-256, hardware string, signed project name and monotonically increasing integer version. Version must exceed both running signed `esp_app_desc.version` and persisted software floor. Candidate descriptor version must equal manifest version; project must match. Use canonical decimal `PROJECT_VER` (0..4294967295, no leading zeros) in the signed `esp_app_desc.version` field. Semver/non-numeric/unterminated/overflow versions are rejected. The SDK secure_version configuration depends on hardware anti-rollback, so this adapter deliberately does not use that field.
- Every begin/chunk/finish requires an authorized application operation, contact up, qualified power, durable recorded data and idle recorder. The owner task must obtain fresh signals and serialize update/recording; these booleans are not a substitute for measured battery thresholds or actual quiescence. No GPIO map is invented. A mid-write change aborts at the next checked call; interrupt-latency/power-hold-up behavior still requires hardware tests.
- Writes strictly increasing offsets and exact bounded size. Duplicate/out-of-order/zero/oversize chunks, unsafe state, write error, short image or hash mismatch terminate the transaction. `esp_ota_end` performs signed-image validation under the required SDK configuration. Descriptor checks and `esp_ota_set_boot_partition` follow only after success. Installation selects the verified image for the **next** boot and never reboots automatically.

## Boot validation and rollback
Call `pen_update_idf_boot_result` early after boot with measured diagnostic results. Mask bits are storage=1, protocol=2, power=4, contact=8, camera=16; all five plus safety gates must pass before mark-valid. Merely waiting is not a self-test. The camera/optical chain is presently unqualified, so an integrator must not invent that pass bit to complete OTA acceptance.

On a pending image, incomplete tests return INVALID_STATE and leave rollback active. Explicit diagnostic failure plus separate safe reboot authorization calls `esp_ota_mark_app_invalid_rollback_and_reboot`; if no previous bootable image exists, the vendor call can return an error and must be shown as recovery-required, not success. A reset before confirmation uses the SDK rollback path. No reset loop or automatic bond/NVS erase is added.

The application stores the new software version floor in NVS namespace `pen_update` and commits it **before** calling mark-valid. A failure or reset between floor commit and mark-valid may still boot the prior known-good image; the floor gates future installs, not the bootloader's recovery choice. Thus recovery is not bricked by that ordering. NVS failure prevents mark-valid. Physical power-cut reliability of NVS/otadata is not established by mock tests. NVS software floor is not tamper-resistant: physical flash rewriting or running arbitrary unsigned firmware can defeat it. Signed-on-update without hardware Secure Boot does not establish a secure boot chain. Production provisioning, key custody, secure boot/eFuse choices and physical rollback tests require a separate reviewed authorization.

## Integration contract
Add `firmware/update` as an ESP-IDF extra component. Initialize NVS without automatically erasing it on failure; allocate an all-zero `pen_update_idf` and use it from one owner task. Supply a manifest only from an authenticated update-management path, with signed image trust rooted in an approved public key. Hardware profile metadata is bound by enforced equality of the hardware and signed project identifiers (at most31 UTF-8/ASCII bytes), not by trusting a free-form unsigned string. This component does not install or generate a trust key.

A transaction is terminal after success or failure. Free/abort it before discarding the object. After power loss, restart transfer from byte zero into an inactive partition; no unsafe partial-image resume is offered. The current boot slot remains untouched until a complete signed image passes checks. Application-data logs and BLE durable ACK handling are independent and must finish or quiesce before update admission. Record-log recycling must never include OTA/NVS regions.

No application runtime calls these functions by default; integration into a real camera/pressure power task is still required. Build success does not prove update delivery, signature verification against a real signed image, radio transport security, boot recovery, hardware power safety or measured camera self-tests.

## Executed host verification
```
python -m unittest discover -s tests -p 'test_update*.py' -v
```
Three tests compile C11 with `-Wall -Wextra -Werror -pedantic`:
1. Portable policy: each safety/build gate, identity/version/size errors, ordering, truncation, digest/signature status failure, required diagnostic mask.
2. Actual adapter compiled against fault-injecting SDK mocks: active/boot-target exclusion, SDK write fault, hash/signature/descriptor rejection before boot selection, short transfer, durable floor before mark-valid, explicit rollback authorization.
3. Five insecure/disabled configuration variants: install disabled, signature check disabled, rollback disabled, hardware anti-rollback enabled, and mismatched hardware/project alias. All reject with zero OTA begin/select/mark-valid/reboot calls.

Mock SHA/signature routines only establish call order and error handling. They are deliberately not cryptography tests. Actual ESP-IDF compile status is recorded below when completed; absent a build record, do not infer SDK compilation from mock compilation.

## Official API basis
- [ESP-IDF v5.4 ESP32-S3 OTA documentation](https://docs.espressif.com/projects/esp-idf/en/v5.4/esp32s3/api-reference/system/ota.html): inactive-slot update, otadata, pending verification and rollback APIs.
- [ESP-IDF v5.4 Secure Boot v2](https://docs.espressif.com/projects/esp-idf/en/v5.4/esp32s3/security/secure-boot-v2.html): signed-image verification and trust-chain distinction.

The SDK version is a reproducible compilation target, not a claim that its patch level is suitable for unreviewed production deployment.

## Actual SDK compile evidence (completed)
Integrated with storage, recorder and contact modules in `firmware/runtime_idf`, using official ESP-IDF v5.4 commit `67c1de1eebe095d554d281952fde63c16ee2dca0`:

The exact final binary sizes, hashes, generated configurations and source fingerprints are maintained only in [`firmware/runtime_idf/compile_report.json`](../../firmware/runtime_idf/compile_report.json). Rebuilds after safety fixes supersede earlier hashes; this document intentionally does not duplicate those changing values.

The enabled generated SDK configuration has `SECURE_SIGNED_ON_UPDATE=y`, `PEN_OTA_ALLOW_INSTALL=y`, `BOOTLOADER_APP_ROLLBACK_ENABLE=y` and equal project/hardware `smartpen_runtime_compile`. Hardware anti-rollback and automatic binary signing are disabled. Official esptool image-info reports project `smartpen_runtime_compile`, app version `1`, secure version `0`, confirming the software version field no longer depends on eFuse anti-rollback.

This is an **unsigned compile artifact**, intentionally awaiting external signing and never installed. No signing key was generated or used, no hardware Secure Boot was enabled, no eFuse was burned. `app_main` only reports disabled integration and returns; retaining component symbols in the linked ELF checks actual SDK API compatibility without exercising hardware. Exact toolchain/build commands are in [SDK build record](sdk_build_20261028.md). Host policy/adapter tests also passed ASan+UBSan with leak detection disabled; no leak-test result is claimed.
