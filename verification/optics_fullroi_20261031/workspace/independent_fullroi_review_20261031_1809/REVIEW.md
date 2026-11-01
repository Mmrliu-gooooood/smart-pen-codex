# Independent isolated full-ROI refinement review

Scope: standalone default-off candidate; no active source/integration, provider, hardware, public write or physical/FPS qualification. Author source copied into independent directory solely for recompilation and tests; original active/archive source remains read-only. This review is not approval of whole V3 crop semantics or general perspective decoding.

## Source/standards axis

No blocking wrapper defect found in reviewed source. Candidate includes V3 ABI headers and separately compiles active/V3 entry-point symbols; shared original structs match. Active and V3 detect() bodies are byte-identical. OFF calls exact active cold with prior NULL. ON passes full original image dimensions/stride to refined_transform, without crop, evidence filtering, oracle priors or active-accept short circuit. Thus full bounded consensus and seed overflow remain authoritative. Declared caller-owned arena is nonreentrant, not inferred embedded task stack.

Overlap and uintptr range-wrap checks precede all writes, including diagnostics reset; diagnostics may reset for nonoverlap argument failures while result is unchanged. Seed overflow is tested before next seed write and returns AMBIGUOUS. At cap64 native workspace23424B/result68B; cap1 workspace21912B. Neither is V3 wrapper32640B nor an assumption that active21888B suffices.

Minor Python test entrypoint issue identified before author freeze: unittest.main preceded AliasTests and direct execution skipped that class. Discovery/native tests already covered aliases. Final disposition recorded below.

## Independent native execution

Six configurations rerun: OFF/cap64, ON/cap64, ON/cap1 each ordinary and ASan+UBSan. All pass, stderr empty. Native input/result/workspace guards, input immutability, failure result preservation, overlap and range-overflow checks actually execute. Constructed overflow image produces65 seeds for cap64 and2 for cap1, rejects with zero refinement iterations/models. LSan explicitly disabled; no general memory-safety proof or target SDK qualification follows.

Separate omitted-macro build confirms header's true default OFF rather than only a build script explicitly setting0. A new independent full-region test takes frozen001 positive and adds a6px dark edge stroke outside central96: both OFF/ON accept original and reject modified full200 input with DETECTION, keeping failure output and input unchanged. This corroborates source-level full-region preservation; no author fixture was changed.

## Regression/oracle interpretation

478 inputs comprise same70 frozen synthetic PGMs and340+68 old generated images. The new fullROI experiment must not be presented as archived crop V3 reproducing254 accepts. Dense continuous frames are rejected under unchanged full-input128-component/strict-edge quality boundary; retaining those limits is intentional for this narrow quantization seam.

The regression checks correct coordinates/symbols for the probe and exact symbols plus full-frame conservative dot-square support and must_reject for historical images. It does NOT supply transforms or assert old transform-error oracle, explicitly because this interface has no transform output. The stronger boundary support check does not make other historical oracle dimensions equivalent. All prior required rejections must remain rejected independently of aggregate accuracy.

## Acceptance decision gate

Only isolated defaultOFF software-research continuation may be supported after all final source hashes, OFF equality, ON expected recoveries, target positives/offset-boundary rejections, negative fixtures and frozen results independently verify. No production adoption, camera/lens/paper freeze, physical-tip/IR, real-time/FPS or GAP interpolation follows.

## Final result / decision

Frozen author44-file MANIFEST SHA256 `3c32b7b5533673e36c757f721b962fc8d1c5b5596f8ce7b430af6eb2f412592b` verified with zero mismatches; copied candidate/build/harness files match final bytes. OFF and ON independently execute all478 each, exit0, all per-case semantic outputs equal to author run excluding host duration. OFF23 correct/0 invalid/455 reject, ON32/0/446. Transitions23 retained correct,9 recovered,446 retained rejects,0 lost. All50 explicit must_reject and all154 historical rejects stay rejected. Eight target positives pass and three offset-boundary negatives reject. Same70 probe improves22 to31 correct,0 wrong,48 to39 reject; both340 continuous sets wholly reject and each68 adversarial set has only one consistent-double-window accept. This is deliberately not continuous-paper qualification.

Unittest entrypoint moved last before final freeze; copied final test file direct run independently passes all3. No decoder source change involved. Author README initially blurred oracle scope: probe branch scores x/y+36symbols, with support=None; historical408 branch scores symbols+full-dot-square support+must_reject (no transform-error check). Successor `orthogonal_refine_fullroi_erratum_20261031_1812/ERRATUM.md` correctly narrows this; frozen artifacts unchanged. Independent EXTRA post-return projected bounding-square oracle checks all53 accepted probe outputs across OFF22+ON31: all fit full200 ROI, minimum margin8.983333333333348px. This is new reviewer evidence, not retroactively attributed to author regression.

**No blocking issue for retaining this defaultOFF isolated research candidate.** Not approval to activate production, replace V3 crop behavior, relax quality thresholds, buy hardware or assert physical/IR/FPS capability. Further integration requires its own scope and review. Original source checkout remains clean; no user raw photos/PDF accessed. Independent evidence frozen here after completing final checks.
