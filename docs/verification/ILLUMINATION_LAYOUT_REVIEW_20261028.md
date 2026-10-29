# Illumination layout: independent review

Date: 2026-10-28 UTC. **NOFAB.** No new connection error found in the checked candidate. It is a resistor-limited LED switch, not a constant-current driver or optically qualified illuminator.

## Snapshot and fresh checks

All 42 manifest entries matched. Manifest SHA-256: `d3e42f7e22d143ef9e59edb0002ce3f2a96a660ffd94494305fd7d65cf782d08`.
PCB SHA-256: `6ee6b9c71af987a6a7019f6a9be24666c72e85bf6cc23ef39682ad40bce178ba`.

Fresh KiCad source export and all-severity ERC: **0 violations**. Fresh PCB DRC with schematic parity/all-track-errors: **0 violations / 0 unconnected / 0 parity issues**. Independently compared complete endpoint/net/pin-function/type sets against the original illumination XML; all 7 components, values and 16 endpoints agree. Actual board pad nets, values and DNP also agree. The assigned interface footprints are not changes to the electrical circuit.

An independent actual pad/track/via graph, with separate actual filled-polygon contacts, confirms all **7 multi-pad nets** connected. The three GND pads are joined through actual routing and the single B.Cu ground fill. Same-net labels alone were not accepted as physical connectivity.

## Defaults and interfaces

- J1 is 1=3V3_AON, 2=GND, 3=ILLUM_STROBE. The frozen host XML associates ILLUM_STROBE with U101 pin 36, **GPIO48_SPICLK_N**, rather than an assumed camera pin.
- Q1 actual assignments are 1=gate, 2=source/GND, 3=drain/LED_K. R2 is the 1 kΩ series gate resistor; R3 is the local 100 kΩ gate-to-source pull-down. This supplies a static high-impedance-host OFF bias, not a guaranteed glitch-free startup or ideal zero-leakage output.
- JP1 is the only XML/PCB DNP item. Its separate physical pads remain on distinct 3V3_AON and LED_COMMISSIONED nets. It disconnects LED supply when left OPEN; routing has not bypassed it.
- Intended path is J1.1 → OPEN JP1 → R1 330Ω → J2.1 LED_A → external LED → J2.2 LED_K → Q1 → protected GND. **LED_K is not GND**. No connection to an unknown camera's 30-pin interface is established or authorized by this circuit.

## Mathematical limits and qualification boundary

Independently recalculated, conditional on rail ≤3.6 V, real R1 ≥326.7Ω and no resistor bypass: shorted-LED current ≤**11.0193 mA**, resistor dissipation ≤**39.6694 mW**, and static MOS load-line dissipation ≤**9.9174 mW**. These are conditional static electrical bounds, not actual brightness, full-temperature resistance qualification, dynamic switching losses or enclosed-pen thermal results. R1 short/bypass remains outside that limiting protection.

The SOT-23 footprint remains a **library candidate**. This review does not claim exact original-manufacturer landpattern/mask/paste verification; the documented unavailable p11 drawing remains an assembly gate, not a reason to invent a pass or bypass the failed download. Pad-number correctness and native parity do not close that gate.

Still open: actual LED selection and radiant output, eye/skin safety, exposure timing and usable image illumination, gate/startup waveforms, resistor total error and derating, wire order/insulation/strain relief, return routing in the assembled pen, switching interference, final mechanical fit and cost. The bare 8×15 mm PCB is not the full assembly envelope. JP1 stays OPEN pending those checks. No source changes, physical tests or manufacturing approval were performed.
