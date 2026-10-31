# Independent review — disabled host adapter

## Result
Bounded acceptance: no blocking defect found against README's explicitly host-only synthetic adapter scope. NOT acceptance for active firmware integration, real producer ordering, camera qualification, physical mapping or hardware execution. Provider remains NULL; reviewed profile registry remains empty. No author artifact or active source was changed by this review.

## Evidence
- Candidate MANIFEST SHA256: 77393689a9afbede897e656984a25c27a7001489a23f6d94f996ccc1a90a9fff.
- 30 manifest file hashes, 224 external dependency hashes and 6 integration-delta manifest hashes verified: hash_check.log.
- Fresh run_tests.py: 12/12 normal/NDEBUG/ASan+UBSan configurations passed: suite.log. Leak detection explicitly disabled by original harness.
- Independent seeded 10,000 eight-event sequences with edge/idle ties, stable same-kind ordering, arbitrary arrival times, partial/equal-watermark drains and level checks: normal/NDEBUG/ASan+UBSan passed, 490005 explicit checks per mode: independent.log; run_independent.py reproduces. Original synthetic fixture imported unchanged. The renamed original main has a localized return-type warning suppression because C's implicit-return rule applies only to main; this is a harness adaptation, not a candidate defect.
- Adjacent recovery HEAD b261859addbecac79e4727449bb73da616fab549; git status --short clean. Candidate is a standalone non-Git artifact, so no merge-base diff exists.

## Spec axis
Queue admission and stable insertion (src/adapter.c:18–25), cutoff drain/sealing (:33–52), equal-time edge/frame/idle ordering, original capture timestamp preservation, mandatory terminal notification and cleanup (:12–16), callback/reinit protection (:3–9,36–52), synthetic-only lease acceptance (:55–62), exact-pointer live ROI binding (:64–70), and default gate OFF conform to the documented bounded candidate contract. Reviewed both unchanged capture ownership/ROI helpers and all four tests. Original suites exercise frame-before-edge arrival, held-frame overflow, invalid/stolen leases, source/frame/time mismatches, two ROI origins, reentry, sink/cleanup failures, NULL provider and no VALID coordinates through actual application modules.

The larger INTEGRATION_DELTA is not fully implemented. Producer watermark certification, event acquisition/initial levels, source boot continuity, capture error scheduling, real immutable mapper/calibration policy, asynchronous storage/BLE/sleep guards, repeated wake and hardware remain explicit obligations rather than hidden software completion. In particular the pipeline test calls the rejecting mapper manually; it does not prove calibrated mapper execution through a qualified pipeline. A fault sink must actually stop/surface consumer failure. A fabricated producer watermark cannot be detected by this adapter. These are already disclosed, not newly discovered defects.

## Standards axis (separate isolated reviewer)
No blocking architectural/lifecycle finding. Header contains declaration-local allocation, ownership, callback and watermark contracts; centralized admission/cleanup and synchronous dispatch remain cohesive. Explicit CHECKs survive NDEBUG. No AGENTS.md/CODING_STANDARDS.md/CONTRIBUTING.md found through workspace depth 3; reviewed against documented API and architecture baseline, not an unavailable project standard. Separate reviewer read source/header/tests but did not execute tests or hash checks; those were performed here.

## Physical boundary
NOPOWER/NOFAB; no SDK rebuild, external writes, device actions or purchases. User-reported OV5640 visible black-dot baseline is not SC031GS qualification or evidence of IR operation. No original OV5640 sample was analyzed. XCLK is not measured PCLK/fps; software ROI is not a sensor mode/FOV. No active provider or hardware release approval follows from this report.
