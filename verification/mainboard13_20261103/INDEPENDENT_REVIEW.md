# a51a SCL candidate independent review

Candidate a51a57bcb5fa50ffd885deb988b045eac39d5e02cd94547f1060e3ece926edad versus f3ca95fff63985144ced0736e652093d2547b3df91f0493eda74dcffe4aba15e.

Supports conditional WIP only, not fabrication or power-on. SCL only joins U204 to R242; J202 remains disconnected. No claim of a complete camera interface.

## Executed evidence
- Fresh native DRC: zero violations, 13 unconnected. No native crash occurred in this replay.
- Replayed all 13 source checks in an isolated copy, both ordinary and optimized Python; see replay outputs and run log. This reuses reviewed source algorithms, not an independent second solver for all checks.
- Separately authored independent.py reads actual PCB vias and analytically recomputes every annulus-to-expanded moved-body rectangle gap. C208 minimum 0.100000 mm; U204 molded-body/flash 0.11298456 mm; R242 0.112500 mm. The earlier c9fa projection defect does not persist.
- Independent raw S-expression block comparison recorded all changes; 103 footprints and 238 vias retained in count. Three footprint blocks, three refilled zone blocks change; 10 old copper objects replaced/removed and 23 new objects. Verify script confirms only declared objects changed, all other poses and dependencies unchanged.
- Actual finite copper with drill holes removed preserves all ground terminal groups. The shifted ground annulus intersects the unchanged branch by approximately 0.090008 mm². Removing the shifted ground via isolates R221.2: negative case detects the actual bridge, not ideal-ground connectivity.
- Refilled-plane and physical drill checks run: 3960 retained reference projections have no new native-plane loss. Physical drilling adds 0.0188918014 mm² opening only at the connected GND branch endpoint. Do not call that full reference.
- 36 capacitor-terminal groups/projections and 12 fixed-window plane channels do not regress under the specified geometry method. Translator ground neck increases versus parent from approximately 2.53259 to 2.61597 mm.
- Replayed complete authoritative scene checks: original and expanded moved-body envelopes, maximum U204 mold/flash, and changed hole drill/annulus/expanded cylinders against fixed hardware pass. This is a replay of exact FreeCAD Boolean checks, not physical assembly testing.

## Limitations
New SCL hole and retained supply-hole reference apertures remain, including F/In1 0.065278740 mm², B/In4 0.064988163 mm² and B supply 0.136022720 mm²; inherited In3 supply gap also remains. These are disclosed geometric apertures, not SI/EMC qualification.

The +0.1 mm body projection and additional 0.1 mm gap are screening assumptions, not vendor process specifications. C208 sits at the nominal screening threshold. They cannot guarantee fabrication tolerance, solder-mask behavior, decoupling impedance, thermal/current performance or connector/fixture/FPC access. Camera/FPC physical scene, exact board thickness/process and complete device behavior remain unresolved. Existing design-rule clearances below the optional new-copper target are inherited, not upgraded to 0.2 mm.

Do not override the parent decision or call this production-ready. The finite checks support progression of a clearly labeled WIP only.
