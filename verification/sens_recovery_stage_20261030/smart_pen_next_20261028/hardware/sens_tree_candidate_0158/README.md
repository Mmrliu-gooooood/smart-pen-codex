# SENS external reference tree — native research candidate

**NOFAB / NOPOWER.** Actual native full DRC **0 violations /143 unconnected /0 schematic parity, exit5**. This does not finish the pen or establish camera/back-power safety.

Base `7c81674ef29dc3e176055a823adacd5ef9847b8becd40fef520f832377dc909c`; candidate `ca66f962b84eb96367d52a6b6fc400617c9706bfe666cf964638956cd57f4c5a`.

## Exact native change

Instantiate the frozen `docs/electronics/sens_joint_plan_0155` end-around tree exactly: **37 new SENS objects =30 tracks0.25mm +7 through-vias0.60/0.30mm**. All736 prior copper objects, all102 footprints/366 physical pads, source, board outline, zone definitions, stackup, rules, J103/J106 and JP301 OPEN are unchanged. Total773 copper objects. No thin-feed rescue, regulator, AON short, altered signal, moved pad or removed original object.

The In3 tree goes around the left end of the D7 transverse group, with two explicit short doglegs around existing HREF and GND vias. It retains the full existing DVP and low-speed routes instead of temporarily releasing them. Actual native plot `native_tree.png` was inspected.

## Actual tests

- Full CLI, bound same-basename project/rules: `--all-track-errors --schematic-parity --severity-all --exit-code-violations`; **0/143/0**.143 remaining items prohibit completion claims.
- Finite physical connectivity: **SENS J202.23 core1→12/12** (four translator groups, four bypass caps and two pullups); AON **23→23/39**, GND **57→57/102**. All prior same-net source-pad components are preserved, not only the newly routed net.
- Existing12 DVP links/19 source-net connectivity preserved by the stronger all-prior-components comparison. No old signal object changed.
- Explicit physical copper intersections: SENS versus AON/GND/CAM switched supply **none**, including actual filled-plane units. This is not an electrical back-power test.
- All7 new through-via disks checked against every physical pad on every actual copper layer, including same net: **no overlap**. This does not establish solder-mask registration or manufacturing tolerance.
- Source/rules exact bytes; stripped noncopper/zone-definition native text exact. No altered source or hidden footprint change.
- Normal and optimized verification results identical. Fresh-fill/save/reload/refill idempotent. Exact script replay returns same candidate SHA.
- Remove37 new objects, rebuild connectivity/freshfill: **exact parent7c816 SHA and0/149/0**. Two actual native deletion+refill+fullCLI negatives (source via, C202 via) each produce **2/144/0**, exit5. No hypothetical negative substituted for native result.
- Guarded raw-native Unfracture return check: main GND each loses4.488771064mm²; small GND each0.045242728mm²; AON4.442572168mm². Each normalized0.25mm-eroded outline remains one component; no additional old signal reference projection loss above1e-8mm². These are actual post-fill measures, distinct from the earlier approximate planning losses; they do not qualify current/EMI/transient behavior.

## External source and unresolved gates

`SENS_VIO_1V8` remains supplied only by the external head reference at J202.23, whose connector symbol is passive. There is **no on-board1.8V source**. The physical12-pad tree is connected; this is not confirmation the external reference can supply these loads, sequence safely, or withstand back-power. AXC VCCB versus TCA VCCA domain naming remains as source. Unknown camera must not be connected/powered.

Main MCU analog supplies, other grounds/signals and actual board completion remain pending. Earlier MCU eight in-pad vias and23.8µm nominal EP hole-edge margin remain unchanged unresolved manufacturing risks. Caps/assembly, external source capacity, voltage ramp, power-off behavior, battery/charging and whole-product tests remain unqualified. No GitHub push, fabrication, powered test, flashing or radio action in this task.
