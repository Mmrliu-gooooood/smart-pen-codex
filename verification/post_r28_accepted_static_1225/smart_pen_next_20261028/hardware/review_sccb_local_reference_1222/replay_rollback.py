from pathlib import Path
import subprocess,sys,os,shutil,hashlib,json
D=Path(__file__).resolve().parent;BASE=D.parent/'control_envelope_native_1051/native';N=D/'native';REPLAY=D/'native_replay';BACK=D/'native_rollback'
def req(c,m):
 if not c:raise RuntimeError(m)
def inventory(root):return{str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest()for f in root.rglob('*')if f.is_file()}
r=subprocess.run([sys.executable]+(['-O']if sys.flags.optimize else[])+[str(D/'materialize.py')],env={**os.environ,'GROUND_NATIVE_OUTPUT':str(REPLAY)},capture_output=True,text=True);(D/'replay_materialize.log').write_text(r.stdout+r.stderr);req(r.returncode==0,'replay success');a=inventory(N);c=inventory(REPLAY);req(a==c,'full native replay byte equality')
base=inventory(BASE);patch=[];changes=[]
for rel in sorted(set(base)|set(a)):
 if base.get(rel)==a.get(rel):continue
 old=BASE/rel;new=N/rel;cmd=['diff','-u','--label','a/'+rel,'--label','b/'+rel,str(old)if old.exists()else'/dev/null',str(new)if new.exists()else'/dev/null'];r=subprocess.run(cmd,capture_output=True,text=True);req(r.returncode==1,'text delta '+rel);patch.append(r.stdout);changes.append({'path':rel,'before_sha256':base.get(rel),'after_sha256':a.get(rel)})
(D/'native_forward.patch').write_text(''.join(patch));shutil.copytree(N,BACK,dirs_exist_ok=True)
r=subprocess.run(['patch','-R','-p1','--batch','--remove-empty-files','-i',str(D/'native_forward.patch')],cwd=BACK,capture_output=True,text=True);(D/'rollback_patch.log').write_text(r.stdout+r.stderr);req(r.returncode==0,'actual inverse patch');req(inventory(BACK)==base,'full inverse patch restores exact old native')
r=subprocess.run(['kicad-cli','pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','-o',str(D/'rollback_drc.json'),str(BACK/'mainboard_revD.kicad_pcb')],env={**os.environ,'XDG_CONFIG_HOME':'/tmp/schmittrollback0745'},capture_output=True,text=True);(D/'rollback_drc.log').write_text(r.stdout+r.stderr);d=json.loads((D/'rollback_drc.json').read_text());counts=[len(d[k])for k in['violations','unconnected_items','schematic_parity']];req(counts==[0,69,0],'actual rollback CLI')
print(json.dumps({'replay_all_native_files_byte_equal':True,'replay_native_file_count':len(a),'inverse_patch_actual_applied':True,'rollback_all_native_files_byte_equal':True,'rollback_native_file_count':len(base),'rollback_DRC_unconnected_parity':counts,'changes':changes,'note':'Real inverse unified diff applied to candidate tree, not replacing PCB with baseline copy; no upstream source edited'},indent=2))
