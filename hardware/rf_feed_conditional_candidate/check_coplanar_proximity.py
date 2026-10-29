#!/usr/bin/env python3
import os,pathlib,json
os.environ['XDG_CONFIG_HOME']='/tmp/pen-rf-check/config'
import pcbnew as p
D=pathlib.Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'mainboard_revD.kicad_pcb'))
def poly(x):
 q=p.SHAPE_POLY_SET();x.TransformShapeToPolygon(q,p.F_Cu,0,500,p.ERROR_OUTSIDE);return q
obs=[]
for f in b.GetFootprints():
 for pad in f.Pads():
  if pad.IsOnLayer(p.F_Cu)and pad.GetNetname()=='GND':obs.append((f.GetReference()+'.'+pad.GetNumber(),poly(pad)))
for t in b.GetTracks():
 if t.GetNetname()=='GND'and(isinstance(t,p.PCB_VIA)or t.GetLayer()==p.F_Cu):obs.append((t.m_Uuid.AsString(),poly(t)))
rows=[]
for t in b.GetTracks():
 if t.GetNetname()not in ['RF_SIP','RF_ANT']:continue
 q=poly(t)
 for name,other in obs:
  if not q.Collide(other,p.FromMM(.35)):continue
  lo=0;hi=p.FromMM(.35)
  for _ in range(20):
   mid=(lo+hi)//2
   if q.Collide(other,mid):hi=mid
   else:lo=mid+1
  rows.append(dict(rf_uuid=t.m_Uuid.AsString(),ground_object=name,estimated_copper_gap_mm=hi/1e6))
print(json.dumps(dict(status='LOCAL_NONUNIFORM_TRANSITIONS_REQUIRE_EM_OR_VNA_REVIEW',screening_gap_mm=.35,manufacturer_limit=False,nearby_ground=rows,do_not_claim_entire_feed_50ohm=True),indent=2,sort_keys=True))
