from pathlib import Path
import os,json
os.environ['XDG_CONFIG_HOME']='/tmp/pen-region2150'
import pcbnew as p
from finite_copper import build,L
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));nets=build(b)
def reachable(nodes,start,omit=None):
 nodes=[x for x in nodes if x[0]!=omit];seen={start};todo=[start];lookup={x[0]:x for x in nodes}
 while todo:
  _,_,si=lookup[todo.pop()]
  for name,_,sj in nodes:
   if name in seen:continue
   for l in si.keys()&sj.keys():
    if not si[l].BBox().Intersects(sj[l].BBox()):continue
    q=p.SHAPE_POLY_SET();q.BooleanIntersection(si[l],sj[l])
    if q.Area()>1:seen.add(name);todo.append(name);break
 return sorted(seen)
core={}
for net,start in [('GND','J106.3'),('3V3_AON','J106.2')]:
 reach=reachable(nets[net],start);core[net]=dict(all_reachable_objects=reach,connected_zone_fragments=[n for n in reach if '/'in n])
core['GND_negative_remove_corevia']=dict(omitted='70f2443f-1a5f-5292-8401-7d0f5fea8c0a',connected_zone_fragments=[n for n in reachable(nets['GND'],'J106.3','70f2443f-1a5f-5292-8401-7d0f5fea8c0a')if '/'in n])
if not core['GND']['connected_zone_fragments']or core['GND_negative_remove_corevia']['connected_zone_fragments']:raise RuntimeError('corevia counterfactual failed')
regions=[]
for z in b.Zones():
 if z.GetIsRuleArea():continue
 for l in L:
  if not z.IsOnLayer(l):continue
  a=p.SHAPE_POLY_SET(z.GetFilledPolysList(l));a.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000);regions.append(dict(zone=z.m_Uuid.AsString(),layer=b.GetLayerName(l),erosion_radius_mm=.25,fragments=[dict(area_mm2=a.UnitSet(i).Area()/1e12,bbox_mm=[a.UnitSet(i).BBox().GetX()/1e6,a.UnitSet(i).BBox().GetY()/1e6,a.UnitSet(i).BBox().GetWidth()/1e6,a.UnitSet(i).BBox().GetHeight()/1e6])for i in range(a.OutlineCount())]))
print(json.dumps(dict(core_regions=core,half_mm_erosion_fragments=regions,note='Non-mutating finite-copper counterfactual, not native negative board. Erosion satellites can be local nubs; fragmentation alone is not proof a load-path neck is below 0.5 mm.'),indent=2))
