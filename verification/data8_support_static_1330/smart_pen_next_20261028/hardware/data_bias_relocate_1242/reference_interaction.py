from pathlib import Path
import os,sys,json,shutil,hashlib,math
os.environ['XDG_CONFIG_HOME']='/tmp/data1242interaction'
import pcbnew as p
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'translator_domain_candidate_0130'));from native_polygon import native_fractured_once
from finite_copper import shape
m=json.loads((D/'materialization.json').read_text());b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));tracks=list(b.GetTracks());signal_vias={r['uuid']:r for r in m['mapping']if r['type']=='via'and r['net'].startswith('CAM_D')};uid=lambda t:t.m_Uuid.AsString();sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def planes(board):
 out={}
 for l in [p.In1_Cu,p.In4_Cu]:
  q=p.SHAPE_POLY_SET()
  for z in board.Zones():
   if not z.GetIsRuleArea()and z.GetLayer()==l:
    if z.GetNetname()!='GND':raise RuntimeError('GND reference only')
    q.BooleanAdd(native_fractured_once(z.GetFilledPolysList(l)))
  out[l]=q
 return out
actual=planes(b);results=[];keepers=[b];fillers=[]
for net in ['CAM_D2','CAM_D3','CAM_D4','CAM_D6']:
 N=D/'reference_counterfactuals'/net/'native';shutil.copytree(D/'native',N,dirs_exist_ok=True);f=N/'mainboard_revD.kicad_pcb';q=p.LoadBoard(str(f));keepers.append(q);fillers.append(p.ZONE_FILLER(q));fillers[-1].Fill(q.Zones());p.SaveBoard(str(f),q)
 if sha(f)!=m['pcb_sha256']:raise RuntimeError('matched-project baseline refill differs '+net)
 ts=list(q.GetTracks());keepers.append(ts);remove=[u for u,r in signal_vias.items()if r['net']!=net]
 for t in ts:
  if uid(t)in remove:q.Remove(t)
 fillers.append(p.ZONE_FILLER(q));fillers[-1].Fill(q.Zones());p.SaveBoard(str(f),q);cf=planes(q)
 for l,ref in [(p.F_Cu,p.In1_Cu),(p.B_Cu,p.In4_Cu),(p.In3_Cu,p.In4_Cu)]:
  projection=p.SHAPE_POLY_SET()
  for t in tracks:
   if uid(t)in m['added']and not isinstance(t,p.PCB_VIA)and t.GetNetname()==net and t.GetLayer()==l:projection.BooleanAdd(shape(t,l))
  if not projection.OutlineCount():continue
  before=p.SHAPE_POLY_SET();before.BooleanSubtract(projection,actual[ref]);after=p.SHAPE_POLY_SET();after.BooleanSubtract(projection,cf[ref]);recovered=p.SHAPE_POLY_SET();recovered.BooleanSubtract(before,after)
  results.append({'net':net,'layer':b.GetLayerName(l),'reference':b.GetLayerName(ref),'actual_uncovered_mm2':before.Area()/1e12,'counterfactual_own_plus_inherited_uncovered_mm2':after.Area()/1e12,'incremental_missing_due_other_new_signal_vias_mm2':recovered.Area()/1e12,'removed_neighbor_signal_vias':remove,'counterfactual_sha256':sha(f),'baseline_matched_project_refill_byte_equal':True})
# Exact actual local hole size and physical nearest existing/new ground-via distance; not impedance or an acceptance limit.
holes=[]
for ref,plane in actual.items():
 for i in range(plane.OutlineCount()):
  for j in range(plane.HoleCount(i)):
   h=p.SHAPE_POLY_SET();h.AddOutline(plane.Hole(i,j));vs=[t for t in tracks if isinstance(t,p.PCB_VIA)and uid(t)in signal_vias and h.Contains(t.GetPosition())]
   if len({t.GetNetname()for t in vs})<2:continue
   bb=h.BBox();holes.append({'reference':b.GetLayerName(ref),'area_mm2':h.Area()/1e12,'bbox_mm':[bb.GetX()/1e6,bb.GetY()/1e6,bb.GetRight()/1e6,bb.GetBottom()/1e6],'signal_vias':[{'uuid':uid(t),'net':t.GetNetname(),'xy_mm':[t.GetPosition().x/1e6,t.GetPosition().y/1e6]}for t in vs]})
nearest=[];gnds=[t for t in tracks if isinstance(t,p.PCB_VIA)and t.GetNetname()=='GND']
for t in tracks:
 if uid(t)not in signal_vias:continue
 v=min(gnds,key=lambda v:math.dist([t.GetPosition().x,t.GetPosition().y],[v.GetPosition().x,v.GetPosition().y]));nearest.append({'signal_via':uid(t),'net':t.GetNetname(),'nearest_GND_via':uid(v),'nearest_GND_xy_mm':[v.GetPosition().x/1e6,v.GetPosition().y/1e6],'centre_distance_mm':math.dist([t.GetPosition().x,t.GetPosition().y],[v.GetPosition().x,v.GetPosition().y])/1e6})
report={'candidate_sha256':m['pcb_sha256'],'matched_project_counterfactuals':results,'actual_multi_new_net_holes':holes,'nearest_ground_stitches_descriptive_only':nearest,'limits':['Counterfactual copper deletions are diagnostic TEST specimens, never design proposals','Whole merged-hole category is not identical to foreign incremental coverage loss','No return-current density, inductance, coupled noise, edge-rate or loaded-output qualification','Actual new-via reference coupling remains explicitly disclosed; all U101 long links remain disconnected']}
(D/('reference_interaction_optimized.json'if sys.flags.optimize else'reference_interaction.json')).write_text(json.dumps(report,indent=2)+'\n')
print('matched-project interaction report written')
