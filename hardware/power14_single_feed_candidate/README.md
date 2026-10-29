# 14×45 mm single-feed thermal-supply candidate

**NOFAB. JP1 remains OPEN / DNP. This is an isolated layout candidate, not a production release.**

## Authoritative files

Only `SINGLE_FEED_MANIFEST.json` lists current candidate evidence. Other copied files in this research directory (old `drc.rpt`, `erc.rpt`, `preview/`, `projection_check.json`, old `run_checks.sh`, routing experiments) are inherited baseline working material and are **not current verification or previews**. Do not publish this directory recursively. Use `run_single_feed_checks.sh` for this candidate.

The original frozen `hardware/power_integrated_layout_14x45` and its 104-file manifest remain unchanged. This candidate uses its schematic, rules, footprints, placements and BOM unchanged.

## Exact layout change

Removed seven **added thermal F.Cu VBUS tracks**, not original charger-core copper. Added three 0.30 mm F.Cu segments:

C1.1 (7.75, 4.80) → (8.10, 5.15) → (8.10, 5.825) → existing thermal via (7.50, 6.425), in mm.

Exact UUIDs are in `single_feed_delta.json`; actual geometry and whole-board preservation are checked in `single_feed_check.json`. All other tracks/vias and every footprint/pad/value/net/DNP are unchanged relative to the frozen integrated board. Filled polygons are regenerated and may differ; no claim that all copper fill is byte-identical.

This removes additional front-side connections to the J2/BQ charging trunk. The retained old wide charger trunk now carries the full conditional BQ load. The new feeder joins at C1's input pad under the ideal-pad model. The rest of the thermal network remains the previous routed network, including 0.15 mm segments, local loops and cross-layer paths. **This is not a complete replacement of every thermal trace with a 0.30 mm tree**, and does not independently qualify quiet/Kelvin returns.

## Fresh checks, 2026-10-28 UTC

- Native ERC: 0 errors, 0 warnings, `--exit-code-violations` enabled.
- Native DRC + schematic parity: 0 violations, 0 unconnected pads, 0 footprint errors; true process exit 0.
- All 25 multi-pad networks pass actual-contact/filled-island connectivity checks.
- Explicit source/delta checker preserves all baseline copper except the seven whitelisted additions; unique JP1 remains DNP and schematic source/rules are byte-identical.
- Normal Python and `python -O` produce equal resistor-network and delta-check output; safety decisions in the new delta checker use explicit exceptions, not asserts. This does not certify every inherited script fail-closed.
- Original frozen 104 file hashes remain unchanged.

## Conditional DC comparison

The independent analysis implementation is reused, adapted only for candidate path/source hash, in `reproduce_network_candidate.py`. This is a lumped network, not finite-element/current-rating signoff. Assumptions: 85°C copper, outer31.5µm/inner18µm, ideal zero-ohm pads/vias, no source/return/pad-spreading impedance, heating, dynamics or device models.

- Only BQ U1.13 = 1 A normalized load: old board added-thermal maximum 0.322809852 A/A; candidate maximum 6.8×10^-14 A/A (numerical zero). KCL and power conservation checked.
- Candidate J2→BQ trace drop 9.478628 mV/A; old parallel network 6.821066 mV/A. Increased drop is expected after removing the unintended parallel shortcut. It does not establish or violate a current rating by itself.
- Only U102.4 = hypothetical25mA: candidate drop 7.062865mV vs old7.046764mV. This load is a sensitivity case, not an actual specified IC worst-case current.
- 1 A is not USB current authorization. The PCB still requires USB startup, charging-current, copper/via/temperature and component qualification.

Do not subtract VBUS drop directly from comparator differential threshold margins. The previous independent report distinguishes 20°C recovery availability from 10°C/45°C inhibit safety. This layout change does not close reference/NTC leakage, differential ground shift, dynamic ramp, thermal coupling, assembly, cell or firmware safety gates. Never close JP1 on this evidence alone.

## Reproduction and dependencies

Run `bash run_single_feed_checks.sh`; installed KiCad9, `/usr/bin/python3` pcbnew and numpy are needed. Relative preserved-source dependencies are `../power_core_layout_candidate/power_core_NOFAB.kicad_pcb` and `../power_integrated_layout_14x45/` (frozen manifest). `make_single_feed.py` regenerates an alternate candidate with fresh track UUIDs and updates its delta manifest; do not run it on a frozen publication snapshot.

No power-up, physical measurement, manufacturer DFM, Gerber release, purchasing or remote publication was performed.
