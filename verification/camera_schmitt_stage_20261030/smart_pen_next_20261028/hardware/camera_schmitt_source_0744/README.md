# Source-only active-Schmitt camera candidate

2026-10-30. **EXPERIMENT / NOFAB / NOPOWER.** No PCB supplied here. Stable AON and controlled USB-JTAG mode only. This is source input to the separately routed parent candidate, not a full power/reset/timing qualification. JP201/JP202/JP301 remain OPEN; provider NULL unchanged. No eFuse programming or physical power.

## Exact changes
- Remove Q201 PMV30UN2 instance. Add U205 **TI SN74LVC1G14DCKR**:1NC,2A=ISO_GATE,3GND,4Y=CAM_ISO_OE_N,5VCC=3V3_AON.
- New custom symbol in embedded controls_sccb and local ISO.kicad_sym, preserving the original three external control labels/wires and adding VCC and explicit NC. Input/output/power electrical types are explicit, not generic passive pins.
- C209100nF16V X7R±10%0402, proposed KEMET C0402C104K4RACTU,1AON/2GND. No guaranteed minimum effective capacitance claim; placement/supply response require verification.
- R202100k1%→10k1%, same0603 footprint, proposed Yageo RC0603FR-0710KL. R107/R201/R203 and every other old component/net unchanged.
- Custom SmartPenIO:TI_DCK0005A_Schmitt_OfficialLand: official example rectangular pads .95×.4mm, X±1.1mm, Yleft−.65/0/+.65,right±.65. 1top-left,2middle-left,3bottom-left,4bottom-right,5top-right. No silent generic-KiCad SC70 substitution. F.Fab bodymax1.4×2.15mm. Courtyard ±1.85×±1.35 is our conservative assembly margin, not an official TI courtyard requirement. This footprint has no fabricated or assembled validation.
- Schematic experiment warning changed; U205 reference/value moved clear of NC marker after visual inspection. Other sheet contents preserved.

`handoff.json` provides actual instance UUID/full hierarchy paths and C209 pad geometry. New NC pin1 exports as `unconnected-(U205-NC-Pad1)` with `no_connect` type; it must not be routed to another net or mistaken for ground.

## Source evidence
- TI SN74LVC1G14, SCES218AA October2025; pinout/DCK0005A example land: https://www.ti.com/lit/ds/symlink/sn74lvc1g14.pdf
- Official exact resistor spec: https://yageogroup.com/component-documentation/download/specsheet/RC0603FR-0710KL —10kΩ1%0603,100ppm/°C,0.1W70°C. Tolerance is specified at reference conditions; do not treat 1% as complete hot/cold error. Calculations in prior0730 study use tolerance only and require temperature coefficient allowance for final worst-temperature budget.
- Official exact capacitor spec: https://search.kemet.com/component-documentation/download/specsheet/C0402C104K4RACTU —0.1µF±10%16V X7R0402. Availability/price not qualified.
- Broader rail/boot/edge/model restrictions remain `docs/electronics/camera_schmitt_candidate_0730` and frozen0719 audit.

## Actual checks
- KiCad9.0.2 netlist export succeeded.
- Real ERC: **0 errors,1 inherited dangling VBUS_5V global-label warning**; CLI exit5 because `--exit-code-violations` includes warnings. No suppression added.
- `tools/check.py`: every old pin-net/function/type except removed Q201 preserved; only old value change R202; added exact U205 and C209 pinmap verified; custom footprint dimensions checked. Frozen0628 manifest all799files rehashed unchanged. Normal and `python -O` outputs identical.
- `tools/build.py` deterministic UUID5 and explicit source-edit contract; independent `replay/native` reconstruction byte-identical to native. `replay.json` records comparison. Replay files are redundant and excluded from publication manifest.
- Rendered actual KiCad controls sheet SVG→PNG reviewed. First draft had value close to NC marker; moved properties and reran export/ERC/render. Final `controls_sccb.png` verified clear; geometry/trace interpretation relies on native source and exported netlist, not screenshot alone.

No new PCB/ERC-parity/DRC/physical routing claim in this source package. Parent must synchronize paths/values/netlist with actual new PCB, run true all-track DRC/parity, functional graph/cut/replay negatives, and independent review. Old source 0628 untouched. Continuous worst-case output edge, five-OE load, loaded GPIO VOH, brownout/startup, thermal and commissioning gates remain OPEN.

## Reproduce
Run `python tools/build.py /absolute/new/replay/native` from this package (destination must not exist). Then KiCad export netlist/ERC using copied root `native/mainboard_revD.kicad_sch`; use writable XDG_CONFIG_HOME/XDG_CACHE_HOME/XDG_DATA_HOME. `tools/check.py` compares the primary exports to frozen0628. The generated library/footprint are project-local. No updates to shared installed KiCad libraries.
