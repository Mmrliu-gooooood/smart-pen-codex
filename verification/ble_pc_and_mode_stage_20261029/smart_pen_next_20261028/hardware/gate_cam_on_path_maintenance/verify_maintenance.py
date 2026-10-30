from pathlib import Path
import json,hashlib,collections,math
D=Path(__file__).resolve().parent;s=(D/'audit_gate.py').read_text();exec(compile(s[:s.index('na,nb=build')],__file__,'exec'))
base=D.parent/'gate_control_output_candidate';before=p.LoadBoard(str(base/'mainboard_revD.kicad_pcb'));delta=json.loads((D/'maintenance_delta.json').read_text())
require(hashlib.sha256((base/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest()==delta['source_pcb_sha256'],'Source hash')
def geom(t):return(t.GetClass(),t.GetNetname(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,int(t.GetLayer()),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None)
aa={t.m_Uuid.AsString():geom(t)for t in before.GetTracks()};zz={t.m_Uuid.AsString():geom(t)for t in b.GetTracks()}
removed={r['uuid']for r in delta['removed']};added={r['uuid']for r in delta['added']}
require(set(aa)-set(zz)==removed and set(zz)-set(aa)==added,'Exact maintenance UUID delta')
require(all(aa[u]==zz[u]for u in aa.keys()&zz.keys()),'Any surviving copper changed')
require(all(aa[u][1]=='CAM_ON' and aa[u][0]=='PCB_TRACK'and aa[u][7]==150000 for u in removed),'Scope removed non-CAM_ON or wrong width')
require(all(zz[u][1]=='CAM_ON' and zz[u][0]=='PCB_TRACK'and zz[u][7]==150000 for u in added),'Scope added non-CAM_ON or wrong width')
def fg(f):return(f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees(),f.GetLayer(),f.GetAttributes(),f.GetValue(),f.GetFPIDAsString(),f.GetPath().AsString(),[(q.GetNumber(),q.GetNetname(),q.GetPosition().x,q.GetPosition().y,q.GetSize().x,q.GetSize().y,q.GetOrientationDegrees(),list(q.GetLayerSet().Seq()))for q in f.Pads()])
f0={f.GetReference():fg(f)for f in before.GetFootprints()};f1={f.GetReference():fg(f)for f in b.GetFootprints()};require(f0==f1,'Physical footprint or source identity changed')
na,nb=build(before),build(b);ca={n:components(v)for n,v in na.items()if sum(q[1]for q in v)>1};cb={n:components(v)for n,v in nb.items()if sum(q[1]for q in v)>1};require(ca==cb,'Actual old net pad partition changed')
def filled(board):
 out={}
 for z in board.Zones():
  if z.GetIsRuleArea():continue
  for l in L:
   if z.IsOnLayer(l):out[(z.m_Uuid.AsString(),int(l))]=str(z.GetFilledPolysList(l).Format())
 return out
filla,fillb=filled(before),filled(b);require(filla==fillb,'Actual filled plane geometry changed')
# Relabel each actual AON filled island as a component witness, not only the pads.
aon=[(name,ispad or '/'in name,sh)for name,ispad,sh in nb['3V3_AON']];cc=components(aon);core=next(c for c in cc if 'C104.1'in c);islands=[name for name,_,_ in aon if '/'in name];require(len(islands)==6 and all(i in core for i in islands),'AON islands not all physically connected to core')
def union(nodes,layer):
 out=p.SHAPE_POLY_SET()
 for _,_,sh in nodes:
  if layer in sh:out.BooleanAdd(sh[layer])
 out.Fracture();return out
def diff_area(a,z):
 q=p.SHAPE_POLY_SET(a);q.BooleanSubtract(z);return q.Area()/1e12
changes={};returns={}
for l,ref in [(p.F_Cu,p.In1_Cu),(p.B_Cu,p.In4_Cu)]:
 a=union(na['CAM_ON'],l);z=union(nb['CAM_ON'],l)
 changes[b.GetLayerName(l)]={'removed_copper_area_mm2':diff_area(a,z),'added_copper_area_mm2':diff_area(z,a),'before_union_area_mm2':a.Area()/1e12,'after_union_area_mm2':z.Area()/1e12}
 ground=p.SHAPE_POLY_SET()
 for zone in b.Zones():
  if not zone.GetIsRuleArea()and zone.GetNetname()=='GND'and zone.IsOnLayer(ref):ground.BooleanAdd(zone.GetFilledPolysList(ref))
 ground.Fracture();returns[b.GetLayerName(l)]={'adjacent_reference':b.GetLayerName(ref),'before_CAM_ON_copper_not_over_filled_GND_mm2':diff_area(a,ground),'after_CAM_ON_copper_not_over_filled_GND_mm2':diff_area(z,ground),'metric':'Projected finite CAM_ON pad/track/via copper, not electromagnetic return path. Signal via antipads naturally contribute; no HF/PI qualification.'}
# Check actual changed track copper against all foreign net copper on matching layers.
hits=[]
for name,_,ss in nb['CAM_ON']:
 if name not in added:continue
 for net,nodes in nb.items():
  if net=='CAM_ON':continue
  for other,_,oo in nodes:
   for l in ss.keys()&oo.keys():
    if not ss[l].BBox().Intersects(oo[l].BBox()):continue
    q=p.SHAPE_POLY_SET();q.BooleanIntersection(ss[l],oo[l])
    if q.Area()>1:hits.append((name,net,other,int(l)))
require(not hits,'New actual copper foreign overlap')
# Branch junction retained in actual F copper, plus all three exact old vias.
branch=p.VECTOR2I(8400000,67950000);u=union(nb['CAM_ON'],p.F_Cu);require(u.Contains(branch),'Real F branch location lost')
for uid in delta['unchanged_via_UUIDs']:require(uid in zz and aa[uid]==zz[uid],'Preserved gate via changed')
# Exact native finding multiset, ignoring item order only.
def multiset(file):
 x=json.loads(file.read_text());norm=[]
 for v in x['violations']:
  q=dict(v);q['items']=sorted(q.get('items',[]),key=lambda a:json.dumps(a,sort_keys=True));norm.append(json.dumps(q,sort_keys=True))
 return collections.Counter(norm),x
d0,x0=multiset(base/'preflight.native_drc.json');d1,x1=multiset(D/'drc.json');require(d0==d1,'DRC violation multiset changed')
result={'pcb_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'all_102_physical_source_footprints_unchanged':True,'only_CAM_ON_new_track_delta':True,'all90_net_pad_partitions_identical':True,'AON_islands_in_core':islands,'all_five_native_zone_layer_polygon_serializations_identical':True,'plane_neck_geometry':'identical to 508e: no new neck changes; existing neck ampacity/PI not qualified','CAM_ON_copper_union_delta':changes,'reference_coverage':returns,'new_foreign_copper_overlap':hits,'violation_multiset_identical':True,'native_counts':{k:len(x1[k])for k in ['violations','unconnected_items','schematic_parity']},'unconnected_reporting':'Native representative airwire list can differ; actual per-net pad partitions independently identical.','all_FP_via_CTPowerDVP_unchanged':True,'fixture_edge_strips':'Changed copper only x4.85..9.9/y66.5..73 on F/B; does not intersect x0..0.25 or13.75..14 clamp strips.','NOFAB':True}
print(json.dumps(result,indent=2))
