from pathlib import Path
import os,json,math,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/pen-mcuclearance0109'
import pcbnew as p
from finite_copper import shape,L
D=Path(__file__).resolve().parent;R=D.parents[1];old=R/'hardware/mcu_power_ground_candidate_0043/native/mainboard_revD.kicad_pcb';new=D/'native/mainboard_revD.kicad_pcb';meta=json.loads((R/'hardware/mcu_power_ground_candidate_0043/materialization.json').read_text());uid=lambda x:x.m_Uuid.AsString();results=[]
def req(c,m):
 if not c:raise RuntimeError(m)
def circle(t):
 q=p.SHAPE_POLY_SET();q.NewOutline();c=t.GetPosition();r=t.GetDrillValue()/2
 for n in range(512):q.Append(round(c.x+r*math.cos(2*math.pi*n/512)),round(c.y+r*math.sin(2*math.pi*n/512)))
 return q
for label,f in [('rejected_old',old),('clearance_successor',new)]:
 b=p.LoadBoard(str(f));vias=[t for t in b.GetTracks()if uid(t)in meta['EP_GND_added']];rows=[];nonEP=[]
 for t in vias:
  for fp in b.GetFootprints():
   for pad in fp.Pads():
    for l in L:
     if not pad.IsOnLayer(l):continue
     raw=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(raw,l,0,100,p.ERROR_OUTSIDE);q=shape(pad,l);ov=p.SHAPE_POLY_SET();ov.BooleanIntersection(raw,q);dr=p.SHAPE_POLY_SET();dr.BooleanIntersection(circle(t),q)
     if ov.Area()>1 or dr.Area()>1:
      row={'via':uid(t),'pad':fp.GetReference()+'.'+pad.GetNumber()+'#'+uid(pad),'net':pad.GetNetname(),'layer':b.GetLayerName(l),'annulus_disk_overlap_mm2':ov.Area()/1e12,'drill_overlap_mm2':dr.Area()/1e12,'is_intended_U101_ground_EP':fp.GetReference()=='U101'and pad.GetNumber()=='57'and pad.GetNetname()=='GND'};rows.append(row)
      if not row['is_intended_U101_ground_EP']:nonEP.append(row)
 results.append({'board':label,'sha':hashlib.sha256(f.read_bytes()).hexdigest(),'actual_same_and_foreign_net_pad_overlaps':rows,'non_EP_overlaps':nonEP})
 if label=='rejected_old':req(any(x['pad'].startswith('C504.2#')and x['drill_overlap_mm2']>0 for x in nonEP),'old collision negative missing')
 else:req(not nonEP,'nonEP via overlap remains')
req(results[1]['sha']==json.loads((D/'materialization.json').read_text())['pcb_sha'],'currenthash')
print(json.dumps({'status':'LIMITED_XY_NOMINAL_SCREEN_NO_ASSEMBLY_QUALIFICATION','boards':results,'C504_complete_pad_union_XY_budget':{'center_mm':[4.25,9.75],'size_mm':[2.45,.95],'relocated_via_disk_gap_mm':.225,'relocated_drill_gap_mm':.375,'source':'unchanged native C504 two .9x.95 pads at3.475/5.025,9.75; enclosing rectangle retained, not shrunk to selected pad'},'top_EP_drill_to_copper_bbox_gap_mm':.0238,'limits':['23.8um nominal between drill and two EP copper-square edges does not establish drill/mask registration capability.','Other eight via centers remain directly in EP solder lands; hole filling/capping/tenting and voiding process require fabrication/assembly decision.','No component height/wire/thermal product certification from XY clearance.']},indent=2))
