# Camera isolation control source contract — research only

**NO FAB / NO POWER.** Exact parent is `imu_control_native_0522`, PCB SHA `5ed5f0ad90f5f15830f50479e0ecc48fe0685ffaff1819ff642a300f9550a1e9`. Source remains unchanged; script checks exported embedded-source net/pin/value identity. This is not certification of a complete safe board.

## Actual graph, not net-name assumptions

- U101 package48 is **GPIO42_MTMS**, not GPIO48. `CAM_IO_EN` joins R107.1 (100k ground default) and JP201.1.
- JP201 is **DNP_IO_COMMISSION, OPEN**. JP201.2 reaches R201.1 (`IO_ENABLE_LINK`); R2011k then Q201.G (`ISO_GATE`). R202100k pulls that gate to GND. Q201 is PMV30UN2: G1/S2/D3; S2 is GND.
- Q201.D pulls `CAM_ISO_OE_N` down when enabled. R20310k±1% pulls this net to **3V3_AON**. The seven pads are Q201.3,R203.1,U201.22,U202.14/.15,U203.14/.15. There is no MCU pad directly on the OE net.
- All five OE inputs are active LOW. U201 is SN74AXC8T245PWR; U202/U203 are SN74AXC4T245PWR. Their VCCA and control reference are AON, VCCB is external SENS_VIO_1V8.
- U204 TCA9517DGKR is deliberately opposite: VCCA1=SENS_VIO_1V8, VCCB8=AON. EN5 is **active HIGH**; `SCCB_EN_SAFE` has R2054.7k ground default and receives separate GPIO47 via JP202 OPEN and R204100R. Never join EN to OE.
- `SENS_VIO_1V8` arrives at J202.23, not from a local regulator. JP301 remains OPEN. No commissioning links are bridged; no NC outputs connected.

## Expected static states, conditional on actual assembled continuity

| State | AXC | TCA | Qualification boundary |
|---|---|---|---|
| AON valid, MCU high-Z, JP201/202 OPEN | R202 gate-low/Q201 off; R203 OE-high => isolated | R205 EN-low => disabled | Actual hot leakage, contamination and transient response still unmeasured |
| Links hypothetically commissioned, MCU high-Z | R107/R202 intended low defaults; OE high | R108/R205 intended low defaults | GPIO reset/debug internal pulls must be verified; high-Z is an assumption, not a reset guarantee |
| AON valid, VIO truly0V | AXC either-supply<100mV isolation applies | Power-good inhibits while VCCA below0.8V | Not a guarantee at arbitrary partially powered voltages or of zero back-power through complete head |
| Both rails valid, GPIO42 high after authorized commissioning | Q201 pulls OE low, enabling selected directions | Remains separately controlled by GPIO47 | Not implemented by NULL board provider; no startup/stop sequence tested |
| Shutdown | First request I/O disable, idle and disable SCCB, stop clocks, then remove head power | EN changes only during bus idle | Delay and rail-decay requirements need measurement; no invented fixed delays |

## Manufacturer evidence and quantitative screens

- [TI SN74AXC8T245 SCES875C](https://www.ti.com/lit/ds/symlink/sn74axc8t245.pdf), pin functions/§5.3/§7: OE22 high isolates, controls reference VCCA; either rail below100mV isolates outputs. Pull OE toward VCCA for startup/shutdown. Partial-power-down current is finite, not zero. At3.0–3.6V, control VIH≥2V and VIL≤0.8V.
- [TI SN74AXC4T245 SCES877B](https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf), PW pin table/§5.3/§7.3: OE14/15 low enables; control domain VCCA; either rail<100mV isolates. Control transition-rate specification must be respected: **10k passive OE rising edge with five input loads and route capacitance is not yet slew-qualified**. No resistor change is silently proposed or applied. Unused inputs still need proper bias; NC outputs are not bias inputs.
- [TI TCA9517 SCPS242D](https://www.ti.com/lit/ds/symlink/tca9517.pdf), §7.3/7.5/9.3.2/11: EN has an internal pull-up to VCCB. Its low-input current reaches30µA at EN0.2V; R205 max4.747k gives a142.41mV screening drop, below both0.2V test level and0.9V VIL at3V AON. This is a component-level screen, not a full leakage proof. VCCB logic powers the part; power-good thresholds are2.5V/0.8V. EN transitions require idle buses.
- [Nexperia PMV30UN2](https://assets.nexperia.com/documents/data-sheet/PMV30UN2.pdf), pin table/characteristics: G1/S2/D3. Specified100nA gate leakage at25°C gives10.1mV across maximum R202; drain leakage1µA is specified at25°C only. **Do not extrapolate this to hot-board worst case.** R203 sink demand at3.6V/9.9k is363.64µA before control leakage. Logic-high gate drive, turn-off delay, contamination, hot leakage and OE high/low thresholds require bench verification.

## Scope accounting

The original '7 gaps' is six airwires joining seven OE pads plus one R203 AON connection. A **complete MCU-to-commissioning control graph needs10 gaps**: additionally two CAM_IO_EN and one IO_ENABLE_LINK. Already connected ISO_GATE and ground defaults are preserved. Commissioning links remain separate nets, not logical short-cuts.

Only research candidates are permitted. Unknown purchased camera must not be connected to power. Cell/charging/thermal/ESD/SI/DFM gates remain. Firmware board provider is absent; no actual camera operation, wake behavior or low-power performance is claimed.
