from pathlib import Path
import os,json
os.environ['XDG_CONFIG_HOME']='/tmp/transwap0130'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];b=p.LoadBoard(str(R/'hardware/mcu_power_ground_clearance_0109/native/mainboard_revD.kicad_pcb'));L=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu];f={f.GetReference():f for f in b.GetFootprints()};s={}
for r in ['C207','C208']:s[r]=dict(value=f[r].GetValue(),package=str(f[r].GetFPID().GetLibNickname())+':'+str(f[r].GetFPID().GetLibItemName()),xy=[f[r].GetPosition().x/1e6,f[r].GetPosition().y/1e6])
f['C207'].SetPosition(p.VECTOR2I(10000000,65000000));f['C208'].SetPosition(p.VECTOR2I(2000000,65000000))
def shape(t,l,m=0):
 q=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(q,l,m,50,p.ERROR_OUTSIDE);return q
hits=[]
for r in s:
 for q in f[r].Pads():
  for t in list(b.GetTracks())+[x for ff in b.GetFootprints()if ff.GetReference()not in s for x in ff.Pads()]:
   if t.GetNetname()==q.GetNetname():continue
   for l in L:
    if t.IsOnLayer(l)and q.IsOnLayer(l):
     a=shape(q,l,150000);a.BooleanIntersection(shape(t,l))
     if a.Area()>1:hits.append(dict(pad=r+'.'+q.GetNumber(),other=t.m_Uuid.AsString(),net=t.GetNetname(),layer=b.GetLayerName(l)))
(D/'cap_swap_compare.json').write_text(json.dumps(dict(source=s,proposed_swap_xy_only=True,foreign_net_conflicts=hits,native_saved=False),indent=2)+'\n');print(json.dumps(hits,indent=2))
