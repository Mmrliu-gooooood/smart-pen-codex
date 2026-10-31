from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent
if (D/'review_manifest.json').exists():raise RuntimeError('already frozen')
files=set()
for dirname in ['native','final_candidate']:
 for f in (D/dirname).rglob('*'):
  if f.is_file()and(f.suffix in ['.kicad_pcb','.kicad_sch','.kicad_pro','.kicad_dru','.kicad_sym','.kicad_mod']or f.name in ['sym-lib-table','fp-lib-table']):files.add(f)
for n in ['finite_copper.py','native_polygon.py','source_netlist.xml']:files.add(D/'review_dependencies'/n)
names='''README.md CONTRACT.md RUN_CHECKS.md verify_manifest.py freeze_review.py verify_final.py check_candidate.py geometry_native.py source_roles.py native_contract_final.py raw_contract.py native_blocks.py anchor_policy.py anchor_regression_final.py fill_one.py refill_check.py negatives_final.py run_saved_cuts.py reference_final.py reference_check.py plane_delta_final.py plane_islands_final.py newpaths_final.py retained_reference_unions.py clock_centerline.py copper_metrics.py collinear_screen.py boundary_flag_regression.py window_policy_regression.py junction_exact_delta.py model_replay.py aggregate_checks.py proposed_full104.json proposed_obstacles.json final_verification.json final_verification_optimized.json candidate_check.json candidate_check_optimized.json source_roles.json source_roles_optimized.json final_native_contract.json final_native_contract_optimized.json raw_contract.json raw_contract_optimized.json anchor_regression.json anchor_regression_optimized.json final_drc.json final_fill_reload.json reference_checkpoint.json plane_delta_final.json plane_islands_final.json newpaths_final.json retained_reference_unions.json clock_centerline.json copper_metrics.json collinear_screen.json ordinary_layer_component_evidence.json boundary_regression.json boundary_regression_optimized.json window_policy.json window_policy_optimized.json junction_exact_delta.json junction_reversible.ndiff model_replay.json aggregate_checks.json advisory_dependencies.json'''.split()
for n in names:files.add(D/n)
for f in (D/'final_validation').iterdir():
 if f.is_file()and f.suffix in ['.json','.ndiff']:files.add(f)
rows=[]
for f in sorted(files):
 if not f.is_file():raise RuntimeError(str(f))
 rows.append({'path':str(f.relative_to(D)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
r={'status':'FROZEN_BOUNDED_STATIC_RESEARCH_CANDIDATE_FOR_INDEPENDENT_REVIEW','native':'final_candidate/mainboard_revD.kicad_pcb','native_sha256':'7522ff428329ffdac9a5ea5222c4c2b6e29e60d67fc4b31977396abac7c279d1','parent_sha256':'6882360bd2e0ace9957ef9382d0ba5c5b1f9c9cd04501f9710f9f87456ce7e08','actual_drc':[0,37,0],'scope':'Four MCU control/camera-off service physical joins; all old non-zone raw blocks exact. CAM_PWDN_UART_RX is naming alias mapped SENS_TRIG_IN, NOT validated sensor PWDN. Explicit19.00508mm new In2 conductor and filled-plane material/shared-hole changes;3363 old reference projections retain coverage, not SI/PDN/boot/service qualification. NOFAB/NOPOWER/providerNULL/JP201JP202JP301OPEN.','files':rows,'excluded':'All unselected/rejected/planning native boards, generated cut/refill boards, caches/UI.prl, transient route searches. Labeled negative/replay/model evidence is not adoptable hardware. Exact diagnostic6902 can be reconstructed only for differential evidence from the explicit junction ndiff; selected7522 is the sole offered candidate.','advisory_dependencies':json.loads((D/'advisory_dependencies.json').read_text()),'mechanics_pending_author_binding':'../reconstruction_control_service_final_mechanics_20261031_0524'}
(D/'review_manifest.json').write_text(json.dumps(r,indent=2)+'\n');print(len(rows),hashlib.sha256((D/'review_manifest.json').read_bytes()).hexdigest())
