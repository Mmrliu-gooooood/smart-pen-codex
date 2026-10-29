# BIAS4 recovery: fresh independent read-only verification

2026-10-28 18:34 UTC. **NOFAB / not ready to manufacture.**

## Exact input and preservation

- Source: `hardware/mainboard_resume_20261028/mainboard_revD.kicad_pcb`.
- PCB SHA-256: `0796d092b4775e314f9b5f43b62b0a7ba153c9b4e8804fb02c6f0ea8cdeae5cc`.
- Comparison XCLK5 PCB: `9f9937d894fa52d63c5edebd29d10a9396d6f8463819d4a3714fa2724c9bed49`.
- 246 pre-existing non-cache files hashed before/after; changed files: **0**. No source schematic, board, project, guard or recorded result was overwritten. New reports are confined to this directory.

## Fresh native checks

KiCad 9.0.2 was invoked with writable, isolated XDG paths. The initial help-only command had default-XDG read-only warnings; those were not treated as verification and all actual checks below use the explicit writable environment.

- Native XML export exit **0**.
- ERC with `--severity-all --exit-code-violations`: exit **0**, 0 messages.
- DRC with `--severity-all --all-track-errors --schematic-parity --exit-code-violations`: exit **5**, as required for this incomplete board.
- DRC reports **4 unconnected items**, **34 dangling vias**, **2 dangling tracks**, **16 missing-footprint parity entries**. No other native geometry violation was reported. This is not a DRC pass.
- Remaining actual disconnections: CAM_HREF has 3 copper components (two missing joins); CAM_PWDN_UART_RX has 2; RF_SIP has 2.

## Source and real-copper invariants

The previously independent audit was rerun from a new output directory, with only input/output path rebinding. It passed in normal Python and `python -O` using explicit exceptions. It independently checks native XML component/pin records, actual board pad nets and attributes, exact retained track/via geometry and actual per-filled-island connectivity (not connectivity inferred from matching net names).

- 90 schematic entities and **374 pin endpoints** retained.
- Sole schematic property delta relative XCLK5: R217 footprint changes 0603 to 0402; same 100 kΩ value, DNP/BOM state and net mapping.
- 74 PCB footprints / 269 pad shapes; 73 other footprints' pad geometry unchanged.
- **3281** retained copper items unchanged; only 2 isolated old D7 items removed. Added copper is 4 CAM_D7 items and 2 GND items.
- Real copper joins U101.19, U201.10, R217.1. All **27 AON**, **75 GND**, **11 VIO** pad shapes remain connected.

## Guard behavior

All 10 normal/optimized cases freshly reproduced: good literal-net contracts continue to the post-guard marker and a DRC invocation; wrong-net, empty, missing-UUID and duplicate-key contracts return nonzero before both. The good control-flow harness intentionally uses DRC without violation exit code: its exit 0 proves continuation only, **not a clean board**. The separate full DRC invocation above returns 5.

This review does not prove all legacy scripts fail-closed under optimization. It does not qualify 0402 land geometry/assembly, SI, supply integrity, RF/USB, camera pin mapping, battery/thermal safety, or actual writing accuracy. No purchase, power-on, flashing, Gerber release or GitHub write occurred.

Evidence: `exit_statuses.json`, `erc.rpt`, `drc.rpt`, `independent_check.json`, `guard_recheck.json`, per-command stdout/stderr, before/after source hashes.
