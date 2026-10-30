# Camera OE active-edge candidate — source decision, not a native revision

2026-10-30. **RESEARCH / NOFAB / NOPOWER.** Frozen 0628 native and 0719 audit unchanged. All commissioning bridges OPEN; provider NULL. No purchasing/publication. This study recommends the next *bounded experimental* revision under controlled stable-power commissioning; it does not require proving every possible software behavior before prototype work.

## Decision and minimum local change proposed (NOT applied)

Prefer **Texas Instruments SN74LVC1G14DCKR**, active push-pull Schmitt inverter, SC70-5, AON powered. Replace Q201's open-drain function: pin 2 A = ISO_GATE, pin 4 Y = CAM_ISO_OE_N, pin 3 GND, pin 5 AON, pin 1 NC. Add local 100 nF bypass. Retain R201 1 kΩ, R203 10 kΩ pull-up, R107 100 kΩ and JP201 OPEN. Propose R202 from 100 kΩ to **10 kΩ, 1%** for firmer external input default; this is a documented proposed source change, not an applied one. Preserve the existing five OE terminals and their domain assignment. R203 is now a passive bias, not the edge generator. New component references must be checked for uniqueness during native implementation. Do not substitute a different manufacturer's similarly named part.

The original low input → Q off → OE high polarity is preserved by the inverter: low input disables camera translation; high input enables it. No firmware/provider change is justified by this proposal.

Controlled prototype mode: AON stable within 3.0–3.6 V, correct sensor VIO established, JP201 remains OPEN until separately authorized commissioning, only USB-JTAG (no pad-JTAG on GPIO42), no GPIO42 internal pull-up/alternate function/hold that can assert enable. GPIO42 high intentionally enables and cannot be distinguished from an active-high debugger drive: this is an interface mode restriction, not a request to burn eFuses. Observe the gate and OE at the actual translator pins before camera connection.

## Official selection evidence

TI datasheet SCES218AA October 2025: VCC 1.65–5.5 V; DCKR −40 to 125 °C; Schmitt input; push-pull output; partial-power-down Ioff. Pin mapping above from §5. II max ±5 µA at VI=0/5.5 V and VCC=0–5.5 V; Ioff max ±10 µA at VCC=0. Endpoint tests are not a blanket guarantee of every intermediate ramp voltage. At 3 V, VOH ≥2.4 V at −16 mA and VOL ≤0.4 V at 16 mA; at 100 µA, VOH ≥VCC−0.1 and VOL ≤0.1 over the listed VCC range. ICC max 10 µA for the specified static rail-input conditions; midrail input can draw additional current.

At VCC=3 V, VT+ max=1.87 V and VT− min=0.84 V; at 1.65 V VT− min=0.39 V. Datasheet table/figure interpolation is not a substitute for an independently characterized corner. At 3.3±0.3 V and CL=50 pF, tpd max=5.5 ns to 85 °C, 6.5 ns to 125 °C. **This is propagation delay, NOT a maximum output rise/fall-time guarantee.**

SN74AUC1G14 rejected: maximum recommended VCC 2.7 V, incompatible with 3.3 V AON without another rail. Nexperia 74LVC1G14 is a possible alternate but not interchangeable by assumption: different static guarantees and also no output-transition maximum. TI remains the selected exact-source candidate.

## Static budgets and limits

`calculate.py` records deterministic arithmetic, not a SPICE or production qualification.

- Proposed R202=10 kΩ±1% and inverter II=5 µA gives 50.5 mV worst resistor drop for JP201 OPEN, before board leakage. A chosen 0.2 V engineering ceiling gives 19.802 µA total-source budget, leaving 14.802 µA after inverter leakage; 0.2 V is a design target, not a datasheet threshold.
- ESP32-S3 datasheet §5.4 gives IIH/IIL max 50 nA **at 3.3 V, 25 °C** and VOH≥0.8VDD **with high-impedance load**. Do not extrapolate either to all temperature or the approximately 0.3 mA pull-down load. The arithmetic input-high margin is a provisional screen only, pending loaded-GPIO characterization/qualified specification.
- Five AXC OE inputs: ±1 µA each to 125 °C under their specified powered endpoint tests. At 3.6 V and R203 min9.9 kΩ, low-state load from R203 plus five OE leaks is 368.636 µA. This is far below the LVC static 16 mA test current, but does not prove dynamic edges.
- Choose a 100 µA total high-state leakage budget to use LVC's VCC−0.1 specification; 5 µA for OE leaves 95 µA for other leakage under valid operating conditions. This is an allocation, not a measured board-leakage maximum. Sensor-VIO-off and intermediate rails must be checked separately.
- Internal 45 kΩ pull-up is only typical. A 10 kΩ external pull-down improves the nominal divider but cannot prove immunity to unbounded internal pull-up or active pad-JTAG. Explicitly disallow those modes when connected.

## Output transition and capacitance — evidence separated

AXC4/8 require input transition ≤10 ns/V at AON=3.0–3.6 V; OE is a standard CMOS input, no documented slow-OE exemption. The passive R203 design is not dynamically qualified (0719 audit). Active shaping directly addresses this mechanism.

Five OE Ci values of 4.5 pF are **typical**, not max. A CL=50 pF datasheet delay test does not establish either our board's max load or a 10 ns/V output-transition guarantee. Use actual five-terminal copper, probe loading, pads/vias, package parasitics and temperature/voltage corners. No maximum load closure is claimed here.

Official TI IBIS downloads SCEM419/585/580 retrieved successfully. LVC model rev1.3 June2017 includes DCK and 3.3 V output; 3.3 V model columns use 3.3/3.0/3.6 V and 25/85/−40 °C ambient (junction40/100/−40). It **does not cover the 125 °C ambient selection range**. Ramp min-corner figures give 0.327 ns/V rising and 0.277 ns/V falling, but R_load=500 Ω and waveform C_fixture=0: these numbers are NOT the five-OE circuit waveform. Cref=50 pF is a reference field, not the waveform fixture capacitance.

AXC4 PW model uses package C=0.2 pF typ/0.24 pF max-column and OE input_3p3 C_comp up to 2.13619 pF among listed corners. AXC8 PW nOE pin22 package C_pin=0.56494 pF and same input C_comp numerical envelope. Five modeled terminals give a 12.20589 pF numerical envelope before PCB/probe contributions. This is not a datasheet maximum nor a simultaneously consistent PVT circuit simulation. Both models describe simulation-generated data and are supplied as-is. In particular, their smaller envelope cannot override the datasheet's typical 22.5 pF combined Ci with a new claim of maximum 12.2 pF.

Required prototype evidence: simulate exact interconnect and full model corners, clearly separate unsupported temperatures; measure both edges at every OE with calibrated probe-capacitance accounting across chosen rail/temperature/load envelope. Define maximum actual total load with conservative allowance or obtain manufacturer qualification. Confirm monotonic traversal and ≤10 ns/V, overshoot/undershoot and peak sink/source currents. Until then, active-edge proposal is a strong candidate, not dynamic compliance.

## Power/reset truth table and remaining sequencing gate

| Conditions | Expected / limit |
|---|---|
| AON=0; no external forced controls | LVC Ioff applies at its specified endpoint; AXC VCCA near zero isolates under its own limits. Not a guarantee for all intermediate rails. |
| AON in approximately 0.65–1.65 V, sensor VIO present | AXC may operate while LVC is below its recommended minimum: OE behavior **not guaranteed**. |
| AON stable 3.0–3.6 V, JP201 OPEN, input held low | LVC drives OE high: translation disabled, subject to leakage/load limits. |
| Stable AON, JP201 closed, GPIO42 ordinary input/high-Z, no pull-up/hold | External pull-down intends disabled; verify actual boot/reset configuration and loaded leakage. |
| Stable AON, permitted GPIO42 output low | Disabled. |
| Stable rails and intentional GPIO42 output high | Enabled, only after safe rail/direction/firmware checks. |
| Pad-JTAG / alternate output / internal pull-up / active hold | Unsupported operating mode; cannot claim reset-safe disable. |
| Sensor VIO=0 while AON valid | AXC specified VCC isolation applies near zero; intermediate VIO ramps not declared safe. |
| AON brownout while VIO remains present | Unresolved low-voltage window; bench sequencing gate retained. |

GPIO42 normal reset IE without default WPU, GPIO39 eFuse-related WPU exception, and reset-mode distinctions are documented in frozen0719. This does not guarantee every firmware/debug/reset state is low.

### Extra monitoring/default-disabled options versus minimum prototype

1. **Minimum local Schmitt prototype above:** smallest logic change, five OE edges actively driven once AON valid. Keep JP201 OPEN and enforce stable-power bench sequencing. Does not fix autonomous power-up/brownout behavior.
2. **Hardware qualified enable/reset:** a voltage supervisor/power-good-qualified logic path that forces OE high until AON and sensor VIO are valid, and asynchronously disables on MCU reset/undervoltage. Requires an exact device with specified low-voltage output behavior, threshold/hysteresis/timing, dual-domain loss behavior and five-OE output timing/load; another undefined low-V logic gate is not a fix. Adds component/route/space/cost. A GPIO-only monitor does not protect while MCU is reset.
3. **Default-off sensor supply sequencing:** enforce sensor VIO below the AXC isolation threshold until AON control circuitry is valid, and remove VIO before AON loses validity. Present VIO is externally provided through J202.23, so this needs a head-interface contract or explicit switching/discharge hardware, not just a software promise. Out of this local board edit scope.

Recommend option1 as the next experimental native candidate, keeping sequencing as an explicit NOPOWER commissioning gate; option2/3 need a separately bounded source decision before any production-safe claim. No need to expand this task into unrelated firmware behavior or whole-board relayout.

## Package, layout, cost and next native work

TI DCK0005A body max1.4×2.15 mm, lead-span max2.4 mm, height max1.1 mm, pitch0.65 mm. Official example land0.95×0.4 mm, row-center spacing2.2 mm. Generic installed KiCad SC70-5 uses0.65×0.4 mm/1.9 mm: do not blind-swap. Local bypass and a short ground path are additional placement demands.

`space_screen.py/json` only screen two poses at old Q201 center(2.5,69) against existing F.Cu; removing only Q201 pads, retaining tracks. At0° two proposed pins and180° four pins have conservative foreign-copper clearance collisions. **Not drop-in, not proof no local placement exists.** No new footprint/native/routing or DRC run is claimed. Next local candidate can deliberately remove only superseded Q201 control stubs, fit official land+bypass, preserve unrelated source/copper/reference and run actual all-layer checks. Do not retain conflicting old tracks merely to call it drop-in.

Exact TI part active. TI rendered page had no usable quote; LCSC C35740 identified TI but current parsed page had no price. Cached search quote was ~1.3 years old and rejected as current evidence. Procurement availability/current unit/assembly cost remain OPEN. A ¥5 logic+bypass design allowance, if used by project budgeting, is only an assumption and not a quote or proof of ¥380 total. No substitution or purchase authorized here.

No new schematic/ERC/PCB/DRC/parity/functional negative rerun: **no native changed in this study**. Prior0628 results remain0DRC/96unconnected/0parity, not a complete board or product. Future new native must rerun source/netlist parity, ERC, all-track DRC, all-layer/pad/via checks, cut-negative/replay and independent review; retain inherited clock/reference/DFM gates.
