# Accepted data8 bias branches and saved support CAD — static research only

LOCAL ONLY pending publication approval. The 44 dcbd/static dependency blobs are now verified published at remote `95a3292a953ce4d876ec1f20863e32f5fcd2eb0e`, tree `9fa97ec1cf0a422bccdf14a7765f8183b450c3db`, exact-head CI41066551268 success. DEPENDENCY_PUBLICATION.json records individual blob checks. SOURCE_MAP origin labels are historical preparation-time metadata; the former LOCAL_QUEUED427_NOT_PUBLISHED labels are superseded by this publication evidence. Preserve chronology and all old manifests unchanged.

Exact accepted PCB: `4d7d95d253b3c8c994a7f2c4c628087346c271ea290c69aa511ea9a1cb8eadad`, author manifest `8f534ddbb2ec79d4f9a2e625fe0850fc42076e4f61716819cdecefe3dfed027c` (115 content files). Independent review reports static 0/59/0, not a complete working device. The original PENDING author status is historical; later independent verdict is separate, not fabrication or power approval.

Included: exact author data8 allowlist; independent electrical evidence and byte-identical execution aliases; explicit mechanical author manifests, independent static reviews and required runtime/provenance sources; accepted outline1239, support1251, final saved data8/support1314. No SCCB1322 or newer successor. No whole exploratory planner/trial directories.

## Rejected negative controls, never adopted CAD

Exactly three files under `assembly_support_proposal_20261030_1238/corrected_connected/` (RevD_BENCH, ACCESS19, ACCESS20 FCStd) are required by the accepted independent support reviewer. Their zero support gap intentionally fails the newer 0.2 mm requirement. Label: **REJECTED_ZERO_GAP_NEGATIVE_CONTROL_ONLY**. They are not the accepted1251 support files or the accepted1314 saved integration. No other failed support trial is included.

## Unresolved gates

NOFAB / NOPOWER; JP201/JP202/JP301 OPEN; provider NULL. Eight U101 long links remain disconnected. Added 100k output branches and 3.536–12.387 mm stubs are not timing/loaded-VOH/edge-rate/return-impedance qualifications. Mutual new-via reference void exceptions are disclosed, not waived; mixed In2 is not GND. Inherited SCCB source-hole, C207 loop, dynamic OE/sequencing, power, RF/FPC, battery/thermal, manufacturing, real assembly and firmware gates remain open. CAD support results are nominal geometric contact/access only, not fabrication tolerance, fatigue, force or assembly qualification.

## Privacy and reconstruction

Private supplier PDFs/photos, secrets, executables, caches, backup files and unrelated trials are excluded. AXC8 source cache PDF is not bundled; source_roles.json retains public TI citation and recorded hash. Original freeze.py is retained as provenance, not rerun against absent vendor cache.

Reconstruct into a new separate workspace by hash. Do not run generators against frozen publication files. Mechanical inventory CAD paths need transparent in-memory relocation only. Use a distinct untouched input view for hash-bound author bindings, and separate output locations/copies for regenerated KiCad logs and FCStd containers. Regenerated FCStd ZIP bytes are not assumed deterministic. Python boundary audit forbids moving-workspace reads; no full native syscall-tracing claim is made (ptrace unavailable). Verification completed: 40 electrical and 50 accepted mechanical commands passed. See VERIFICATION_SUMMARY.json and MECHANICAL_EXACT_OUTPUT_DELTAS.json. Twenty-four of 25 mechanical normal/optimized pairs are JSON byte-equal; the support-rebuild pair differs only in three regenerated FCStd ZIP hashes, verified against the actual regenerated files. Historical NOT_YET_FROZEN binding fields advance to the exact accepted manifest; original reports remain unchanged. One initial native negative-child empty-output exit was recovered by exact-cut and full-suite reruns without changing checks; its cause remains unestablished and the attempt is disclosed.

## Reproduction commands

From this `_closure` directory (use new destinations):

```sh
python reconstruct.py REPOSITORY FROZEN_INPUT [QUEUED427_OVERLAY] [THIS_PAYLOAD_OVERLAY]
python mechanical/reproduce_final492.py --source-map SOURCE_MAP.json --input-root FROZEN_INPUT --output NEW_MECHANICAL_RESULTS
python reconstruct.py REPOSITORY ELECTRICAL_WORK [QUEUED427_OVERLAY] [THIS_PAYLOAD_OVERLAY]
python reproduce_electrical.py ELECTRICAL_WORK NEW_ELECTRICAL_RESULTS
```

Optional overlays are local staging inputs, not evidence of remote publication. Installed toolchain is recorded in TOOLCHAIN.json. The 44 already-published dependency blobs must be available and hash-identical; reconstruction fails rather than substituting moving workspace files.
