# Independent SENS reference-tree review

**NOFAB / NOPOWER. Formal accepted 9a03 is not replaced. Whole pen and power system are not complete.**

Reviewed immutable author `hardware/sens_tree_candidate_0158`, 95-file manifest SHA `622421ef5e01440939c14a38a97fedec0547f6961ef46e7f1a6c99e658a689a7`; candidate PCB `ca66f962b84eb96367d52a6b6fc400617c9706bfe666cf964638956cd57f4c5a`. Read-only plan 19-file manifest `7a5b6998ebab84371df7011dcf41e4e4d35b43f13526a6f189abe6842374dcf6`. All manifest and declared dependency hashes passed before/after; original files were not edited.

## Results

- Fresh KiCad 9.0.2 full CLI, actual bound source/project/rules, all-track-errors + schematic-parity + severity-all: **0 violations / 143 unconnected / 0 parity; exit 5**. Not a board-completion pass.
- Independent physical-UUID finite-copper graph, actual copper layers, finite track/via/pad shapes with via drill removed: **SENS 12/12; AON 23/39; GND 57/102**. All 9 existing local bypass relationships remain closed.
- Exact 12 SENS physical pad names: C202.1, C204.1, C206.1, C208.1, J202.23, R242.2, R243.2, U201.23, U201.24, U202.16, U203.16, U204.1. Actual R242.1=SENS_SCL, R243.1=SENS_SDA; both .2=SENS_VIO_1V8. My initial assumed .1 expectation failed; preserved `REJECTED_assumed_pullup_pad1.log`, corrected by actual PCB and embedded source, not by modifying hardware.
- Actual embedded library confirms AXC VCCA=AON / VCCB=SENS, opposite TCA VCCB=AON / VCCA=SENS. J202.23 is a passive connector pin, not an on-board regulator. PCB PAD pin-function strings are not used as source proof.
- All 736 old copper objects and 102 footprint identities/poses retained; 37 added objects (30 tracks 0.25 mm, 7 vias 0.60/0.30 mm), total 773. No source, rules, outline, zone definitions, pad or footprint text changes. Exact plan replay reproduces candidate SHA, including fresh-fill stability.
- Independent actual copper SENS intersections with AON, GND and CAM_3V3_SW: none on all actual layers. This is not leakage/back-power/sequence qualification.
- All 7 new via annuli AND drill disks checked against every actual physical pad/layer, including same-net: no intersections. Controlled same-net drill intrusion into C202.1 is detected (0.070684094104 mm²). Nominal geometrical clearance alone is not manufacturing tolerance qualification.
- Reproduced author all-prior-physical-pad-component comparison (including prior DVP and control networks), guarded raw-native one-shot Unfracture, plane erosion and signal projection: no prior component loss and no additional old-signal projection loss above model threshold 1e-8 mm². Main GND removal 4.488771064 mm² each; small GND 0.045242728 mm² each; AON 4.442572168 mm². Each normalized 0.25 mm eroded outline remains one component. This is finite geometry, not current/EMI/transient proof; never raw fractured erosion or repeated Unfracture.
- Independent graph and reproduced author checks normal/-O are byte-identical.

## Native adversarial tests

Actual remove-all-37, rebuild connectivity and refill returns exact parent `7c81674ef29dc3e176055a823adacd5ef9847b8becd40fef520f832377dc909c`, full **0/149/0**, exit 5. In-memory graph deletion independently isolates J202.23.

Actual source via deletion `1ba49ad4-6eae-515d-aad4-1eb40505061b` and C202 access via deletion `c829effe-d63d-5689-8aa7-40befde07fc3`, each freshly filled and run through full CLI, each **2/144/0**, exit 5. No hypothetical native result substituted. Actual author plot `native_tree.png` visually inspected.

## Unresolved gates

External reference sourcing capacity, load/startup demand, sequence, voltage ramp, power-off/back-power behavior and camera identity remain unqualified. A connected SENS tree does not establish a usable safe 1.8 V supply. Unknown camera must not be connected/powered. MCU other supplies/grounds and 143 native unconnected items remain. Earlier 8 in-pad MCU EP holes plus 23.8 µm nominal EP drill-edge margin remain unresolved DFM risks. Actual capacitors, paste/mask/fill/registration, assembly costs and battery/charging/product tests are not qualified. JP301 remains OPEN. No fabrication, upload, power, procurement, flashing or radio operations performed.

## Reproduction / publication contract

Only `review_manifest.json` allowlisted files are review publication artifacts. Local copied support/native directories are deliberately excluded, not silently claimed to be backed up. To reproduce, place this review at `hardware/<review-name>` under the same repo root and copy from the immutable 95-file author package: `native/`, `verify.py`, `finite_copper.py`, `native_polygon.py`, `materialization.json`, `drc.json`, `counterfactual.py`, `native_negative.py`, `materialize.py`, `noncopper.py`, `domain_isolation.py`; retain declared dependency paths. Use /usr/bin/python3 (pcbnew); execute independent.py normal/-O, verify.py normal/-O, counterfactual.py, native_negative.py source_access_via and C202_access_via, noncopper.py. Run materialize.py with SENS_NATIVE_OUTPUT=<review>/replay/native. Fresh CLI command is recorded in this report above; copied same-basename project/rules must remain bound.
