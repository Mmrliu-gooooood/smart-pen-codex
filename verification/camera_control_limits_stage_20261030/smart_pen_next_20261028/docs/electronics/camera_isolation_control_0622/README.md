# Camera isolation complete control model / source audit

Research only, **NO FAB / NO POWER**. Parent actual native `imu_control_native_0522` PCB5ed5f0ad….

Read `SAFE_OFF_CONTRACT.md` first. The seven-gap OE/AON block is not the full MCU control graph: ten gaps total require CAM_IO_EN and IO_ENABLE_LINK, while JP201/JP202/JP301 stay OPEN. AXC OE and TCA EN have opposite polarity and opposite A/B rail naming. Exact source values/pin roles are checked by `source_contract.py`, including R20310k±1% and GPIO42 at U101 package48.

Old9a03 net copies fail current geometry; `old_reuse.json` retains concrete collisions. Only two coherent bounded topologies were explored:
1. OE tree first, MCU-to-JP201 last: last leg exhausted the bounded raster domain y≥2.5; no global impossibility claim.
2. MCU control first and existing RF-safe domain y≥0.5, then local link/OE tree: all nine signal branches plus R203 source branch finite-clear. Signals F/In3/B only, no In1/In4 long signal slots, source supply branch0.3mm with0.60/0.30via. No original copper removal, no footprint/source change.

`strategy2.json`387objects was compacted deterministically to `model.json`209objects, retaining all16via locations and same-net/pad contact anchors. Many short segments remain; this is not final elegant production layout. `verify_model.py` normal/-O agrees and rejects a known foreign-pad collision.

`strategy*.py` regenerate raster input binaries. Those ~440MB scratch inputs are intentionally excluded from this compact evidence package; C++ source/executable, result paths, exact final model, finite tests and logs remain. No binary raster is a source of truth for final native geometry.

Native materialization and independent-review boundary: `hardware/camera_isolation_control_native_0628`. All inherited power/clock/IMU/reference/assembly/unknown-camera/firmware gates apply.
