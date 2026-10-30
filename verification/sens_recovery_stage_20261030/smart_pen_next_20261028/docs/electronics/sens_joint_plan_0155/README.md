# One joint SENS tree model — read-only, NOFAB

Base `7c81674ef29dc3e176055a823adacd5ef9847b8becd40fef520f832377dc909c` is unchanged. No native copper is added by these scripts. This single end-around topology has **37 proposed objects:30 tracks of0.25mm and7 through-vias0.60/0.30mm**. No components, source net identity, old copper or footprint move/delete. The actual12 SENS pads form one finite-copper component. Deleting the source-access via or first cap-access via breaks it in `negative.json`.

## Attribution of the prior B blockers

- B10: J202.17/18 fixed physical pads, not disposable signal routes. Keep footprints and move proposed source transition to(3.5,91.4).
- B13: CAM_CT/CAM_ON low-speed control vias, retained. Lower SENS tree passes their left side rather than moving control nets.
- B16: newly routed EXTCLK transverse signal. Retained complete; new SENS upper tree stays In3 instead of crossing the B segment.
- B17: HREF/VSYNC/PCLK new signal transverse routes, AON supply via, and fixed J104 signal/GND pads. None may be released as a shortcut. All retained, SENS changes layer/topological route instead.
- B18: fixed R206 GND/R227 D3 pads. No FP movement; upper SENS passes In3, then goes around the left endpoint of the D7 In3 transverse group rather than crossing them.
- B23: existing CAM_3V3_SW main supply copper. No narrowing or relocation. Use the previously clear access via(11.05,75.15).

The first29-object proposal retained two clearance failures: HREF via(5.025,50.9) and GND via(7.6,74.0). `plan.first.json`/`first.log` preserve that rejected intermediate model. The final **same topology** adds two deterministic short doglegs around those exact disks; no sweep/search or original-signal deletion. All37 objects pass the combined0.15mm foreign-copper,0.25mm edge/hole separation, actual layer keepout, and **all-layer including same-net pad versus new via** checker.

## Evidence and boundaries

`plan.json` has exact candidate coordinates, whole/per-object checks and every old source-pad component. No old objects are removed, so all existing12 DVP links and19 source nets retain their finite-pad continuity in this unfilled model; native fresh fill can still affect plane connectivity and must be separately tested. Source netlist contains12 pads and no independent TP; J202.23 remains passive connector symbol with external-reference INPUT design role. No regulator and no AON bridge.

`evidence.json` has nominal return-risk subtraction only: main GND planes lose4.453529519mm² each, small planes0.043611883mm² each. Guarded raw-native Unfracture then0.25mm erosion remains one component; no old signal projection loss above the numerical threshold. **Not a real native refill or DRC result**; these are prospective hole-clearance effects, not power/EMI/thermal qualification. Candidate board creation, full freshfill/parity/DRC, source comparison, real copper core tests and replay remain mandatory before accepting it as a native research candidate.

External head voltage, reference current capacity, sequence/back-power and real camera remain unknown. NOFAB/NOPOWER. No publication or manufacturing.
