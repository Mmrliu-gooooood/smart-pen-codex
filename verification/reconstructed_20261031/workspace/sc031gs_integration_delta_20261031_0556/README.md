# SC031GS missing integration delta — 2026-10-31

Status: REVIEW CONTRACT ONLY. NOFAB / NOPOWER. No active source, GPIO map, PCB, provider, profile or power hardware changed. No external writes, contact, purchase, download of private material or device operations. User's unanswered capture-setup question remains pending; no additional question sent.

## Corrected starting point
The repo already archives an independently reviewed SC031GS capture v2. Do not rebuild a naive wrapper from upstream or discard its fixes. Its candidate README's historical “review pending” is superseded by sibling `smart_pen_camera_v2_independent_review_20261029_1824/REVIEW.zh-CN.md` and stage README. This is accepted bounded software evidence, not active product integration.

Pinned upstream: espressif/esp32-camera `f37e65608f709bd94846dee01d947f02ae07c0b0`; SDK `67c1de1eebe095d554d281952fde63c16ee2dca0` (IDF5.4). Local third_party tree is PATCHED, not pristine upstream: retain `verification/esp32-camera.patch` and source manifest. Pin is inherited from archived provenance; this audit did not independently fetch/reconstruct the entire upstream tree. Public official URLs in SOURCE_EVIDENCE.json reference immutable commit paths.

Active `firmware/application_idf/main/CMakeLists.txt` links board_provider_absent.c, pipeline, existing ROI and storage, not pen_capture. Active provider returns NULL. Archived capture profile registry also returns NULL for all names; standalone app_main does not initialize hardware even in enabled-compile builds. Thus “no camera implementation” is too broad; “no qualified camera profile or integrated operational provider” is accurate.

## Fresh checks
`source_manifest_check.log`: 192 source members matched the archived manifest.
`host_replay.log`: existing eight host test groups passed freshly with ASan/UBSan (leak detection disabled as authored); hardware/SDK dependencies are mocked where labeled. No SDK rebuild or real camera execution was attempted. All original test writes are temporary files. Source hashes and source guards captured in SOURCE_EVIDENCE.json. This does not re-run every independent reviewer test.

## Next implementation review
Read INTEGRATION_DELTA.md and MODULE_LENS_UNKNOWNS.md. Implement only a separate, disabled host adapter candidate first. Keep production provider NULL and profile allowlist empty. A future merge, physical profile, remap, power operation or purchase requires its own scope/evidence; none follows from this document.

Runtime 4h/1000h is soft; offline24h is cost-prioritized starting target; camera selection delegated and replacement permitted; visible dots precede IR. Lab/SMT inquiry already pending. Historical5µm metrology is not a mandatory equipment requirement.
