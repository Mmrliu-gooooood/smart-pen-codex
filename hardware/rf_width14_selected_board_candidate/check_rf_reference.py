#!/usr/bin/env python3
import os,pathlib,json,hashlib,math
os.environ['XDG_CONFIG_HOME']='/tmp/pen-rf-check/config'
import pcbnew as p
D=pathlib.Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'mainboard_revD.kicad_pcb'))
ref=p.SHAPE_POLY_SET()
for z in b.Zones():
 if not z.GetIsRuleArea()and z.GetNetname()=='GND'and z.GetLayer()==p.In1_Cu:ref.BooleanAdd(z.GetFilledPolysList(p.In1_Cu))
# Actual filled reference—not outline. 0.35 mm side envelope is a conservative
# 3*h layout screening assumption (h=.1164), NOT manufacturer RF qualification.
rows=[];bad=[]
for t in b.GetTracks():
 if t.GetNetname()not in ['RF_SIP','RF_ANT']:continue
 if isinstance(t,p.PCB_VIA):raise RuntimeError('RF feed unexpectedly changes layers')
 a,c=t.GetStart(),t.GetEnd();terminal=min(a.y,c.y)<0
 q=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(q,p.F_Cu,0,500,p.ERROR_OUTSIDE)
 if terminal:
  if t.GetNetname()!='RF_ANT' or abs(a.x-p.FromMM(9.5))>1 or abs(c.x-p.FromMM(9.5))>1 or min(a.y,c.y)<p.FromMM(-1.9) or max(a.y,c.y)>0:raise RuntimeError('Unapproved radiator feed intrusion')
  rows.append(dict(uuid=t.m_Uuid.AsString(),type='unreferenced_radiator_transition_not_50ohm',length_mm=t.GetLength()/1e6));continue
 # Feed's round endpoint at y=0 protrudes into the explicitly unreferenced terminal.
 limit=p.SHAPE_POLY_SET();limit.NewOutline()
 for xx,yy in [(0,0),(12,0),(12,95),(0,95)]:limit.Append(p.FromMM(xx),p.FromMM(yy))
 clipped=p.SHAPE_POLY_SET();clipped.BooleanIntersection(q,limit)
 r=p.SHAPE_POLY_SET();r.BooleanSubtract(clipped,ref)
 guard=p.SHAPE_POLY_SET(q);guard.Inflate(p.FromMM(.35),p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000)
 rr=p.SHAPE_POLY_SET();rr.BooleanSubtract(guard,ref)
 row=dict(uuid=t.m_Uuid.AsString(),length_mm=t.GetLength()/1e6,width_mm=t.GetWidth()/1e6,unsupported_trace_area_mm2=r.Area()/1e12,unsupported_guard_area_mm2=rr.Area()/1e12)
 rows.append(row)
 if r.Area()>1:bad.append(row)
out=dict(status='REFERENCE_GEOMETRY_SCREEN_ONLY_NOFAB',stackup_contract_sha256=hashlib.sha256((D/'stackup_contract_snapshot.json').read_bytes()).hexdigest(),rows=rows,unsupported_trace_segments=len(bad),rf_qualified=False)
(D/'reference_screen.json').write_text(json.dumps(out,indent=2))
if bad:raise RuntimeError('Unsupported RF trace segments '+str(len(bad)))
print(json.dumps(out,indent=2))
