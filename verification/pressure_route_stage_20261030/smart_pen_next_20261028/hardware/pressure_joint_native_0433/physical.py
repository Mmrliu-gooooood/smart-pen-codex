from pathlib import Path
import os,sys,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/imu-physical0405';D=Path(__file__).resolve().parent;R=D.parents[1]
sys.path.insert(0,str(R/'hardware/imu_power_return_candidate_0333'));import geometry as g
sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));from native_polygon import native_fractured_once
p=g.p;m=json.loads((D/'materialization.json').read_text());g.b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));alltracks={g.desc(t):t for t in g.b.GetTracks()};g.old=[t for u,t in alltracks.items()if u not in m['added']];new=[alltracks[u]for u in m['added']];g.pads=[pad for f in g.b.GetFootprints()for pad in f.Pads()];g.cache.clear();g.outline=p.SHAPE_POLY_SET();g.b.GetBoardPolygonOutlines(g.outline)
def req(c,m):
 if not c:raise RuntimeError(m)
e=g.errors(new);req(not e,'native all finite clearance')
fps={f.GetReference():f for f in g.b.GetFootprints()};req(fps['R503'].GetValue()=='47k 1%','R503');req(fps['JP301'].GetValue()=='OPEN / DO NOT BRIDGE','JP301OPEN')
for f in fps.values():f.BuildCourtyardCaches()
cts=[]
for i,t in enumerate(new):
 if isinstance(t,p.PCB_VIA):
  for ref,f in fps.items():
   for l in [p.F_CrtYd,p.B_CrtYd]:
    a=g.shape(t,p.F_Cu);a.BooleanIntersection(f.GetCourtyard(l))
    if a.Area()>1:cts.append({'index':i,'ref':ref,'side':g.b.GetLayerName(l),'overlap_mm2':a.Area()/1e12})
print(json.dumps({'native_geometry_errors':e,'new_via_courtyard_intersections':cts,'scope':'courtyard intersections are DFM review gates, not clearance waivers','JP301':'OPEN'},indent=2))
