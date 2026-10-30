# MCU power/ground recovery index — 2026-10-30 01:25 UTC

**Read-only recovery map / NOFAB / NOPOWER.** This new document does not amend frozen manifests or implement any circuit. Independent review is pending. Formal accepted9a03 is not replaced. All numbers below concern local research layouts, not completed product status.

## Recovery sequence

1. `docs/electronics/MAINBOARD_RECOVERY_20261029_2315.md` and mandatory `MAINBOARD_RECOVERY_ADDENDUM_20261029_2327.md`: actual conservative `hardware/gnd_conservative_recovery_2305`, PCB **ead39fa832de2aabff4fbec9ce67d12199094ac9d77e700de54920d8fec86959**, full native **0 violations /203 unconnected /0 parity**, AON **1/39**, GND **30/102** physical pads reaching J106.2/.3. Preserve the 2327 guarded one-shot Unfracture correction; raw fractured polygon erosion counts are not physical connectivity proof. Never Unfracture an already hole-bearing Boolean result.
2. `docs/electronics/aon_branch_reuse_plan_2318`: eight whole AON groups, 41 original objects, geometry-screened proposal only at that stage. Not native restoration or power qualification.
3. `docs/electronics/mcu_supply_path_assessment_2338/REPORT.md`, manifest **70afb64621dee18443310ce00c270ab7d8ecd44a362927d99face8e508839350**: official PICO pin46 is CPU IO supply, not a 500mA-per-pin rating. Local routes and general S3 guidance cannot establish actual domain peak current, SiP applicability, load/thermal/transient safety. Source references and caveats are retained there.
4. `hardware/mcu_power_ground_candidate_0043`, manifest **6d0fabde970d9f25b3ca55da149985d88cceabd834dec9f0dcd98d1bbac0fa2a**: restored eight groups, ten local tracks widened to0.254mm, nine EP vias. **REJECTED** despite native **0/180/0**, AON14/39 and GND40/102. Original via(4.5,10) intersects bottom C504.2 pad/drill budget on the same GND net. Ordinary DRC misses this manufacturing conflict; the extra C504.2 core connection is a defect, not progress.
5. `hardware/mcu_power_ground_clearance_0109`, PCB **77537f15c2beff27ec3098c0ccd9d3dd5cd10ac335b74c4909954f2fedcf4a24**, 108-file manifest **b60e4be8abb820cff7e2e61f23cda937ddc4c1d2afb14ab144ead38c5d93496e**: moved the same0.60/0.30mm via to(4.25,10.75), added0.5mm F-ground link. Actual fresh-fill native **0/181/0**, exit5; AON **14/39**, GND **39/102**, including all nine actual U101.57 physical pads. All630 original copper,102 footprints/366 pads, prior connected components, net assignments and source rules preserved. Four actual native deletion/reversion counterfactuals and exact replay are included. C504.2 is correctly isolated again.

## Manufacturing and electrical gates remain open

The moved drill has only **23.8µm nominal clearance to top EP copper-square edges**. Its disk clears the full C504 pad-envelope by0.225mm nominal, drill by0.375mm, but this is not a certified drill/mask/body/assembly tolerance budget. Eight other vias remain inside EP solder lands. No filled/capped/tented via process, stencil, wicking/void, inspection, thermal capability, added cost or assembler feasibility is approved. Redesign may be required. Zero native violations do not close DFM.

MCU main analog supplies U101.2/.3 remain outside core. C207.2 and C504.2 remain outside core. The25 AON and63 GND pads below are **physical pad counts outside the relevant J106 core component**, not181 airwire items, not isolated component count and not necessarily entirely copper-free pads. Some can be mutually connected in islands. Supply without a verified local return is not completed decoupling. Plane area/erosion screening establishes no ampacity, transient, RF or thermal guarantee. Charging commissioning stays OPEN; unknown camera is not powered.

## Actual pin-domain map (current source, not historical annotations)

`extract.py` reads the native board and current schematic embedded `lib_symbols`, rejects inconsistent duplicated symbol definitions, and subtracts the frozen actual core physical-pad set. `remaining_pads.json` retains UUID, coordinates, actual net, source library/pin name and schematic path for all88 remaining pads. This index does not independently rerun fullDRC or finite connectivity; it consumes the frozen verified core set.

| Device | A-side supply | B-side supply | Actual GND pins |
|---|---|---|---|
| U201 SN74AXC8T245PWR | pin1 VCCA =3V3_AON | pins23,24 VCCB =SENS_VIO_1V8 |12,13|
| U202 SN74AXC4T245PWR | pin1 VCCA =3V3_AON | pin16 VCCB =SENS_VIO_1V8 |8,9|
| U203 SN74AXC4T245PWR | pin1 VCCA =3V3_AON | pin16 VCCB =SENS_VIO_1V8 |8,9|
| U204 TCA9517DGKR | **pin1 VCCA =SENS_VIO_1V8** | **pin8 VCCB =3V3_AON** |4|

**U204 reverses the A/B-domain naming relative to U201–203.** Do not generalize VCCA=AON to all translators. SENS_VIO_1V8 is the actual net spelling and is separate from3V3_AON. No SENS supply pad is included in the25 remaining AON count.

The proposed next bounded design topic is restoration/verification of the actual U201–203 VCCA + GND local decoupling (C201/C203/C205), and separately U204 VCCB with C207 ground return. This is a priority suggestion, not a safe-route approval or automatic restoration instruction. SENS_VIO_1V8-side C202/C204/C206/C208 and U204 VCCA must remain a separate review/domain. Assess actual available copper, same-net drilling conflicts, reference antipads and local loops before any implementation; preserve previously established components.

## Remaining-pad categories

The generated table below is exhaustive for25 AON and63 GND physical pads. Translator DIR pins tied to rails are identified as control pins, not mistaken for power pins. Other source names such as U501 NC/RES are reproduced as current source definitions, not newly approved datasheet tie instructions.

### 3V3_AON

|Category|Count|Pads|
|---|---:|---|
|other 3V3_AON|11|R203.2, R501.1, R502.1, R503.1, U101.2, U101.3, U301.1, U501.10, U501.2, U501.3, U501.9|
|AON capacitor supply|8|C103.1, C201.1, C203.1, C205.1, C301.1, C501.1, C502.1, C503.1|
|translator VCCA|3|U201.1, U202.1, U203.1|
|translator VCCB|1|U204.8|
|translator 1DIR|1|U203.2|
|translator 2DIR|1|U203.3|

### GND

|Category|Count|Pads|
|---|---:|---|
|other GND|42|C302.2, C303.2, C504.2, J103.2, J104.3, J105.2, J107.3, J202.1, J202.10, J202.13, J202.17, J202.4, J202.7, R104.2, R206.2, R214.2, R216.2, R218.2, R219.2, R220.2, R221.2, R222.2, R223.2, R224.2, R225.2, R226.2, R227.2, R228.2, R229.2, R230.2, R231.2, R232.2, R233.2, R234.2, R235.2, R237.2, R301.2, U301.2, U501.5, U501.6, U501.7, U501.8|
|GND return of AON capacitor|7|C201.2, C203.2, C205.2, C207.2, C501.2, C502.2, C503.2|
|GND return of SENS_VIO capacitor (separate domain)|3|C202.2, C204.2, C206.2|
|translator DIR1|1|U201.2|
|translator DIR2|1|U201.11|
|translator GND|7|U201.12, U201.13, U202.8, U202.9, U203.8, U203.9, U204.4|
|translator 1DIR|1|U202.2|
|translator 2DIR|1|U202.3|

### Separate sensor-domain inventory (not added to88 remaining pads)

C208.1 [1], C204.1 [1], U201.23 [VCCB], U201.24 [VCCB], R243.2 [2], U204.1 [VCCA], C202.1 [1], U203.16 [VCCB], R242.2 [2], C206.1 [1], U202.16 [VCCB], J202.23 [23].

These12 SENS_VIO_1V8 net pads are inventory only; this new document makes no sensor-rail core connectivity claim.
