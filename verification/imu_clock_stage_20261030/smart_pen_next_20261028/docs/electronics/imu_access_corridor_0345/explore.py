import sys,json
from pathlib import Path
D=Path(__file__).resolve().parent; R=D.parents[2]
sys.path.insert(0,str(R/'hardware/imu_power_return_candidate_0333'))
import geometry as g
p=g.p;F=p.F_Cu;A='3V3_AON';G='GND'
fps={f.GetReference():f for f in g.b.GetFootprints()}
fps['J107'].SetPosition(g.V((3.2,88)))
# fresh all-pad cache after explicit in-memory move
print('j107 pads',[(q.GetNumber(),g.xy(q),q.GetNetname()) for q in fps['J107'].Pads()])
def tr(n,pts,w=.25):return [g.track(n,F,a,b,w)for a,b in zip(pts,pts[1:])]
items=[]
items+=tr(A,[(4.7625,81.25),(5.2,81.25),(5.72,80.7)])
items+=tr(A,[(4.7625,81.75),(5.2,81.75),(5.72,82)])
items+=tr(A,[(3.2375,81.75),(2.65,81.75),(2.65,82.25),(3.2375,82.25)])
items+=tr(A,[(2.65,81.75),(2.65,79.9)])+[g.via(A,(2.65,79.9))]
# Ground outward then bottom horizontal shared bus, one west access via.
items+=tr(G,[(4.7625,82.25),(5.1,82.25),(5.1,83.3),(2.65,83.3)])
items+=tr(G,[(4.7625,82.75),(5.1,82.75)])
items+=tr(G,[(3.75,82.7625),(3.75,83.3)])
items+=tr(G,[(4.25,82.7625),(4.25,83.3)])
items+=[g.via(G,(2.65,83.3))]
items+=tr(G,[(6.68,80.7),(7,80.7),(7,83.3),(5.1,83.3)])
items+=tr(G,[(6.68,82),(7,82)])
items+=tr(G,[(6.25,84.5),(7,84.5),(7,83.3)])
# common AON access branch follows top across outside MEMS body
items+=tr(A,[(2.65,79.9),(5.72,79.9),(5.72,80.7)])
items+=tr(A,[(5.72,80.7),(5.72,82)])
items+=tr(A,[(2.65,80.0),(1.8,80.0),(1.8,84.5),(4.35,84.5)])
print(json.dumps({'objects':len(items),'errors':g.errors(items)},indent=2))
