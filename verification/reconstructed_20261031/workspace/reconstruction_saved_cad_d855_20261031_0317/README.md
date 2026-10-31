# NEW saved d855 assembly derivative — research only

Four actual editable FreeCAD documents and four STEP files are newly saved from independently accepted saved f27 package `reconstruction_saved_cad_f27_20261031_0156`, manifest `16459c2cf811324a6e59658426d18297dc7aa3a7e4d335c233d7f47ebbc4ad66`. This is a NEW derivative, not restoration of missing historical receive CAD.

Current electrical identity: `d8550195b14521806a14654c4bdeba0a6d533b0aa536b473919481da2b9d6e5b`. Exact mechanical source package `reconstruction_receive_margin_mechanics_20261031_0305`, manifest `7b5941e25c88ecb1dfad76c88c43555a6a50f0a4d36fe22dd077976fe860c6d5`. Independent electrical review remains separate. PCLK/HREF four closures only; VSYNC is not closed.

## Actual saved changes
- R230 F(7.5,40.9)0° → F(11.1,34.25)90°.
- R219 B(7.5,41.5)0° → B(6.2,39.5)0°.
- Both full 2.45×.95×1.45 installation envelopes rigidly transformed, no shrinking or height waiver.
- NativeBinding current PCB, ParentSavedCAD/ParentSavedPCB and CurrentPoseDeltaJSON identify the new stage. Earlier recovered lineage and earlier R101/R503 PoseDeltaJSON are retained as history; current fields are explicitly separate.
- Board CurrentPCB_SHA256 updated; its geometric historical label remains unchanged. No board/support shift.

Every other saved shape retains bounds/volume. All 104 full entities, 97 static refs plus six operation/DNP refs =103 contracts, all original Status/uncertainty strings and six operation Evidence strings preserved. Exact native positions/angles/sides and reopened full104 bounds/heights independently audited. Board is 14×99.8 mm, .93 mm mechanical thickness budget, not a measured thickness; native .83 mm is recorded separately. Datum X=nativeX−7, Z=127−nativeY remains unchanged.

## Reproduction and gates
Run `/usr/bin/python3 native_pose_check.py`, `build.py`, `check_saved.py`, `audit_saved.py`. `build.py` and `check_saved.py` support `RECOVERY_CAD_OUTPUT=/tmp/unique_replay_directory` so replay need not overwrite delivered artifacts. Use `-O` for optimized replay. Native pose and audit normal/-O results match; independent optimized rebuild/contact results match normal JSON. All files are frozen after these checks.

Each saved FCStd is reopened and checked for exact labels, poses, bounds, volumes, current metadata, operation evidence, uncertainty Status and board dimensions. STEP files are reopened and valid, with solid counts RevC126, bench164, ACCESS19/20 each137. Exchange volume residuals respectively −.0000041884623, −.0000061167011, −.0012745226195, −.0010565259618 mm³. Absolute .005 mm³ comparison limit is a numerical exchange check, NOT manufacturing tolerance.

New-pose minimum clearance .675 mm R230/U201, next .9125 R230/C202. The support/contact checker preserves the corrected head .8 mm² contact, zero head penetration, lower/J202 .2 mm gap, ACCESS RF toe and tail toe contacts, .1 mm secondary catch gap, and three .5 mm² primary patches. All seven checked support parts remain valid single solids and clear all104 full bodies. RevC does not inherit an unsupported new support claim. Existing ACCESS19/C103 approximately .0679813 mm cover tolerance gate remains unresolved.

RevD_BENCH is an external bench fixture, not a pen enclosure. Operation gates J104/J108/JP201/JP202/C106/C107 remain open. These CADs model full assembly budgets, not detailed PCB copper; finite routing, C104 return, reference and loaded timing gates belong to the bound native reviews. No global assembly-access, strength, material, printing, manufacturing or electrical qualification.

NOFAB / NO POWER / no unqualified cell / two pens budget CNY760. No upload performed by this agent.
