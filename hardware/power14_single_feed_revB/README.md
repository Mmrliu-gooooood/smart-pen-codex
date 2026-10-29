# Single-feed revision B: explicit finite-width copper gate

**NOFAB. JP1 remains OPEN/DNP. Independent review still required.**

Rev A (`../power14_single_feed_candidate`, PCB12818a…8f8b2ca) was **rejected**: although its centreline resistor model reported zero charging-current flow in thermal traces, two retained thermal vias physically touched the original charger trunk at three positive-area regions outside C1. The original42-file freeze is retained as failed evidence. That numerical result did not prove physical isolation.

## Revision B

Baseline: original frozen14×45 PCB `5c5764e7576c9461464c12da3531410e63ef4db32a28a67a5fa6125ef0b92014`.
Candidate: `94ced2bd4100ba6fd8d9a9af11f101cc091a4c112a1bb3c8bb5dec2b2dedcdbc`.

Exact `REVB_EXPECTED_DELTA.json` geometry whitelist:
- Removed26 added-thermal copper objects:7 F.Cu shortcut tracks,2 offending through vias at(7.9,5.875)/(7.5,6.425),17 now-unused In2.Cu branch segments.
- Added43 tracks:3 F.Cu tracks,0.30mm wide,5.571320mm total;40 B.Cu tracks,0.15mm wide,19.968250mm total. No new vias. Other tracks/vias are unchanged.
- F.Cu path: C1.1(7.75,4.80)→(7.75,3.75)→(10.15,3.75)→existing thermal via(11.65,5.25), mm. It goes above C1, rather than retaining core-touching annuli or adding a via in the capacitor pad.
- B.Cu bridge joins existing thermal branch to that remote feed. This is a longer detour around other nets, not claimed optimal/production-quality routing. The many small route bends and long path merit layout refinement.
- All original charger-core track/via objects, all footprints/pad identities/positions/netnames/values/DNP, schematic sources and board rules remain unchanged. Filled polygons were regenerated and may differ.

## What passed freshly

Run `bash run_single_feed_checks.sh`; normal/optimized checks use explicit failure exceptions where specified.

- KiCad9 native ERC0; DRC0, unconnected0, schematic-parity0, all with `--exit-code-violations`, actual process exit0.
- 25 multi-pad nets connected, including native polygon-based physical connectivity, individual actual zone islands and drilled-via annuli.
- The copied independent finite-width audit (`physical_contacts.py`, provenance: `docs/verification/power14_single_feed_review_20261028`) finds **all original-core↔added-thermal VBUS copper contacts confined to C1.1**. No extra contact outside that pad. Shape expansion uses0.5µm inward polygon approximation and explicit drill subtraction. This is stronger than the previous centreline model, but not a manufacturing-tolerance or electromagnetic field proof.
- Delta whitelist verifies 26 removals/43 additions, no original core copper removal and no common-item changes. JP1 still DNP, sources/rules unchanged.
- Original frozen104 file hashes remain unchanged.
- Normal versus Python `-O` physical-contact, DC-network and explicit delta outputs agree. This does not certify every inherited helper against all failure modes.

## Conditional DC comparison, not safety signoff

The independent resistor implementation, adapted to the candidate path, assumes85°C copper, outer31.5µm/inner18µm, ideal zero-ohm pads/vias and centreline splitting. It excludes finite pad spreading, return impedance, via barrel resistance, heating, noise and dynamic device models.

- Only BQ U1.13 normalized1A: max added-thermal flow6.96×10^-14A/A, numerical zero; original wide trunk trace drop9.478628mV/A. Original board gave0.322809852A/A unintended fine-trace flow and6.821066mV/A total drop.
- Only U102.4 hypothetical25mA:9.800580mV drop, versus original7.046764mV. The extra route costs supply resistance;25mA is not a confirmed IC worst-case load.
- KCL and power conservation pass.1A is not USB current authorization.
- Finite-width topology is checked separately before relying on this conditional transfer model. Exact finite-current distribution within C1 pad still needs a more detailed model/physical measurement.

This candidate does **not** fully convert the downstream network into a tree or widen every0.15mm thermal trace. Quiet/Kelvin returns, differential ground movement, reference/NTC leakage, contamination, ramp/brownout/charging/LED/RF transients, sensor thermal coupling and cell/assembly/manufacturing limits remain open. Supply drop cannot be subtracted directly from comparator differential recovery/cutoff margins. Do not close JP1.

## Publication and reproduction

Only `SINGLE_FEED_REVB_MANIFEST.json` is authoritative for current source and evidence. Other copied files, old README-derived manifests, reports and previews in this scratch directory are **not current evidence** and must not be recursively published. Earlier failed routing reports are retained but excluded from the current whitelist.

Dependencies: installed KiCad9, system pcbnew/numpy/scipy, `../power_core_layout_candidate/power_core_NOFAB.kicad_pcb`, and immutable `../power_integrated_layout_14x45/`. Current native files suffice for review; `make_single_feed.py` then `bridge_back_supply.py` regenerate geometry with fresh UUIDs, requiring a new independent delta whitelist rather than overwriting this freeze.

No purchase, power-up, charging, physical measurement, Gerber release or GitHub publication occurred.
