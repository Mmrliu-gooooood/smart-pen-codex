# Local publication package R4 — 2026-10-28

This package is staged locally only. It does not establish a GitHub upload, manufacturing release, charging approval, or a complete working pen. **All hardware remains NOFAB.**

## Start here and upload in small batches

1. Application: 51 manifest-locked files, approximately 148 KB. The final 8 MiB profile documentation is a separate 9-file supplement plus its original manifest (SHA256 43e6b70eb45c529e062e67aa9269fa8ef8d2c513417b028228e3f54ad6e9b8c7), mapped into the original repo-relative document paths; its manifest is retained at verification/profile8_20261028/DOC_MANIFEST.json. The standalone independent review contributes13 evidence files plus its own manifest (approximately72KB). The review binds final source manifest99ff5c16… and reports83 full host tests with0 skips plus independent negative tests and three target builds. Real camera, GPIO, BLE and pose providers are still absent/default NULL. The enabled SDK build is not a deployable whole-pen demonstration. Flash profiles do not prove endurance, write lifetime or actual physical flash capacity.
2. Selected board core: `publication_manifest_selected_board_native_first.json` contains the current native PCB, schematic, local libraries and status README. It is only a first upload subset; the full131-file selected-board batch carries the original130-file manifest plus manifest itself.
3. Interface placement core: `publication_manifest_interface_native_first.json` contains only the authoritative native design and libraries/status, not `initial_refilled` exploratory boards. The full63-file batch preserves all62 original manifest entries as historical evidence. Never fabricate `initial_refilled` as a selected result.
4. Complete review, dependencies, v4 ownership/source, routing plan, harness and conditional mechanical evidence remain separate batches. Full native review snapshots and historical sources account for most package size. They are not additive BOMs or separate finished pens.

## Do not merge different progress claims

- The selected stepped14mm PCB is bound to SHA016d963f764430b6122da29039a5573792e3f0c78078180b18582af69b044c7e. Its selected-source check has0 geometry/0 unconnected/4 missing footprints; ERC has1 cross-board VBUS warning. Complete-master parity still has14 missing footprints. This is not a complete physical interface implementation.
- The84-footprint `physical_interface_placement_candidate` is a subsequent native prelayout bound to v4 ownership. It still has37 unconnected items. Do not reuse the selected016d routing result as proof that this newer placement is connected.
- `selected14_independent_review` contains review snapshots, reference masters and negative-test scripts/results. Its original whitelist excludes corrupt `guard_boards/`; they are not delivered. Anything in this review directory is evidence/test material, not manufacturing output.
- Current mode harness is `mainboard_integration_harness_revB`, bound to the actual016d board and power single-feed RevB94ced2bd…. It does not authorize commissioning or remove the need for physical strain relief/ESD/assembly verification.
- The mechanical016d screen binds79 actual extracted entities and the exact mixed capacitor placement. Its conditional19mm screen retains only about0.01237mm beyond its own0.10mm threshold. It is not proof of the requested15–18mm grip envelope. The84FP interface report has separate full-harness blockers. Neither result qualifies the real13mm camera or a future8mm camera interchangeably.
- Exact resistor and stackup studies are conditional specifications and source evidence, not supplier approval, quotation or RF qualification.

## Dependencies and reproducibility

Original bytes and manifest names are preserved. `verified_source_manifests.json` records each origin manifest and verified SHA. Each upload batch lists path, Git blob SHA, SHA256, size and binary flag. Native-first batches deliberately overlap their later full evidence batch; do not treat overlap as different revisions.

The application review is mapped into `verification/application_pipeline_independent_20261028`. Its supplied scripts support `PEN_REVIEW_SOURCE` and `PEN_REVIEW_OUTPUT`: set the former to the repository root and the latter to a new scratch directory. Their old default sibling path is not valid at the new destination. No binary build artifacts are uploaded; reproduce SDK builds using the exact documented SDK/toolchain and do not interpret retained hash metadata as a flashed device.

Selected-board review dependencies include frozen v3 allocation and the RF conditional baseline. They are provided in a separate dependency batch. The latest power RevB sources and their earlier prerequisites remain in `verified_revisions_r3`; publish the r3 power batch before rerunning exact-version harness tests. The earlier mechanical `flex_power_revD_study` and `flex_power_tolerance_supplement` are also r3 prerequisites for the six-layer thickness supplement. All prior-stage dependencies are historical provenance, not licenses to mix physical versions.

Some retained extraction scripts embed their historical cloud source paths; read their documented inputs or supply path options where supported. Staging preserves them rather than claiming every old generator is relocation-safe. There are no private manufacturer PDFs/photos, ELF/BIN/object/static-library binaries, caches, or moving gate-overlay/routing trials in this package. The stackup PNGs are public technical reference captures from the frozen research whitelist.
