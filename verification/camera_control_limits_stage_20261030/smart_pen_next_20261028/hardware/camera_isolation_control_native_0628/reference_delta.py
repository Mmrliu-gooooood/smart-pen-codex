from pathlib import Path
import sys,json,os
os.environ['XDG_CONFIG_HOME']='/tmp/isoref0628'
import pcbnew as p
import math
D=Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));from finite_copper import shape
from native_polygon import native_fractured_once
old=p.LoadBoard(str(D.parent/'imu_control_native_0522/native/mainboard_revD.kicad_pcb'));new=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'))
def planes(b):
 out={}
 for z in b.Zones():
  if not z.GetIsRuleArea():out.setdefault(z.GetLayer(),p.SHAPE_POLY_SET()).BooleanAdd(native_fractured_once(z.GetFilledPolysList(z.GetLayer())))
 return out
A=planes(old);B=planes(new)
def ring(c):return[[c.CPoint(i).x/1e6,c.CPoint(i).y/1e6]for i in range(c.PointCount())]
def intervals(q,a,b):
 ts=[0.,1.];dx=b[0]-a[0];dy=b[1]-a[1]
 def cross(u,v):return u[0]*v[1]-u[1]*v[0]
 for oi in range(q.OutlineCount()):
  for ch in [q.COutline(oi)]+[q.Hole(oi,j)for j in range(q.HoleCount(oi))]:
   pts=ring(ch)
   for c,d in zip(pts,pts[1:]+pts[:1]):
    ex=d[0]-c[0];ey=d[1]-c[1];den=cross((dx,dy),(ex,ey));cx=c[0]-a[0];cy=c[1]-a[1]
    if abs(den)<1e-14:
     if abs(cross((cx,cy),(dx,dy)))<1e-12:
      for v in [c,d]:
       t=((v[0]-a[0])*dx+(v[1]-a[1])*dy)/(dx*dx+dy*dy)
       if 0<t<1:ts.append(t)
     continue
    t=cross((cx,cy),(ex,ey))/den;u=cross((cx,cy),(dx,dy))/den
    if 0<t<1 and -1e-10<=u<=1+1e-10:ts.append(t)
 ts=sorted(set(ts));out=[]
 for lo,hi in zip(ts,ts[1:]):
  if (hi-lo)*math.hypot(dx,dy)<1e-6:continue
  v=(hi+lo)/2
  if q.Contains(p.VECTOR2I(round((a[0]+v*dx)*1e6),round((a[1]+v*dy)*1e6))):out.append([lo,hi])
 return out
def bounds(q):
 if q.Area()<=1:return None
 b=q.BBox();return[b.GetX()/1e6,b.GetY()/1e6,b.GetWidth()/1e6,b.GetHeight()/1e6]
vias=[t for t in new.GetTracks()if isinstance(t,p.PCB_VIA)];out=[]
for uid,refs in [('f50aa801-170b-4339-91cd-374a0faa5f75',[p.In1_Cu]),('eba5b185-27fd-57f9-b1a5-37b4fa4d4ec8',[p.In2_Cu,p.In4_Cu])]:
 t=next(t for t in new.GetTracks()if t.m_Uuid.AsString()==uid);a=[t.GetStart().x/1e6,t.GetStart().y/1e6];b=[t.GetEnd().x/1e6,t.GetEnd().y/1e6];strip=shape(t,t.GetLayer())
 for l in refs:
  x=p.SHAPE_POLY_SET();x.BooleanIntersection(strip,A[l]);y=p.SHAPE_POLY_SET();y.BooleanIntersection(strip,B[l]);loss=p.SHAPE_POLY_SET();loss.BooleanSubtract(x,y);holes=[]
  for oi in range(B[l].OutlineCount()):
   for hi in range(B[l].HoleCount(oi)):
    h=p.SHAPE_POLY_SET();h.AddOutline(B[l].Hole(oi,hi));j=p.SHAPE_POLY_SET();j.BooleanIntersection(h,loss)
    if j.Area()<=1:continue
    holes.append({'bbox_mm':bounds(h),'contour':ring(h.COutline(0)),'via_centers':[{'uuid':v.m_Uuid.AsString(),'net':v.GetNetname(),'xy':[v.GetPosition().x/1e6,v.GetPosition().y/1e6]}for v in vias if h.Contains(v.GetPosition())]})
  og=p.SHAPE_POLY_SET(strip);og.BooleanSubtract(A[l]);ng=p.SHAPE_POLY_SET(strip);ng.BooleanSubtract(B[l]);extra=intervals(loss,a,b)
  out.append({'track':uid,'net':t.GetNetname(),'a':a,'b':b,'width':t.GetWidth()/1e6,'reference':new.GetLayerName(l),'loss_mm2':loss.Area()/1e12,'loss_bbox':bounds(loss),'loss_contours':[ring(loss.COutline(i))for i in range(loss.OutlineCount())],'parent_centerline_gap_intervals_fraction':intervals(og,a,b),'new_centerline_gap_intervals_fraction':intervals(ng,a,b),'additional_centerline_loss_length_mm':sum(hi-lo for lo,hi in extra)*math.dist(a,b),'holes':holes})
# General line predicate controls, independent of selected route direction.
sq=p.SHAPE_POLY_SET();sq.NewOutline()
for x,y in[(.4,.4),(.6,.4),(.6,.6),(.4,.6)]:sq.Append(round(x*1e6),round(y*1e6))
if abs(sum(hi-lo for lo,hi in intervals(sq,[0,0],[1,1]))-.2)>1e-10:raise RuntimeError('positive')
if intervals(sq,[0,1],[.1,1]):raise RuntimeError('negative')
print(json.dumps({'status':'ACTUAL_NATIVE_REFERENCE_GATES_NOT_SI_PASS','rows':out,'inherited_clock_edge_loss_each_plane_mm2':0.0017414094705,'controls_pass':True,'limits':['New CAM_ON edge projection loss is real and retained, not masked by ideal circles','Existing IMU clock merged-hole/reference loss remains inherited unchanged','Hole contour and centerline continuity are not signal-integrity qualification']},indent=2))
