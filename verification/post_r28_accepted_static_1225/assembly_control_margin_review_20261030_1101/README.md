# Control-path repair: ≥0.2mm exploratory J104 margin — NOFAB / NO POWER

Exact native `hardware/control_envelope_native_1051/native/mainboard_revD.kicad_pcb` SHA256 **8312b1d5ec56f0ab4c396cba2b78449e191f06225bf9aa64ea6522fd1c3c68bb**. This replaces the control routing trial from accepted unused-bias2a540, not a patch silently applied to frozen1041. Earlier30f015 C206/J104 crossings and51ee .0119409mm near-miss remain separate historical findings, not accepted manufacturing options.

## Concrete nominal result

All **18 exterior tracks +2 through vias** have zero non-target full-installation-envelope, native Fab-bounding-body or native courtyard projection intersections. Explicit endpoint-target refs alone may have reported copper projection overlaps. No envelope shrink, zero-height wire exception, or same-net blanket waiver is used.

**J104 cached service rectangle** B x8.955..11.045,y51.755..57.845:
- RESETvia(11.475,54.75),Ø.45: **.205000mm** nominal gap.
- Closest RESET track(11.325,51.475)→(8.3,51.425),width.15: **.20958922617mm**.
- Thus the parent’s **≥.2mm exploratory geometric constraint is met**, unlike the51ee trial's.01194mm track gap. This is **not a supplier tolerance, actual fixture clearance, or physical probe qualification**. Only.005mm additional nominal headroom remains above the chosen.2 target at the via; do not advertise robust fabrication margin.

**C206 full retained installation budget** F x9.125..11.575,y58.3875..59.3375,height1.45:
- Minimum new-copper gap **.60913503104mm**, PWDNvia(11.85,57.6),Ø.45.
- Closest PWDN F track gap **.75913503104mm**.
- The rejected1041 underbody crossing is eliminated without changing C206 or its installation budget.

## Scope and exact invariants

Source hashes and author manifest-listed files are checked. Each stage’s103 complete footprint/pad contracts remain equal to8684: actual pad layers, positions, rotations, sizes/shapes/nets, footprint identity/value/DNP/pose. Edge.Cuts remain14×99.8mm with RF end−6.5 preserved. Reference zone outline/net/layer/rule-area definitions remain equal. Filled polygons and electrical dynamics are not mechanically certified; independent electrical/refill/reference review is separate.

`results.json` also reproduces prior distinct ground5track and unused14track+1via screens; final cumulative change from8684 is37 exterior tracks+3vias. No non-target body/courtyard projections arise in either prior stage. Unusedvia(9.1,47.025),Ø.45 retains.325mm to U202F/R206B full budgets. Full J202 motion budget and all other installed poses remain unchanged; no unrelated shell redesign is performed.

Method: native finite-width track/via polygons,50nm ERROR_OUTSIDE approximation, conservative per-footprint/Fab graphical bounds, native courtyards and full retained installation rectangles. `margins.py` independently computes exact analytic round-cap segment/disc distances to the specified C206/J104 rectangles; these are not rounded centreline-only estimates. U205/C209 provisional package budgets retained. J108 uses its prior mixed-side service interpretation, not fictitious fitted passive body. Four DNP refs and J104 full probe installation remain explicit unqualified operations;98 static modeled refs do not become103 manufacturing-qualified installations.

## Next actual assembly gate

The geometric crossing/margin remedy is complete at this bounded scope. Next is **the actual J104 service fixture/operation contract**: selected tip/shaft shape, repeatable board datum and total positioning/runout error, axial stroke and force, masking/tenting and adjacent copper, camera-isolated electrical procedure, and a preassembly/cassette-removed service stage. Prior true CAD tests show assembled normal access hits cassette hardware. Native courtyard clearance alone cannot qualify a probe or justify drilling unreviewed access holes. No physical test or power is performed here.

Connector/FPC seating/bend/insertion/tool, J103 strain relief/material/solder, finished-outline tolerance ensuring≤100mm, battery qualification,15–18mm pen target and two-penCNY760 cost remain open. **NOFAB / NO POWER.**

Reproduce in independent copy: `/usr/bin/python3 screen.py`, `/usr/bin/python3 -O screen.py`, `/usr/bin/python3 margins.py`. Verification/manifest bind results after source freeze.

### Checker reporting correction

The frozen1048 grouped checker correctly rejects outline changes before screening, but reuses its local `bounds` name for Fab graphics afterward; its serialized `outline` field therefore accidentally contains the last Fab bounds list. This successor uses a distinct `outline_bounds` variable and reruns all three exact stage guards, serializing **[0,−6.5,14,93.3]** correctly. No PCB or frozen1048 evidence was modified. This is a reporting-field correction, not a previously missed physical outline change.
