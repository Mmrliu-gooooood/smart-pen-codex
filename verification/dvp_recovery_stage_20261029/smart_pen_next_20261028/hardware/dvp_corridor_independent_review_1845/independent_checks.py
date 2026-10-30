from pathlib import Path
import os,json,hashlib,collections,math,sys
os.environ.update(XDG_CONFIG_HOME='/tmp/corridor-review/config',XDG_CACHE_HOME='/tmp/corridor-review/cache',XDG_DATA_HOME='/tmp/corridor-review/data')
import pcbnew as p
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D/'reproduction'))
from copper_geometry import shape
B=D.parent/'j202_low_speed_reference_candidate/native';C=D/'reproduction/native'
a=p.LoadBoard(str(B/'mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(C/'mainboard_revD.kicad_pcb'))
def req(v,m):
 if not v:raise RuntimeError(m)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
req(sha(C/'mainboard_revD.kicad_pcb')=='1d844c44e62e75a01f82e743e87b084707dd50d78afa94c9513aea6b034f5d94','PCB_HASH')
source=[]
for f in B.rglob('*'):
 if f.is_file() and f.suffix in ['.kicad_sch','.kicad_pro','.kicad_dru']:
  q=C/f.relative_to(B);req(sha(f)==sha(q),'SOURCE');source.append(str(f.relative_to(B)))
# Independent full DRC multiset, retaining all report details except ordering.
x,y=[json.loads((D/f).read_text()) for f in ['fresh_baseline_drc.json','fresh_candidate_drc.json']]
def key(v):
 z=dict(v);z['items']=sorted(z.get('items',[]),key=lambda q:json.dumps(q,sort_keys=True));return json.dumps(z,sort_keys=True)
diffs={}
for k in ['violations','unconnected_items','schematic_parity']:
 u,v=[collections.Counter(map(key,w[k])) for w in [x,y]];diffs[k]={'counts':[sum(u.values()),sum(v.values())],'added':[json.loads(z)for z in(v-u).elements()],'removed':[json.loads(z)for z in(u-v).elements()]}
req(diffs['violations']['counts']==[17,17] and not diffs['violations']['added'] and not diffs['violations']['removed'],'VIOLATION_DELTA')
req(diffs['unconnected_items']['counts']==[21,21] and diffs['schematic_parity']['counts']==[0,0],'COUNTS')
old={t.m_Uuid.AsString():t for t in a.GetTracks()};new=[t for t in b.GetTracks() if t.m_Uuid.AsString() not in old]
via_rows=[];ground=[t for t in b.GetTracks()if isinstance(t,p.PCB_VIA)and t.GetNetname()=='GND']
for t in new:
 if isinstance(t,p.PCB_VIA):
  pos=t.GetPosition();row={'net':t.GetNetname(),'x_mm':pos.x/1e6,'y_mm':pos.y/1e6,'ring_mm':t.GetWidth(p.F_Cu)/1e6,'drill_mm':t.GetDrillValue()/1e6,'nearest_ground_via_center_mm':min(math.hypot(pos.x-g.GetPosition().x,pos.y-g.GetPosition().y)for g in ground)/1e6}
  if .05<=pos.x/1e6<=13.95:row['coarse_connector_body_top_gap_mm']=90-(pos.y+t.GetWidth(p.F_Cu)/2)/1e6
  via_rows.append(row)
# Native actual pad positions, not visual CAD placeholders.
ports={f.GetReference():[{'number':q.GetNumber(),'net':q.GetNetname(),'x_mm':q.GetPosition().x/1e6,'y_mm':q.GetPosition().y/1e6}for q in f.Pads()]for f in b.GetFootprints()if f.GetReference()in ['J103','J301']}
# New trace finite-width area outside nearest designated reference, drill-subtracted.
def circle(x,y,r):
 q=p.SHAPE_POLY_SET();q.NewOutline()
 for i in range(256):q.Append(round(x+r*math.cos(2*math.pi*i/256)),round(y+r*math.sin(2*math.pi*i/256)))
 return q
holes=p.SHAPE_POLY_SET()
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):q=t.GetPosition();holes.BooleanAdd(circle(q.x,q.y,t.GetDrillValue()/2))
refs={}
for l in [p.In1_Cu,p.In4_Cu]:
 q=p.SHAPE_POLY_SET()
 for z in b.Zones():
  if not z.GetIsRuleArea() and z.IsOnLayer(l):q.BooleanAdd(z.GetFilledPolysList(l))
 rr=p.SHAPE_POLY_SET();rr.BooleanSubtract(q,holes);refs[l]=rr
missing={};lengths=collections.defaultdict(float)
for t in new:
 if isinstance(t,p.PCB_VIA):continue
 lengths[t.GetNetname()]+=t.GetLength()/1e6
 l=t.GetLayer();req(l in[p.F_Cu,p.In3_Cu,p.B_Cu],'LAYER');ref=p.In1_Cu if l==p.F_Cu else p.In4_Cu
 q=shape(t,l);m=p.SHAPE_POLY_SET();m.BooleanSubtract(q,refs[ref]);missing.setdefault(t.GetNetname(),p.SHAPE_POLY_SET()).BooleanAdd(m)
out={'scope':'INDEPENDENT_STATIC_ONLY_NOFAB','sources_equal':source,'full_drc_delta':diffs,'new_vias':via_rows,'new_trace_length_mm':dict(lengths),'new_trace_union_area_without_nearest_reference_mm2':{n:q.Area()/1e12 for n,q in missing.items()},'actual_ports':ports,'note':'Reference area and nearest ground-via center do not establish dynamic return impedance or EMI. Body gap is only coarse nominal y90 screen, not toleranced connector underside.'}
(D/'independent_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
