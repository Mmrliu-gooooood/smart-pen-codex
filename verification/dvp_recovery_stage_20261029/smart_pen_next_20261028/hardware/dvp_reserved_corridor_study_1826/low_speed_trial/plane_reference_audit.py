from pathlib import Path
import os,json,math
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache';os.environ['XDG_DATA_HOME']='/tmp/rf-independent/data'
import pcbnew as p
from copper_geometry import shape,L
D=Path(__file__).resolve().parent;a=p.LoadBoard(str(D.parents[1]/'j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));plans={};rawplans={}
def circle(x,y,r):
 q=p.SHAPE_POLY_SET();q.NewOutline()
 for i in range(256):q.Append(round(x+r*math.cos(i*2*math.pi/256)),round(y+r*math.sin(i*2*math.pi/256)))
 return q
for ver,board in [('before',a),('after',b)]:
 holes=p.SHAPE_POLY_SET()
 for t in board.GetTracks():
  if isinstance(t,p.PCB_VIA):v=t.GetPosition();holes.BooleanAdd(circle(v.x,v.y,t.GetDrillValue()/2))
 for l in[p.In1_Cu,p.In2_Cu,p.In4_Cu]:
  q=p.SHAPE_POLY_SET()
  for z in board.Zones():
   if not z.GetIsRuleArea()and z.IsOnLayer(l):q.BooleanAdd(z.GetFilledPolysList(l))
  rawplans[ver,l]=q;rr=p.SHAPE_POLY_SET();rr.BooleanSubtract(q,holes);plans[ver,l]=rr
plane={}
for l in[p.In1_Cu,p.In2_Cu,p.In4_Cu]:
 old,new=plans['before',l],plans['after',l];lost=p.SHAPE_POLY_SET();lost.BooleanSubtract(old,new);gain=p.SHAPE_POLY_SET();gain.BooleanSubtract(new,old);plane[b.GetLayerName(l)]={'old_drill_corrected_area_mm2':old.Area()/1e12,'new_drill_corrected_area_mm2':new.Area()/1e12,'lost_mm2':lost.Area()/1e12,'gained_mm2':gain.Area()/1e12}
oldids={t.m_Uuid.AsString():t for t in a.GetTracks()};newloss={};rows=[];lossunions={}
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA)or t.m_Uuid.AsString()not in oldids or t.GetLayer()not in[p.F_Cu,p.In3_Cu,p.B_Cu]:continue
 ref=p.In1_Cu if t.GetLayer()==p.F_Cu else p.In4_Cu;q=shape(t,t.GetLayer());old=p.SHAPE_POLY_SET();old.BooleanIntersection(q,plans['before',ref]);now=p.SHAPE_POLY_SET();now.BooleanIntersection(q,plans['after',ref]);lost=p.SHAPE_POLY_SET();lost.BooleanSubtract(old,now)
 if lost.Area()>1e4:
  item={'net':t.GetNetname(),'uuid':t.m_Uuid.AsString(),'layer':b.GetLayerName(t.GetLayer()),'a':[t.GetStart().x/1e6,t.GetStart().y/1e6],'z':[t.GetEnd().x/1e6,t.GetEnd().y/1e6],'new_reference_loss_mm2':lost.Area()/1e12};rows.append(item);lossunions.setdefault(t.GetNetname(),p.SHAPE_POLY_SET()).BooleanAdd(lost);newloss[t.GetNetname()]=newloss.get(t.GetNetname(),0)+lost.Area()/1e12
rf=[z for z in b.Zones()if z.GetIsRuleArea()and z.GetZoneName().startswith('RF_')];intr=[]
for t in b.GetTracks():
 if t.m_Uuid.AsString()in oldids:continue
 for z in rf:
  for l in L if isinstance(t,p.PCB_VIA)else[t.GetLayer()]:
   ix=p.SHAPE_POLY_SET();ix.BooleanIntersection(shape(t,l),z.Outline())
   if ix.Area()>1:intr.append({'uuid':t.m_Uuid.AsString(),'rule':z.GetZoneName(),'layer':b.GetLayerName(l),'area_mm2':ix.Area()/1e12})
out={'status':'FRESH_FILL_AND_ALL_THROUGH_DRILL_CORRECTED_REFERENCE_SCREEN_NOT_PI_EMI_QUALIFICATION','note':'Both old/new filled planes subtract every through drill; new ground via bore is not falsely counted as solid copper. Existing signal copper identities checked separately. Threshold for numerical area noise 1e-8 mm2.','plane_delta':plane,'old_track_new_reference_loss_by_net':newloss,'old_track_new_reference_unique_union_mm2':{n:q.Area()/1e12 for n,q in lossunions.items()},'affected_old_tracks':rows,'new_RF_region_intrusions':intr};(D/'plane_reference_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))

if intr:raise RuntimeError('RF_INTRUSION')
