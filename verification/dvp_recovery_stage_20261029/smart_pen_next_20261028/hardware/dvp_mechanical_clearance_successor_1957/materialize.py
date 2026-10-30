from pathlib import Path
import os,json,shutil,hashlib,sys
os.environ['XDG_CONFIG_HOME']='/tmp/pen-native1950-config'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];S=D.parent/'dvp_joint_native_candidate_1950/native';N=Path(sys.argv[2]).resolve()if len(sys.argv)==3 and sys.argv[1]=='--replay-dir'else D/'native'
if N.exists():raise RuntimeError('REFUSE OVERWRITE')
if hashlib.sha256((S/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest()!='184dce12e82219e5d4bb3e1f20f84cf2bc6e06c1494f5b23862f5e1978024f81':raise RuntimeError('INPUT SHA')
shutil.copytree(S,N,ignore=shutil.ignore_patterns('*.kicad_prl'));b=p.LoadBoard(str(N/'mainboard_revD.kicad_pcb'));fs={f.GetReference():f for f in b.GetFootprints()}
changes={}
for ref,x,y in [('R206',9,46),('J107',3.2,84)]:
 f=fs[ref];old=[f.GetPosition().x/1e6,f.GetPosition().y/1e6];f.SetPosition(p.VECTOR2I(round(x*1e6),round(y*1e6)));changes[ref]={'before_xy':old,'after_xy':[x,y],'side':f.GetLayerName(),'angle':f.GetOrientationDegrees()}
p.SaveBoard(str(N/'mainboard_revD.kicad_pcb'),b)
sha=hashlib.sha256((N/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest()
if N==D/'native':
 delta=json.loads((R/'docs/electronics/dvp_joint_feasibility_1942/placement_delta.json').read_text())
 for r,c in changes.items():delta[r]['after']['xy']=c['after_xy']
 (D/'selected_6ref_delta_from_7d197.json').write_text(json.dumps(delta,indent=2)+'\n');(D/'two_ref_delta_from_184dce.json').write_text(json.dumps(changes,indent=2)+'\n')
else:
 if sha!=hashlib.sha256((D/'native/mainboard_revD.kicad_pcb').read_bytes()).hexdigest():raise RuntimeError('REPLAY SHA')
print(json.dumps({'pcb_sha256':sha,'changes':changes,'status':'NOFAB_PENDING_FULL_SYSTEM'},indent=2))
