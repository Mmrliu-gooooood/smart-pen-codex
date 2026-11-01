# Independent review — frozen optics/paper screen

Reviewed snapshot: `optics_paper_screen_20261031_1752`, MANIFEST SHA256 `42fa3e57cc9f9750a8d1daa4383974869ef9577d6581b8055ed7a66584990396`. All 116 listed entries verified before/after work. Author artifact and active code unchanged. Review is a standalone artifact review; branch-diff gate is inapplicable. Spec basis is explicit parent request and corrected variable paper/pitch/FOV/near-tip/IR constraints, not approval of historical hardware assumptions.

## Reproduced evidence

- Fourteen Python tests pass normal and optimized. Full 7,200-combination sweep CSV, summary JSON and 256/96/80 crop summary reproduce byte-for-byte in independent directory.
- Geometry classification totals: 551 retained-not-qualified, 829 proxy-risk, 5,637 screened out, 183 invalid-depth; these are NOT decoder success rates.
- Newly compiled native active C executed on regenerated identical frozen pixels: 52 primary cases = 11 correct / 0 wrong / 41 reject; 18 affine controls = 11 correct / 0 wrong / 7 reject. Combined 70 = 22 / 0 / 48. Every per-case result is equal excluding nondeterministic host duration. Every PGM is byte-identical.
- Checked projection derivation and triangular Jacobian analytically; 1,000 central finite-difference checks max scaled discrepancy 2.9673e-10. D is optical-axis depth, not normal height; f is pixels, not real lens EFL. Displacement/radius enclosure and singular-value dot minor/blur calculations agree with declared local ideal-pinhole model. Sampled extrema and blur remain engineering proxies; no global lens/motion/occlusion qualification.
- Reviewed actual generated image contact sheet (8 selected cases) after conversion from frozen PGM: clean finite dot patterns, not user captures. No visual claim of optical qualification.
- C receives image pixels, dimensions/stride, paper dimensions and encoded section; neither pose nor true x/y nor renderer centers are passed. Frozen Python encoder directions drive rendering; C sequence lookup derives coordinates from detected directions. One-codeword coverage and shared code-family constraints remain limitations, not answer leakage.
- Standards reviewer independently verified all source hashes against disk and historical f92911bc. Local ca8cf993/public f92911bc lineage intentionally shares reviewed tree per parent publication receipt; not a source mismatch.

## Standards axis

No blocking standards defect. Minor duplicated metadata: `decoder_probe/controls_active.py:47` carries empty `tilt_offset` subgroup summaries and variable offset wording into fixed-offset affine controls (`:19` sets 1/6). Preserve frozen run evidence; publish successor erratum/metadata correction stating fixed displacement .05 mm under the declared .3 mm mapping and meaningful affine ratio groupings. Separate standards evidence is in sibling `optics_screen_standards_review_20261031_1759`.

## Spec axis

No blocking violation of this bounded screening spec identified. The reports distinguish geometric support/proxy gates from actual C execution and do not freeze final geometry from OV5640 overhead sample. All 36 tested nonzero-tilt projective cases reject, but affine cos15/cos30 controls also reject; therefore perspective alone is not established as the cause and no universal angle bound follows. Existing V3 replay on exact frozen 70 images, with real conditional 96/80 crop policy, is justified before new perspective implementation. V4 remains NOT_ADOPTED because its prior three quality-invalid acceptances are unresolved. No false-accept probability can be inferred from this finite single-codeword set. Preserve GAP on rejection; do not interpolate through unqualified measurements.

No user raw image/PDF accessed. No public writes, hardware, SDK/sanitizer or MCU timing work executed. Reproduction uses source-pinned author harness copies with output/source paths relocated only; independent verification scripts and logs are retained here.
