# Post-r28 accepted static research — LOCAL ONLY

No remote writes are authorized by this draft. NOFAB / NOPOWER; JP201/JP202/JP301 OPEN; provider NULL.

Scope ends at the jointly reviewed SCCB local-reference board `dcbd2e6501c8294ece5ecf7b41ffcc86ccc7f58f7cb54ececfdf24962a50f697` (0/67/0) branching directly from accepted control-envelope `8312b1d5ec56f0ab4c396cba2b78449e191f06225bf9aa64ea6522fd1c3c68bb` (0/69/0). Root accepted this strictly scoped static/nominal result at 12:25 UTC. Later CAM work and post-1216 candidates are excluded.

The original author snapshots may say PENDING REVIEW: those historical bytes are intentionally unchanged. Independent review verdicts, exact-board mechanical reports and this staging boundary distinguish subsequent scoped static acceptance from fabrication, power, real assembly, SI or dynamic qualification. 0 DRC violations does not imply a complete/usable pen.

Accepted source chain from r28: ground_local0920 → tail1000927 → tail_courtyard0949 → ground_pair1007 → unused_bias1017 → control_envelope1051 → sccb_local1216. Each author manifest is an exact allowlist. No whole author/review directory is collected.

## Required diagnostic exceptions, NOT adopted designs

- Gated control1041 PCB + materialization are read only by accepted1051 alternative_delta to prove replacement equivalence. They are not a selected successor.
- Gated SCCB1131 PCB is read only by1216 local_repair_delta and source-hole/bypass advisories. No1131 planner or whole directory is included.
- Source-hole1212 and bypass1148 advisories retain their specified exact native measurement snapshots. They explain reference and bypass compromises, not acceptable high-frequency performance.
- Negative cut native projects are not shipped wholesale. Original cut generators are shipped, and isolated tests must regenerate and exercise them in normal and optimized modes.
- Strict1204 comparison, dominant-reference1215 planner, intermediate relocation/rotation searches, exploratory failures and later CAM work are excluded unless a specifically enumerated artifact is directly required by an accepted check.

## Open limitations

SDA source-via merged clearance with CT/ON remains an explicit reference exception. Mixed-power In2 loss is disclosed, not relabeled as GND. U101.44/45 remain separate from the U204/pullup branches. C207 new plane span increases1.155500mm; shorter surface leads do not prove a better bypass loop. Actual edge-rate/loading/return impedance/EMI, OE startup, loaded VOH, battery/thermal, real FPC, tolerances, assembly/probe access and all fabrication/power release gates remain open.

## Privacy and reproduction

Private manufacturer PDFs, photos, credentials and host executables are excluded. The AXC vendor PDF remains a hash/public-link dependency only; original freeze.py is retained as provenance but is not rerun against a missing private/source-cache PDF. Native checks/replay/negative cases do not require that PDF.

All original bytes are staged by SHA256 and git blob identity. SOURCE_MAP records exact reconstruction aliases and prior-r28 reuse. Mechanical inventory absolute paths require a transparent in-memory path relocation to four exact already-published CAD contexts; inventory bytes are preserved. Python audit blocks moving-workspace reads; native source paths are reconstructed locally. ptrace/strace is unavailable in this sandbox, so no full native syscall-isolation claim is made.

Isolated verification passed; see VERIFICATION_SUMMARY.json. This remains a local proposal pending publication approval. Reconstruct with `python reconstruct.py REPOSITORY NEW_EMPTY_DEST`; use a fresh reconstruction for electrical and mechanical suites separately because KiCad rewrites path-bearing logs. Mechanical wrapper accepts reconstruction root and each script listed in MECHANICAL_INPUTS.json. Original frozen files are not edited.
