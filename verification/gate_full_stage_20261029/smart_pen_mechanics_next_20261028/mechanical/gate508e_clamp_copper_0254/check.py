import os,sys,json,hashlib,math
from pathlib import Path
os.environ['XDG_CONFIG_HOME']='/tmp/gate508e_clamp';os.environ['XDG_DATA_HOME']='/tmp/gate508e_clamp'
import pcbnew as p
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
R=Path(__file__).resolve().parent;src=R.parents[2]/'smart_pen_next_20261028/hardware/gate_control_output_candidate/mainboard_revD.kicad_pcb';V=A.Vector
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
if sha(src)!='508e71cbc50437cfb64a28ea8169a8511eb884f8363620e95f58773f368c5b35':raise ValueError('hash')
b=p.LoadBoard(str(src))
def polys():
 out=[]
 for z in b.Zones():
  if z.GetIsRuleArea():continue
  for l in z.GetLayerSet().Seq():
   ps=z.GetFilledPolysList(l)
   for i in range(ps.OutlineCount()):
    c=ps.Outline(i);pts=[(c.CPoint(j).x,c.CPoint(j).y)for j in range(c.PointCount())]
    out.append(dict(net=z.GetNetname(),layer=b.GetLayerName(l),pts=pts))
 return out
orig=polys();p.ZONE_FILLER(b).Fill(b.Zones());fresh=polys()
# Exact serialized point order comparison, no approximate area equivalence claim.
equal=orig==fresh
if not equal:raise ValueError('fresh polygon changes: electrical review needed')
def face(pts):
 v=[V(x/1e6,y/1e6,0)for x,y in pts];return Part.Face(Part.makePolygon(v+[v[0]]))
zones=[(v,face(v['pts']))for v in fresh]
strips=[]
for y0 in [31,81]:
 for x0,x1 in [(0,.25),(13.75,14)]:
  y1=y0+2;s=face([(x0*1e6,y0*1e6),(x1*1e6,y0*1e6),(x1*1e6,y1*1e6),(x0*1e6,y1*1e6)])
  zs=[]
  for z,f in zones:zs.append(dict(layer=z['layer'],net=z['net'],distance_mm=s.distToShape(f)[0],intersect_area_mm2=s.common(f).Area))
  bounds=[]
  for ref,items in [('track_or_via',list(b.GetTracks()))]+[(f.GetReference(),list(f.Pads()))for f in b.GetFootprints()]:
   for t in items:
    bb=t.GetBoundingBox();a,c,d,e=bb.GetX()/1e6,bb.GetY()/1e6,bb.GetRight()/1e6,bb.GetBottom()/1e6
    dx=max(a-x1,x0-d,0);dy=max(c-y1,y0-e,0);dist=math.hypot(dx,dy)
    bounds.append(dict(ref=ref,net=t.GetNetname(),layer=t.GetLayerName(),bbox_distance_lower_bound_mm=dist))
  minimum=min(v['bbox_distance_lower_bound_mm']for v in bounds)
  strips.append(dict(rect=[x0,y0,x1,y1],zones=zs,min_zone_distance_mm=min(v['distance_mm']for v in zs),min_track_pad_via_bbox_lower_bound_mm=minimum,nearest_bbox=[v for v in bounds if abs(v['bbox_distance_lower_bound_mm']-minimum)<1e-8]))
if any(v['min_zone_distance_mm']<.049999 or v['min_track_pad_via_bbox_lower_bound_mm']<=0 or any(z['intersect_area_mm2']>1e-9 for z in v['zones'])for v in strips):raise ValueError('edge intrusion or reduced margin')
out=dict(source=str(src),sha256=sha(src),cached_fresh_filled_polygon_point_lists_exactly_equal=equal,filled_polygons=len(fresh),strips=strips,status='COPPER_CLEARANCE_ONLY_NOT_CLAMP_QUALIFICATION',note='Outer outline faces omit holes conservatively; strips outside every filled outline. Pads/tracks/vias use conservative bbox lower bound, not falsely exact pad distance. No electrical DRC or fatigue qualification.')
(R/('optimized.json'if sys.flags.optimize else'results.json')).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
