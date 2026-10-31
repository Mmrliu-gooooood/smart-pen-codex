from pathlib import Path
import hashlib,difflib,json,shutil,subprocess,os
D=Path(__file__).resolve().parent;A=D/'native';B=D/'final_candidate';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();files=[str(p.relative_to(A))for p in A.rglob('*')if p.is_file()];assert len(files)==53;delta=(D/'final_validation/native_reversible.ndiff').read_text().splitlines(keepends=True);rows=[]
for name,which,source,target,expected in [('forward',2,A,B,[0,37,0]),('inverse',1,B,A,[0,41,0])]:
 O=D/'independent_replay'/name
 for rel in files:(O/rel).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source/rel,O/rel)
 (O/'mainboard_revD.kicad_pcb').write_text(''.join(difflib.restore(delta,which)));assert all(sha(O/rel)==sha(target/rel)for rel in files)
 r=subprocess.run(['kicad-cli','pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','-o',str(O/'drc.json'),str(O/'mainboard_revD.kicad_pcb')],env={**os.environ,'XDG_CONFIG_HOME':'/tmp/c698replay'},capture_output=True,text=True);(O/'drc.log').write_text(r.stdout+r.stderr);dr=json.loads((O/'drc.json').read_text());counts=[len(dr[k])for k in ['violations','unconnected_items','schematic_parity']];assert counts==expected;rows.append({'direction':name,'all53_manifest_native_files_exact':True,'pcb_sha256':sha(O/'mainboard_revD.kicad_pcb'),'actual_DRC':counts})
(D/'independent_replay.json').write_text(json.dumps(rows,indent=2))
