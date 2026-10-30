import os,json,hashlib
from pathlib import Path
os.environ['XDG_CONFIG_HOME']='/tmp/mech-dvp-two-ref'
import pcbnew as p
R=Path(__file__).resolve().parent;H=R.parent/'smart_pen_next_20261028/hardware';a=H/'dvp_joint_native_candidate_1950/native/mainboard_revD.kicad_pcb';b=H/'dvp_mechanical_clearance_successor_1957/native/mainboard_revD.kicad_pcb';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if sha(a)!='184dce12e82219e5d4bb3e1f20f84cf2bc6e06c1494f5b23862f5e1978024f81'or sha(b)!='f92c7517b40466208d907d30b076ccd80d40bb3c298c162b40891f86b5070f19':raise ValueError('native pin')
def snap(path):
 b=p.LoadBoard(str(path));return{f.GetReference():{'pose':[f.GetPosition().x/1e6,f.GetPosition().y/1e6,f.GetOrientationDegrees(),f.GetLayerName()],'fp':str(f.GetFPID().GetLibNickname())+':'+str(f.GetFPID().GetLibItemName()),'value':f.GetValue(),'pads':sorted([q.GetNumber(),q.GetNetname(),q.GetPosition().x/1e6,q.GetPosition().y/1e6,q.GetSize().x/1e6,q.GetSize().y/1e6,q.GetOrientationDegrees()]for q in f.Pads())}for f in b.GetFootprints()}
x,y=snap(a),snap(b)
if len(x)!=102 or set(x)!=set(y):raise ValueError('102 reference identity')
delta={k:{'old':x[k],'new':y[k]}for k in x if x[k]!=y[k]}
if set(delta)!={'R206','J107'}:raise ValueError('unexpected delta '+str(delta))
if y['R206']['pose']!=[9,46,0,'B.Cu']or y['J107']['pose']!=[3.2,84,180,'B.Cu']:raise ValueError('pose')
if [q[2:4]for q in y['J107']['pads']]!=[[2,81.5],[2,83.9],[2,86.3]]:raise ValueError('pad geometry')
for ref in delta:
 if x[ref]['fp']!=y[ref]['fp']or x[ref]['value']!=y[ref]['value']or[q[:2]+q[4:]for q in x[ref]['pads']]!=[q[:2]+q[4:]for q in y[ref]['pads']]:raise ValueError('non-placement change')
(R/'native_identity.json').write_text(json.dumps({'predecessor_sha256':sha(a),'successor_sha256':sha(b),'native_matches_screened_combination':True,'changes':delta},indent=2)+'\n');print('PASS actual native matches exact jointly screened translations')
