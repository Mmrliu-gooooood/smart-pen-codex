# MCU local supply/ground successor: independent limited review

**NOFAB. No power-up or manufacturing approval.** Formal accepted 9a03 baseline is not replaced.

Reviewed native PCB `77537f15c2beff27ec3098c0ccd9d3dd5cd10ac335b74c4909954f2fedcf4a24`, author manifest `b60e4be8abb820cff7e2e61f23cda937ddc4c1d2afb14ab144ead38c5d93496e`. All 108 author files and 10 declared dependencies were checked before and after review, without edits to original artifacts.

## Verified bounded outcome

- Fresh KiCad 9.0.2 DRC with bound same-basename project/rules, `--all-track-errors --schematic-parity --severity-all --exit-code-violations`: **0 violations / 181 unconnected / 0 parity, exit 5**. The exit is not a pass for a complete PCB.
- Independent finite-copper graph uses actual `IsOnLayer` membership, physical pad UUIDs, 100 nm polygon approximation and 512-edge drill subtraction. It confirms **AON 14/39** and **GND 39/102** physical pads at source core. Nine distinct U101.57 EP islands are connected. C504.2 is correctly NOT core-connected in this successor.
- Eight full AON-group graph deletions disconnect the respective terminals. Deleting all nine EP vias disconnects all nine EP terminals. Normal and `python -O` outputs are byte-identical.
- Independent object-signature comparison confirms all 630 prior copper objects unchanged, exactly 51 new objects, ten supply segments widened to 0.254 mm, and only the prescribed source-via relocation plus new 0.5 mm ground segment. Same source schematic, project and rules remain. Author source/non-copper verifier was reproduced separately in an isolated copy, preserving 102 footprints, 366 physical pads and non-copper native data.
- All prior pad components, including the existing twelve DVP chains and nineteen restored nets, remain connected in the reproduced all-net finite-copper check. This is static continuity, not signal timing or power integrity.
- Exact materialization replay reproduces the native SHA. A real saved/reloaded native deletion of all 51 added objects followed by fresh fill returns exact ead39 SHA and **0/203/0**. Reverting the relocated via and deleting its ground bridge returns exact rejected `732ba1b…` SHA and **0/180/0**.

## Why lower unconnected count was not safer

The rejected original EP via at (4.5,10) drills into the B-side C504.2 ground pad. Same-net native DRC reports zero violation and an apparently improved unconnected count, but this is an unintended mechanical/manufacturing overlap. Independent all-layer pad screening checks copper ring and drill separately against **every actual pad, including same-net pads**. It reproduces the rejected C504.2 drill overlap. The successor's nine vias have no non-EP pad overlap in that screen.

The relocated via at (4.25,10.75), unchanged 0.60/0.30 mm size, has a nominal 0.225 mm full-disk clearance from the retained 2.45 × 0.95 mm C504 pad-union XY envelope. The native F/B comparison image was inspected; the old and new hole positions and retained envelope match the described geometry.

**Not resolved by this screen:** only 23.8 µm nominal drill-to-top-EP copper-edge margin remains, and the other eight vias are still in EP solder lands. The process needs actual drill/mask registration, via treatment, stencil/paste, solder wicking/voiding, assembly inspection and thermal guidance. No filled/capped process, extra cost or vendor acceptance is assumed. A 0-violation DRC does not close this gate. C504 return and other required supply/ground branches remain unfinished.

## Filled copper and source-guide limits

The author's plane/projection checks were reproduced on fresh native geometry in normal and optimized modes, using the required guarded **one-time raw-fractured** conversion. This is not a claim that Unfracture can be called on arbitrary polygons; repeated conversion of canonical hole geometry is unsafe, as the mandatory earlier errata establish. The reproduced differences are approximately 6.417850085 mm² removed per main GND plane and 5.743167145 mm² removed from AON. Current old-signal nearest-reference projection comparison reports no additional uncovered area. These are geometric evidence, not impedance, transient droop, minimum load-path width or current/temperature qualification.

Supply-width source assessment remains separately bounded: the short 0.254 mm fanout follows general ESP32-S3 guidance conservatively. PICO pin 46 is CPU IO supply; an overall 500 mA supply recommendation is not a per-pad domain current rating. The main missing power/ground network cannot be qualified by small calculated DC loss in a short local branch.

## Reproduction and artifact contract

The report manifest contains the independent script/results, isolated author-test results, fresh DRC, native-counterfactual DRC and integrity/replay evidence. Copied native boards and copied author support scripts are not duplicated in this review's publication payload. Reconstruct the local review execution directory by copying `native/`, `verify.py`, `finite_copper.py`, `native_polygon.py`, `clearance.py`, `materialization.json`, `drc.json`, `native_counterfactual.py`, `materialize.py`, and `noncopper.py` from the hash-bound author candidate. Retain the author's ten exact dependency paths in the same repository root. The review directory is at `hardware/<review-name>` so existing relative root resolution remains valid. Run independent.py normally and with `-O`; author reproduction and native negative logs identify their separate scope. Do not run reproduction in the immutable author directory.

The standalone independent script does not itself rerun official source research or certify fabrication. It verifies the described static subset. **Remaining 181 unconnected items, unfinished rails/returns and manufacturing gates prohibit board release or energizing.**
