from pathlib import Path
import os,sys,json,hashlib,uuid,shutil,subprocess
os.environ['XDG_CONFIG_HOME']='/tmp/ground0807-test'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[2];BASE=R/'hardware/camera_schmitt_native_0745/native';N=D/'selected20_native';m=json.loads((D/'selected20.json').read_text());shutil.copytree(BASE,N,dirs_exist_ok=True);f=N/'mainboard_revD.kicad_pcb';raw=f.read_text();b=p.LoadBoard(str(f));blocks=[];mapping=[]
for i,r in enumerate(m['new']):
 u=str(uuid.uuid5(uuid.NAMESPACE_URL,'ground0807/'+json.dumps(r,sort_keys=True)));net=b.GetNetcodeFromNetname('GND');a=r['a'];z=r['b'];mapping.append(dict(uuid=u,**r))
 if r['type']=='track':blk=f'(segment(start {a[0]} {a[1]})(end {z[0]} {z[1]})(width {r["width"]})(layer "{r["layer"]}")(net {net})(uuid "{u}"))\n'
 else:blk=f'(via(at {a[0]} {a[1]})(size {r["width"]})(drill {r["drill"]})(layers "F.Cu" "B.Cu")(net {net})(uuid "{u}"))\n'
 blocks.append(blk)
i=raw.rfind(')');f.write_text(raw[:i]+''.join(blocks)+raw[i:]);b=p.LoadBoard(str(f));b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));from finite_copper import build,components,shape,L
from native_polygon import native_fractured_once
a=p.LoadBoard(str(BASE/f.name));an=build(a);bn=build(b);oldcore=next(c for c in components(an['GND'])if'J106.3'in c);newcore=next(c for c in components(bn['GND'])if'J106.3'in c);targets=[r['pad']for r in m['rows']if r['accepted_finite_geometry']];prior={}
for net,ns in an.items():
 ac=components(ns);bc=components(bn[net]);prior[net]=all(any(set(x)<=set(y)for y in bc)for x in ac)
r=subprocess.run(['kicad-cli','pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','-o',str(D/'selected20_drc.json'),str(f)],capture_output=True,text=True);(D/'selected20_drc.log').write_text(r.stdout+r.stderr);d=json.loads((D/'selected20_drc.json').read_text());counts=[len(d[k])for k in['violations','unconnected_items','schematic_parity']]
# Actual new annuli versus every actual pad, same net included; courtyard overlaps separate gate.
ts={t.m_Uuid.AsString():t for t in b.GetTracks()};pad_overlap=[];courtyard=[]
for fp in b.GetFootprints():fp.BuildCourtyardCaches()
for row in mapping:
 if row['type']!='via':continue
 t=ts[row['uuid']]
 for fp in b.GetFootprints():
  for pad in fp.Pads():
   for l in L:
    if not pad.IsOnLayer(l):continue
    q=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(q,l,0,50,p.ERROR_OUTSIDE);q.BooleanIntersection(shape(pad,l))
    if q.Area()>1:pad_overlap.append({'via_for':row['target_pad'],'pad':fp.GetReference()+'.'+pad.GetNumber(),'layer':b.GetLayerName(l)})
  for l in[p.F_CrtYd,p.B_CrtYd]:
   q=shape(t,p.F_Cu);q.BooleanIntersection(fp.GetCourtyard(l))
   if q.Area()>1:courtyard.append({'via_for':row['target_pad'],'xy':row['a'],'ref':fp.GetReference(),'layer':b.GetLayerName(l),'overlap_mm2':q.Area()/1e12})
planes=[];before={};after={}
for board,store in [(a,before),(b,after)]:
 for z in board.Zones():
  if not z.GetIsRuleArea():store.setdefault(z.GetLayer(),p.SHAPE_POLY_SET()).BooleanAdd(native_fractured_once(z.GetFilledPolysList(z.GetLayer())))
losses=[]
for t in a.GetTracks():
 if isinstance(t,p.PCB_VIA)or t.GetNetname()in['GND','3V3_AON','SENS_VIO_1V8']:continue
 for ref in {p.F_Cu:[p.In1_Cu],p.B_Cu:[p.In4_Cu],p.In3_Cu:[p.In2_Cu,p.In4_Cu]}.get(t.GetLayer(),[]):
  x=p.SHAPE_POLY_SET();x.BooleanIntersection(shape(t,t.GetLayer()),before[ref]);y=p.SHAPE_POLY_SET();y.BooleanIntersection(shape(t,t.GetLayer()),after[ref]);x.BooleanSubtract(y)
  if x.Area()>10000:losses.append({'track':t.m_Uuid.AsString(),'net':t.GetNetname(),'reference':b.GetLayerName(ref),'loss_mm2':x.Area()/1e12})
for l in before:
 x=p.SHAPE_POLY_SET(before[l]);y=p.SHAPE_POLY_SET(after[l]);x.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000);y.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000);planes.append({'layer':b.GetLayerName(l),'before_025_erosion_components':x.OutlineCount(),'after_025_erosion_components':y.OutlineCount()})
result={'status':'PLANNING_SCRATCH_ONLY_NOT_FORMAL_SUCCESSOR_NOFAB_NOPOWER','base_sha256':hashlib.sha256((BASE/f.name).read_bytes()).hexdigest(),'scratch_pcb_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'actual_DRC_unconnected_parity':counts,'base_ground_core':oldcore,'new_ground_core':newcore,'targets_actually_core':[x for x in targets if x in newcore],'targets_not_core':[x for x in targets if x not in newcore],'all_old_components_preserved':prior,'actual_new_via_pad_overlaps_all_layers_same_net_included':pad_overlap,'courtyard_open_DFM_gates':courtyard,'old_signal_additional_reference_losses':losses,'reference_plane_erosion':planes,'mapping':mapping,'no_old_copper_or_source_or_footprint_edit':True,'mechanical_boundary':'0745 board outline and footprints unchanged; no shaft/3D/tenting/RF approval'}
(D/'selected20_result.json').write_text(json.dumps(result,indent=2)+'\n');print('DRC',counts,'GNDcore',len(newcore),'newtargets',len(result['targets_actually_core']),'pad_overlap',len(pad_overlap),'ref_loss',len(losses),'courtyard',len(courtyard))
