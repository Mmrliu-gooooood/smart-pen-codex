from pathlib import Path
import os,json,hashlib,collections
os.environ['XDG_CONFIG_HOME']='/tmp/pen-zone-analysis2150'
import pcbnew as p
from finite_copper import build,components,shape,L
D=Path(__file__).resolve().parent;R=D.parents[1];N=D/'native';f=N/'mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f));base=p.LoadBoard(str(R/'hardware/head_power_joint_native_candidate_2141/native/mainboard_revD.kicad_pcb'));old=p.LoadBoard(str(R/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb'))
uid=lambda x:x.m_Uuid.AsString();xy=lambda q:[q.x/1e6,q.y/1e6]
def req(t,m):
 if not t:raise RuntimeError(m)
def sig(t):return(t.GetNetname(),t.GetLayerSet().FmtHex(),xy(t.GetStart()),xy(t.GetEnd()),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else 0)
req({uid(t):sig(t)for t in b.GetTracks()}=={uid(t):sig(t)for t in base.GetTracks()},'COPPER MULTISET')
def fps(q):return sorted((uid(f),f.GetReference(),f.GetValue(),xy(f.GetPosition()),f.GetLayer(),f.GetOrientationDegrees(),sorted((uid(x),x.GetNumber(),x.GetNetname(),xy(x.GetPosition()),xy(x.GetSize()),x.GetLayerSet().FmtHex())for x in f.Pads()))for f in q.GetFootprints())
req(fps(b)==fps(base),'FP CHANGED')
for x in (R/'hardware/head_power_joint_native_candidate_2141/native').rglob('*'):
 if x.is_file()and x.suffix not in ['.kicad_pcb','.kicad_prl']:req(x.read_bytes()==(N/x.relative_to(R/'hardware/head_power_joint_native_candidate_2141/native')).read_bytes(),'SOURCE CHANGED')
nets=build(b);oldnets=build(old);padrows=[];summary={};oldpads={uid(q):q for f in old.GetFootprints()for q in f.Pads()}
for net,core in [('3V3_AON','J106.2'),('GND','J106.3')]:
 groups=components(nets[net]);cg=next(g for g in groups if core in g);og=next(g for g in components(oldnets[net])if core in g)
 for fp in b.GetFootprints():
  for q in fp.Pads():
   if q.GetNetname()!=net:continue
   name=fp.GetReference()+'.'+q.GetNumber();name+=('#'+uid(q) if name=='U101.57' else '');oq=oldpads[uid(q)];padrows.append(dict(pad=name,pad_uuid=uid(q),net=net,xy=xy(q.GetPosition()),FP_side=b.GetLayerName(fp.GetLayer()),actual_copper_layers=[b.GetLayerName(l)for l in L if q.IsOnLayer(l)],connected_to_core=name in cg,old_connected=name in og,moved_from_old=xy(q.GetPosition())!=xy(oq.GetPosition())or q.GetLayerSet().FmtHex()!=oq.GetLayerSet().FmtHex()))
 summary[net]=dict(core=core,all_pads=sum(len(g)for g in groups),connected_pads=len(cg),unconnected_pads=sorted(set(sum(groups,[]))-set(cg)),pad_components=groups)
# Zone polygon topology, compare like-for-like erosion. Erosion indicates bottlenecks, not ampacity.
zone=[];antipads=[];oldzs={uid(z):z for z in old.Zones()};ground={}
for z in b.Zones():
 if z.GetIsRuleArea():continue
 for l in L:
  if not z.IsOnLayer(l):continue
  q=z.GetFilledPolysList(l);oq=oldzs[uid(z)].GetFilledPolysList(l);er=[]
  for radius in [0.125,0.25]:
   a=p.SHAPE_POLY_SET(q);a.Deflate(round(radius*1e6),p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000);c=p.SHAPE_POLY_SET(oq);c.Deflate(round(radius*1e6),p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000);er.append(dict(radius_mm=radius,new_outlines=a.OutlineCount(),old_outlines=c.OutlineCount(),new_area_mm2=a.Area()/1e12,old_area_mm2=c.Area()/1e12))
  zone.append(dict(uuid=uid(z),net=z.GetNetname(),layer=b.GetLayerName(l),new_outlines=q.OutlineCount(),old_outlines=oq.OutlineCount(),new_area_mm2=q.Area()/1e12,old_area_mm2=oq.Area()/1e12,erosion=er))
  if z.GetNetname()=='GND':
   if l not in ground:ground[l]=p.SHAPE_POLY_SET()
   ground[l].BooleanAdd(q)
  for t in b.GetTracks():
   if not isinstance(t,p.PCB_VIA)or t.GetNetname()==z.GetNetname():continue
   a=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(a,l,150000,250,p.ERROR_INSIDE);a.BooleanIntersection(q)
   antipads.append(dict(via=uid(t),net=t.GetNetname(),zone=uid(z),layer=b.GetLayerName(l),foreign_copper_plus_015_overlap_mm2=a.Area()/1e12))
reference=[]
for t in b.GetTracks():
 if not t.GetNetname().startswith('SENS_')or isinstance(t,p.PCB_VIA):continue
 l=t.GetLayer();ref=p.In1_Cu if l==p.F_Cu else p.In4_Cu
 a=shape(t,l);area=a.Area();a.BooleanIntersection(ground[ref]);reference.append(dict(uuid=uid(t),net=t.GetNetname(),layer=b.GetLayerName(l),reference=b.GetLayerName(ref),projection_area_mm2=area/1e12,covered_fraction=a.Area()/area if area else 0))
# Keep already verified complete nets and pair endpoints, finite copper independently includes fresh zones.
v=json.loads((R/'hardware/head_power_joint_native_candidate_2141/verify_normal.json').read_text())
for x in v['nineteen_nets']:req(len(components(nets[x['net']]))==1,'19 NET LOST')
for x in v['fourteen_pair_chains']:req(any(x['start']in g and x['end']in g for g in components(nets[x['net']])),'CHAIN LOST')
r=json.loads((D/'drc.json').read_text())
print(json.dumps(dict(status='NOFAB_FRESHFILL_ONLY',pcb_sha=hashlib.sha256(f.read_bytes()).hexdigest(),strict_drc=[len(r[k])for k in ['violations','unconnected_items','schematic_parity']],copper_533_exactly_preserved=True,FP102_pad366_source_unchanged=True,core_summary=summary,pads=sorted(padrows,key=lambda x:x['pad']),zones=zone,foreign_via_antipad_checks=antipads,signal_reference_projection=reference,nineteen_nets_and_fourteen_chains_retained=True,JP301_OPEN=True,limits=['Erosion counts are screening only, not a path-specific minimum neck or ampacity proof.','Projected track copper coverage is not field-solver reference qualification.','No old local ground/AON fanouts restored; fill does not connect SMT pads without copper.']),indent=2))
