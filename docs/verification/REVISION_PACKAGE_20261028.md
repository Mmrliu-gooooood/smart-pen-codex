# Verified-revision publication package (2026-10-28)

**All hardware remains NOFAB. No charging, manufacturing, or measured-performance approval is implied.** This is immutable staging only; it has not been uploaded.

## Selected current design and historical evidence

- Current selected power candidate: `hardware/power14_single_feed_revB`. Its frozen manifest still says review pending, because historical bytes are preserved. The completed independent result is `docs/verification/power14_single_feed_revB_review_20261028/README.md`: finite-width single-feed geometry and 25 actual copper nets pass; dynamic safety remains open. Actual change is 26 deleted and 43 added copper objects, not merely three added segments.
- **Rejected power Rev A:** `hardware/power14_single_feed_candidate` is failure evidence ONLY. Its centerline model missed three finite-width copper contacts. Read `docs/verification/power14_single_feed_review_20261028/README.md`; do not select or fabricate Rev A.
- Mainboard HREF2 is only an incomplete connectivity candidate: ERC0, DRC exit5 with 2 unconnected, 33 dangling vias, 3 dangling tracks, and16 missing footprints. HREF3/BIAS4 and their reviews are historical dependencies, not alternative finished products. Power and return qualifications remain open.
- Mechanical studies are conditional envelope research. They distinguish the actual13mm camera from a hypothetical8mm head. Nominal18×213 collision checks do not close tolerance, FPC, missing components or assembly gates. The tolerance supplement does not select an approved diameter.
- The power architecture study permits deleting ZERO safety parts at this stage. Candidate simplifications require further design and qualification.

## Portable native review entrypoint

Run from a clone containing this staged tree:

    python tools/verify_native_candidates.py --output /absolute/path/to/new-review-directory

Requires Python3 and KiCad9 with official symbol/footprint libraries. On Linux the default KiCad share directory is `/usr/share/kicad`; supply `--kicad-share` elsewhere. The output directory must not already exist. The script creates explicit writable XDG config/cache/data and copies each source module to isolated output workspace. Source files and historical evidence are not rewritten.

The script verifies every candidate manifest file and the pinned PCB SHA256, runs fresh all-severity ERC and full DRC with schematic parity and `--exit-code-violations`, parses actual JSON findings, and records expected counts. Exit5 for `all` or `mainboard` intentionally preserves incomplete-hardware status even when the known defect count reproduces; exit1 is a tool/baseline mismatch. `--board power` can exit0 only for reproduced static checks, never a manufacturing release. No rules or exclusions are relaxed.

Fresh normal and `python -O` runs on staged files reproduced the expected reports; both combined runs exited5. Reusing the same output directory correctly exited1. Altered frozen source was rejected with exit1 in normal and optimized Python before native checks. Evidence is in `verification/native_candidates_20261028`.

## Dependency and portability boundary

- Included authoritative manifest whitelists and their hashes appear in `verified_source_manifests.json`. The power base and core are explicit dependency batches, not additive BOMs. BIAS4 native design, source libraries and guard files are selected explicitly; moving trial directories are excluded.
- Older XCLK5 review dependencies remain in the separately staged `remaining_hardware_r2` package. Publish that historical package as well if rerunning BIAS4-vs-XCLK5 historical comparisons.
- Historical scripts were not rewritten. Some retain cloud absolute paths (`bias4_recovery_review.../audit_native.py`, `recheck_guards.py`, historical mechanical extraction scripts); some archived generator paths assume their original study layout (`mainboard_href2_candidate/reproduction/transplant_research.py`, `grid_core.py`; inherited `tools/check_xclk_delta_return.py`). They are provenance, not the portable current-board review entrypoint. Relocation of every discarded experimental generator is not claimed.
- The portable entrypoint above works directly with the selected current native sources and does not depend on moving historical route experiments. It verifies ERC/DRC/parity, not every physical-graph or DC model audit. Those independent reports and scripts retain their documented scopes.
- One PDF in this package is a KiCad-generated project schematic. No private camera photographs, manufacturer PDFs, source archives, credentials, runtime caches or current routing trials were included.
