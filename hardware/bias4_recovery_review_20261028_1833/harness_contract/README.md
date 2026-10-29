# Version-locked power-mode harness contract — NOFAB

This is a logical integration artifact, **not a released physical harness**. `power_mode_mapping.json` locks the BIAS4 MCU source and the integrated 14×45 power candidate by SHA-256 of their actual PCB, root/child schematics and XML files. Exact XML net names are preserved; prefix stripping is not used to invent equivalent signals.

Approved-by-this-logical-check endpoints only:

| Logical signal | BIAS4 source | Integrated 14×45 target |
|---|---|---|
| USB_EN1 | J107.1 / USB_EN1 | J5.1 / /core/USB_EN1 |
| USB_EN2 | J107.2 / USB_EN2 | J5.2 / /core/USB_EN2 |
| GND | J107.3 / GND | J5.3 / GND |

**This target has no external CE port.** No charge permission or jumper closure follows from a passing map. Old standalone power-core J5 is a different four-pin interface: pin3 is /CE_PERMISSION_EXTERNAL and pin4 is /GND. Passing that legacy target, even with its correct hashes, is rejected. A 1:1 legacy harness would connect the MCU ground to the CE-permission interface and is not this contract.

Fresh native XML export and actual PCB pad inspection are recorded in `native_port_evidence.json`. The integrated target has actual J5 pads matching the three native net names; the legacy board has actual J5 pads matching its four-pin definition. **BIAS4 J107 still has no footprint**. A matching source symbol is not an existing solderable port.

Run from any cwd using the files in their current repository-relative layout:

- `python verify_mapping.py`: locks and exact logical mapping; exit nonzero on a mismatch.
- `python test_mapping.py` and `python -O test_mapping.py`: seven positive/negative cases each, including legacy target rejection, ground miswire, duplicate wire, missing ground, changed source hash and CE injection.
- `/usr/bin/python3 check_native.py`: uses installed pcbnew and KiCad CLI to re-export the three source schematics and inspect actual pads; writes new check evidence only here, never changes source PCB/schematics.

`build_contract.py` records the explicitly reviewed initial versions. **Do not regenerate hashes merely to make a failing check pass**; any source change requires intentional re-review of semantics, defaults, physical pads and revised contract. Tests use explicit exceptions and still reject the negative inputs under optimized Python.

Unclosed physical/electrical gates: actual mainboard lands or connector, interconnect length and return path, keying/polarity/insulation and strain relief, default charger mode and MCU high-impedance/brownout behavior, USB current authorization and actual charging safety. The two USB mode controls are not a safety substitute for the locally held-open commissioning chain.
