from pathlib import Path
import sys,json,math,os
os.environ['XDG_CONFIG_HOME']='/tmp/imu-control-reference0522'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));from finite_copper import shape
from native_polygon import native_fractured_once
old=p.LoadBoard(str(R/'hardware/pressure_joint_native_0433/native/mainboard_revD.kicad_pcb'));new=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));uid='eba5b185-27fd-57f9-b1a5-37b4fa4d4ec8';t=next(t for t in new.GetTracks()if t.m_Uuid.AsString()==uid);oldtrack=next(t for t in old.GetTracks()if t.m_Uuid.AsString()==uid)
if(t.GetStart()!=oldtrack.GetStart()or t.GetEnd()!=oldtrack.GetEnd()or t.GetWidth()!=oldtrack.GetWidth()):raise RuntimeError('clock changed')
def planes(board):
 out={}
 for z in board.Zones():
  if not z.GetIsRuleArea():out.setdefault(z.GetLayer(),p.SHAPE_POLY_SET()).BooleanAdd(native_fractured_once(z.GetFilledPolysList(z.GetLayer())))
 return out
a=planes(old);b=planes(new);vias={t.m_Uuid.AsString():t for t in new.GetTracks()if isinstance(t,p.PCB_VIA)}
def chains(q):
 for oi in range(q.OutlineCount()):
  yield q.COutline(oi)
  for hi in range(q.HoleCount(oi)):yield q.Hole(oi,hi)
def intervals(q,x,ylo,yhi):
 ys=[float(ylo),float(yhi)]
 for ch in chains(q):
  pts=[ch.CPoint(i)for i in range(ch.PointCount())]
  for A,B in zip(pts,pts[1:]+pts[:1]):
   if A.x==B.x:
    if x==A.x:ys.extend([max(ylo,min(yhi,A.y)),max(ylo,min(yhi,B.y))])
   elif min(A.x,B.x)<=x<=max(A.x,B.x):
    y=A.y+(x-A.x)*(B.y-A.y)/(B.x-A.x)
    if ylo<y<yhi:ys.append(y)
 ys=sorted(set(ys));out=[]
 for lo,hi in zip(ys,ys[1:]):
  if hi-lo<1:continue
  if q.Contains(p.VECTOR2I(x,round((lo+hi)/2))):
   if out and abs(out[-1][1]-lo)<1:out[-1][1]=hi
   else:out.append([lo,hi])
 return[[x/1e6,y/1e6]for x,y in out]
def bounds(q):
 if q.Area()<=1:return None
 z=q.BBox();return[z.GetX()/1e6,z.GetY()/1e6,z.GetWidth()/1e6,z.GetHeight()/1e6]
def hole_records(poly,region):
 out=[]
 for oi in range(poly.OutlineCount()):
  for hi in range(poly.HoleCount(oi)):
   h=p.SHAPE_POLY_SET();h.AddOutline(poly.Hole(oi,hi));j=p.SHAPE_POLY_SET();j.BooleanIntersection(h,region)
   if j.Area()<=1:continue
   ch=h.COutline(0);out.append({'bbox_mm':bounds(h),'area_mm2':h.Area()/1e12,'containing_via_centers':[{'uuid':u,'net':v.GetNetname(),'xy':[v.GetPosition().x/1e6,v.GetPosition().y/1e6]}for u,v in vias.items()if h.Contains(v.GetPosition())],'contour_xy_mm':[[ch.CPoint(i).x/1e6,ch.CPoint(i).y/1e6]for i in range(ch.PointCount())]})
 return out
rows=[];x=t.GetStart().x;ylo=min(t.GetStart().y,t.GetEnd().y);yhi=max(t.GetStart().y,t.GetEnd().y)
for l in[p.In2_Cu,p.In4_Cu]:
 strip=shape(t,t.GetLayer());oldcov=p.SHAPE_POLY_SET();oldcov.BooleanIntersection(strip,a[l]);newcov=p.SHAPE_POLY_SET();newcov.BooleanIntersection(strip,b[l]);extra=p.SHAPE_POLY_SET();extra.BooleanSubtract(oldcov,newcov);og=p.SHAPE_POLY_SET(strip);og.BooleanSubtract(a[l]);ng=p.SHAPE_POLY_SET(strip);ng.BooleanSubtract(b[l]);ci=intervals(extra,x,ylo,yhi);full=intervals(ng,x,ylo,yhi);oldi=intervals(og,x,ylo,yhi)
 projected=[]
 for oi in range(extra.OutlineCount()):
  bb=extra.UnitSet(oi).BBox();projected.append([bb.GetY()/1e6,(bb.GetY()+bb.GetHeight())/1e6])
 projected.sort();merged=[]
 for lo,hi in projected:
  if merged and lo<=merged[-1][1]:merged[-1][1]=max(merged[-1][1],hi)
  else:merged.append([lo,hi])
 rows.append({'reference_layer':new.GetLayerName(l),'additional_uncovered_strip_mm2':extra.Area()/1e12,'additional_bbox_mm':bounds(extra),'additional_crosses_clock_centerline':bool(ci),'additional_centerline_intervals_y_mm':ci,'longest_additional_centerline_gap_mm':max((hi-lo for lo,hi in ci),default=0),'parent_full_centerline_uncovered_y_mm':oldi,'candidate_full_centerline_uncovered_y_mm':full,'longest_candidate_full_centerline_gap_mm':max((hi-lo for lo,hi in full),default=0),'additional_uncovered_band_projected_y_intervals_mm':merged,'longest_band_projected_additional_gap_mm':max((hi-lo for lo,hi in merged),default=0),'actual_native_holes_intersecting_additional_loss':hole_records(b[l],extra)})
# Negative/positive controls for centerline interval predicate, including a central hole.
def rectangle(x0,y0,x1,y1):
 q=p.SHAPE_POLY_SET();q.NewOutline()
 for xx,yy in[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]:q.Append(round(xx*1e6),round(yy*1e6))
 return q
control=rectangle(4.175,80,4.325,80.1);positive=intervals(control,x,ylo,yhi)
if len(positive)!=1 or abs(positive[0][1]-positive[0][0]-.1)>1e-8:raise RuntimeError('centerline positive control')
control.BooleanSubtract(rectangle(4.225,79.9,4.275,80.2));negative=intervals(control,x,ylo,yhi)
if negative:raise RuntimeError('centerline central-clear negative control')
physical=json.loads((D/'physical.json').read_text());affected=set(v['uuid']for r in rows for h in r['actual_native_holes_intersecting_additional_loss']for v in h['containing_via_centers']);returns=[v for v in physical['new_vias']if v['uuid']in affected]
print(json.dumps({'status':'MEASURED_NATIVE_REFERENCE_DELTA_PENDING_SI_REVIEW','unchanged_clock_track':{'uuid':uid,'net':t.GetNetname(),'layer':new.GetLayerName(t.GetLayer()),'a':[t.GetStart().x/1e6,t.GetStart().y/1e6],'b':[t.GetEnd().x/1e6,t.GetEnd().y/1e6],'width_mm':t.GetWidth()/1e6},'rows':rows,'centerline_predicate_controls':{'positive':positive,'central_clear_negative':negative},'new_vias_in_affected_holes_with_actual_GND_return_observations':returns,'limits':['This supersedes the ideal/model zero-loss reference estimate','Projected area alone neither qualifies nor disqualifies signal integrity','Centerline interval intersection uses actual native polygon edges, with1nm database coordinate resolution','All old pad connectivity is preserved but does not establish return impedance, EMI or timing','No automatic route movement or relaxed threshold; pending independent review']},indent=2))
