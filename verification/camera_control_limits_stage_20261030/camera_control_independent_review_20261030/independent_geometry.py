from pathlib import Path
import pcbnew as p,json,hashlib,sys
R=Path('/workspace/scratch/fe148e758944/smart_pen_next_20261028');D=R/'hardware/camera_isolation_control_native_0628';O=Path(__file__).resolve().parent
boards={k:p.LoadBoard(str(R/'hardware'/v/'native/mainboard_revD.kicad_pcb'))for k,v in [('historical','pressure_joint_native_0433'),('parent','imu_control_native_0522'),('candidate','camera_isolation_control_native_0628')]}
def norm(raw):
 if any(raw.HoleCount(i)for i in range(raw.OutlineCount())):raise RuntimeError('not raw fractured')
 n=p.SHAPE_POLY_SET(raw);n.Unfracture()
 for a,b in [(n,raw),(raw,n)]:
  q=p.SHAPE_POLY_SET();q.BooleanSubtract(a,b)
  if q.Area()>1e8:raise RuntimeError('normalization area changed')
 return n
def fill(b,l):
 n=p.SHAPE_POLY_SET()
 for z in b.Zones():
  if not z.GetIsRuleArea()and z.GetLayer()==l:n.BooleanAdd(norm(z.GetFilledPolysList(l)))
 return n
def loss(a,b,t,l):
 s=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(s,t.GetLayer(),0,250,p.ERROR_INSIDE)
 x=p.SHAPE_POLY_SET();x.BooleanIntersection(s,fill(a,l));y=p.SHAPE_POLY_SET();y.BooleanIntersection(s,fill(b,l));x.BooleanSubtract(y);return x.Area()/1e12
tracks={k:{t.m_Uuid.AsString():t for t in b.GetTracks()}for k,b in boards.items()};old=tracks['parent'];new=tracks['candidate'];added=set(new)-set(old)
rows=[]
for uid,l in [('f50aa801-170b-4339-91cd-374a0faa5f75',p.In1_Cu),('eba5b185-27fd-57f9-b1a5-37b4fa4d4ec8',p.In2_Cu),('eba5b185-27fd-57f9-b1a5-37b4fa4d4ec8',p.In4_Cu)]:
 t=new[uid];rows.append(dict(uuid=uid,net=t.GetNetname(),layer=boards['candidate'].GetLayerName(l),new_loss=loss(boards['parent'],boards['candidate'],t,l),historical_loss=loss(boards['historical'],boards['parent'],t,l)))
# Separately parse balanced root objects, preserving every raw old copper/footprint block.
def blocks(s):
 depth=0;quote=False;esc=False;start=0
 for i,c in enumerate(s):
  if quote:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':quote=False
  elif c=='"':quote=True
  elif c=='(':
   depth+=1
   if depth==2:start=i
  elif c==')':
   if depth==2:yield s[start:i+1]
   depth-=1
import re
get=lambda path:{re.search(r'\(uuid "([^"]+)"\)',b).group(1):b for b in blocks(path.read_text())if b.startswith(('(segment','(via','(footprint'))}
a=get(R/'hardware/imu_control_native_0522/native/mainboard_revD.kicad_pcb');b=get(D/'native/mainboard_revD.kicad_pcb');changed=[u for u in a if b.get(u)!=a[u]]
result={'reference_geometry':rows,'old_raw_copper_and_footprints_changed':changed,'added':len(added),'removed':len(set(old)-set(new)),'added_vias':sum(isinstance(new[u],p.PCB_VIA)for u in added),'jumpers':{f.GetReference():f.GetValue()for f in boards['candidate'].GetFootprints()if f.GetReference()in['JP201','JP202','JP301']},'method':'Separate review implementation, actual filled polygons, guarded one-shot Unfracture, no exclusion masks or enlarged holes; raw balanced-block old geometry comparison.'}
if changed or len(added)!=209:raise RuntimeError(result)
print(json.dumps(result,indent=2))
