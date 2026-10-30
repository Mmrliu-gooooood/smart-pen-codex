import os,json,hashlib
from pathlib import Path
os.environ['XDG_CONFIG_HOME']='/tmp/bench_context';os.environ['XDG_DATA_HOME']='/tmp/bench_context'
import pcbnew as p
R=Path(__file__).resolve().parent;H=Path('/workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware');src=H/'gate_input_local_routing/mainboard_revD.kicad_pcb';old=H/'imu_compact_0402_placement/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(src));a=p.LoadBoard(str(old))
def phys(b):return {f.GetReference():dict(x=f.GetPosition().x,y=f.GetPosition().y,angle=f.GetOrientationDegrees(),layer=f.GetLayerName(),value=f.GetValue(),id=str(f.GetFPID().GetLibItemName()),pads=sorted((q.GetNumber(),q.GetPosition().x,q.GetPosition().y,q.GetNetname(),q.GetSize().x,q.GetSize().y,q.GetOrientationDegrees())for q in f.Pads()))for f in b.GetFootprints()}
x=phys(a);y=phys(b)
# compare geometry/pad identities, value fields are separate source metadata
value_deltas={k:[x[k]['value'],y[k]['value']]for k in x if x[k]['value']!=y[k]['value']}
for v in [x,y]:
 for k in v:v[k].pop('value')
if x!=y:raise ValueError('physical snapshot differs')
# Conservative track/pad/via XY bounding-box screen at actual edge-contact strips; masks/material still unqualified.
contacts=[]
for z in [45,95]:
 for side,(x0,x1)in [('L',(0,.25)),('R',(13.75,14))]:
  y0,y1=127-z-1,127-z+1;hits=[]
  for ref,items in [('tracks_vias',list(b.GetTracks()))]+[(f.GetReference(),list(f.Pads()))for f in b.GetFootprints()]:
   for q in items:
    bb=q.GetBoundingBox();xx0,xx1,yy0,yy1=bb.GetX()/1e6,bb.GetRight()/1e6,bb.GetY()/1e6,bb.GetBottom()/1e6
    if min(x1,xx1)>max(x0,xx0) and min(y1,yy1)>max(y0,yy0):hits.append([ref,str(q.GetLayerName()),q.GetNetname()])
  contacts.append(dict(penZ=z,side=side,PCB_rect=[x0,y0,x1,y1],track_pad_via_bbox_hits=hits))
zone_edges=[]
cached_zone_summary=[dict(rule=z.GetIsRuleArea(),layers=[b.GetLayerName(l)for l in z.GetLayerSet().Seq()],filled=z.IsFilled())for z in b.Zones()]
p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard(str(R/'fresh_filled_audit_ONLY.kicad_pcb'),b)
for zo in b.Zones():
 if zo.GetIsRuleArea():continue
 for layer in [p.F_Cu,p.B_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu]:
  if not zo.IsOnLayer(layer):continue
  poly=zo.GetFilledPolysList(layer)
  for i in range(poly.OutlineCount()):
   l=poly.Outline(i);pts=[(l.CPoint(j).x/1e6,l.CPoint(j).y/1e6)for j in range(l.PointCount())]
   zone_edges.append(dict(net=zo.GetNetname(),layer=b.GetLayerName(layer),points=pts))
(R/'native_contract.json').write_text(json.dumps(dict(source=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),prior_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),all_102_footprint_geometry_pad_identity_equal=True,value_field_changes=value_deltas,count=len(y),contacts=contacts,zone_polygons=zone_edges,cached_source_zone_summary=cached_zone_summary,fresh_filled_audit_sha256=hashlib.sha256((R/'fresh_filled_audit_ONLY.kicad_pcb').read_bytes()).hexdigest()),indent=2)+'\n')
print('identical',len(y),'contacts',contacts,'zones',len(zone_edges))
