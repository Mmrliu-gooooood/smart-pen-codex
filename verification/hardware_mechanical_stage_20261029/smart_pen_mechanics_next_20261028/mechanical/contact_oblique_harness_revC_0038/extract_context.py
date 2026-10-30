import os,json,hashlib
from pathlib import Path
os.environ['XDG_CONFIG_HOME']='/tmp/contact_context'
import pcbnew as p
R=Path(__file__).resolve().parent;H=Path('/workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware');src=H/'imu_compact_0402_placement/mainboard_revD.kicad_pcb';baseline=H/'mainboard_input_imu_power_routing/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(src));old=p.LoadBoard(str(baseline));allowed=['C501','C502','C503','R501'];parts=[]
def physical(board):
 return {f.GetReference():dict(x=f.GetPosition().x,y=f.GetPosition().y,angle=f.GetOrientationDegrees(),side=f.GetLayerName(),value=f.GetValue(),fp=str(f.GetFPID().GetLibItemName()),pads=sorted((q.GetNumber(),q.GetNetname(),q.GetPosition().x,q.GetPosition().y)for q in f.Pads()))for f in board.GetFootprints()}
a=physical(old);c=physical(b)
if {k:v for k,v in a.items()if k not in allowed}!={k:v for k,v in c.items()if k not in allowed}:raise ValueError('unexpected physical footprint delta')
for f in b.GetFootprints():
 if f.GetReference()not in allowed:continue
 bs=[]
 for g in list(f.Pads())+list(f.GraphicalItems()):
  if isinstance(g,p.PAD)or(isinstance(g,p.PCB_SHAPE)and g.GetLayer()in[p.F_Fab,p.B_Fab]):
   q=g.GetBoundingBox();bs.append([q.GetX()/1e6,q.GetY()/1e6,q.GetRight()/1e6,q.GetBottom()/1e6])
 ref=f.GetReference();height=1.45
 if ref in ['C501','C502','C503']:
  L,W,height=(1.05,.55,.70) if ref!='C503' else(2.2,1.45,1.60)
  x=f.GetPosition().x/1e6;y=f.GetPosition().y/1e6;bs.append([x-L/2,y-W/2,x+L/2,y+W/2])
 parts.append(dict(ref=f.GetReference(),side=f.GetLayerName(),bounds=[min(v[0]for v in bs),min(v[1]for v in bs),max(v[2]for v in bs),max(v[3]for v in bs)],height_assumption=height))
(R/'context_imu_snapshot.json').write_text(json.dumps(dict(source=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),baseline_source=str(baseline),baseline_sha256=hashlib.sha256(baseline.read_bytes()).hexdigest(),allowed_deltas=allowed,all_other_footprints_equal=True,count=len(c),parts=parts),indent=2))
