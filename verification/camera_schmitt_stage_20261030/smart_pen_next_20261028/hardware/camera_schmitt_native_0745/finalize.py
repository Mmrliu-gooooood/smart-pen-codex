from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;R=D.parents[1]
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def req(c,m):
 if not c:raise RuntimeError(m)
comparisons={}
for name in ['verify','physical','negative']:
 comparisons[name]=json.loads((D/(name+'.json')).read_text())==json.loads((D/(name+'_optimized.json')).read_text());req(comparisons[name],'normal optimized '+name)
mat=json.loads((D/'materialization.json').read_text());req(sha(D/'native/mainboard_revD.kicad_pcb')==mat['pcb_sha256'],'actual final PCB')
for name in ['verify','physical']:
 d=json.loads((D/(name+'.json')).read_text());req(d.get('pcb_sha256',d.get('pcb_sha'))==mat['pcb_sha256'],'matching output PCB')
checked=[]
for rel in ['hardware/camera_isolation_control_native_0628','hardware/camera_schmitt_source_0744','docs/electronics/camera_safeoff_addendum_0719','docs/electronics/camera_schmitt_candidate_0730']:
 q=R/rel;m=json.loads((q/'manifest.json').read_text());bad=[e['path']for e in m['files']if sha(q/e['path'])!=e['sha256']];req(not bad,'frozen '+rel);checked.append({'directory':rel,'files_rehashed':len(m['files']),'manifest_sha256':sha(q/'manifest.json'),'mismatches':bad})
provider=R.parent/'smart_pen_app_pipeline_20261028/firmware/application_idf/main/board_provider_absent.c';req('return 0;'in provider.read_text(),'provider absent')
r=json.loads((D/'replay_rollback.json').read_text());req(r['replay_all_native_files_byte_equal']and r['rollback_all_native_files_byte_equal'],'replay rollback')
(D/'final_checks.json').write_text(json.dumps({'pcb_sha256':mat['pcb_sha256'],'normal_optimized_results_identical':comparisons,'frozen_inputs_rehashed':checked,'provider_NULL':True,'provider_sha256':sha(provider),'actual_reverse_patch_and_replay_pass':True,'visual_review':'local_after.png inspected; NC isolated; supply/bypass/control routing coherent; courtyard vias remain DFM gate','status':'AUTHOR_VERIFIED_EXPERIMENT_INDEPENDENT_REVIEW_PENDING_NOFAB_NOPOWER'},indent=2)+'\n')
deps=['hardware/translator_domain_candidate_0130/finite_copper.py','hardware/translator_domain_candidate_0130/native_polygon.py','hardware/pressure_pullup_revision_0318/materialize.py','hardware/camera_isolation_control_native_0628/geometry_native.py','hardware/camera_isolation_control_native_0628/materialization.json','hardware/camera_schmitt_source_0744/handoff.json','hardware/camera_schmitt_source_0744/build.py']
(D/'dependencies.json').write_text(json.dumps({'files':[{'path':x,'sha256':sha(R/x)}for x in deps if(R/x).exists()],'frozen_input_manifests':checked,'toolchain':'KiCad9 pcbnew via /usr/bin/python3; kicad-cli; GNU patch/diff; local source symbol/footprint sources pinned in their manifests'},indent=2)+'\n')
excluded={'manifest.json','trial.kicad_pcb','trimmed.kicad_pcb','local_before.png','local_view.py'};files=[]
for f in sorted(D.rglob('*')):
 if not f.is_file():continue
 rel=f.relative_to(D)
 if '__pycache__'in rel.parts or rel.name in excluded:continue
 if rel.parts[0]in ['native_replay','native_rollback']:continue
 if rel.parts[0]=='native_negative'and rel.name not in['drc.json','drc.log']:continue
 files.append({'path':str(rel),'bytes':f.stat().st_size,'sha256':sha(f)})
(D/'manifest.json').write_text(json.dumps({'status':'AUTHOR_VERIFIED_EXPERIMENT_INDEPENDENT_REVIEW_PENDING_NOFAB_NOPOWER','pcb_sha256':mat['pcb_sha256'],'excluded_regenerable_test_trees':['native_replay','native_rollback','native_negative/* native copies (only real DRC reports included)'],'excluded_scratch':['trial.kicad_pcb','trimmed.kicad_pcb','local_before.png','local_view.py','__pycache__'],'files':files},indent=2)+'\n')
print('manifest',sha(D/'manifest.json'),'files',len(files),'bytes',sum(x['bytes']for x in files))
