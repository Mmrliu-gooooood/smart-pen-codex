from pathlib import Path
import os,sys,json,hashlib,re,math
os.environ.update(XDG_CONFIG_HOME='/tmp/tailverify/config',XDG_CACHE_HOME='/tmp/tailverify/cache',XDG_DATA_HOME='/tmp/tailverify/data')
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];A=D.parent/'tail100_routing_native_0927/native';B=D/'native';a=p.LoadBoard(str(A/'mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(B/'mainboard_revD.kicad_pcb'));m=json.loads((D/'materialization.json').read_text());model=json.loads((D/'selected_final.json').read_text());uid=lambda q:q.m_Uuid.AsString();sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def req(c,s):
 if not c:raise RuntimeError(s)
def ts(t):return[t.GetNetname(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetLayerSet().FmtHex(),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None]
at={uid(t):t for t in a.GetTracks()};bt={uid(t):t for t in b.GetTracks()};req(set(bt)-set(at)==set(m['added'])and not set(at)-set(bt),'exact object additions');actualchanged=[u for u in at if ts(at[u])!=ts(bt[u])];req(set(actualchanged)==set(m['changed']),'exact copper modification set')
req(len(m['added'])==4 and len(m['changed'])==9,'bounded local delta')
for u in m['changed']+m['added']:
 t=bt[u];req(min(t.GetStart().y,t.GetEnd().y)>=38000000,'no RF modification');req(t.GetNetname()in ['GND','SENS_VIO_1V8','SENS_EXTCLK','SENS_D0','SENS_D1','SENS_D2','SENS_D3','SENS_D4','SENS_D5','SENS_D6','SENS_D7','SENS_PCLK','SENS_VSYNC','SENS_HREF'],'only declared tail nets')
af={f.GetReference():f for f in a.GetFootprints()};bf={f.GetReference():f for f in b.GetFootprints()};req(set(af)==set(bf),'footprints')
for ref,f in af.items():
 z=bf[ref];delta=p.VECTOR2I(0,0);req(z.GetPosition()==f.GetPosition()+delta,'rigid FP position '+ref);req(f.GetValue()==z.GetValue()and f.GetOrientationDegrees()==z.GetOrientationDegrees()and f.GetLayer()==z.GetLayer()and f.GetFPIDAsString()==z.GetFPIDAsString(),'unchanged FP fields '+ref)
 aa={uid(q):q for q in f.Pads()};bb={uid(q):q for q in z.Pads()};req(set(aa)==set(bb),'same pads')
 for u,q in aa.items():
  v=bb[u];req(q.GetNetname()==v.GetNetname()and v.GetPosition()==q.GetPosition()+delta and q.GetSize()==v.GetSize()and q.GetOrientationDegrees()==v.GetOrientationDegrees()and q.GetLayerSet().FmtHex()==v.GetLayerSet().FmtHex(),'rigid same pad '+ref)
for src in A.rglob('*'):
 if src.is_file()and src.suffix!='.kicad_pcb':req(src.read_bytes()==(B/src.relative_to(A)).read_bytes(),'same native source '+str(src))
outline=p.SHAPE_POLY_SET();b.GetBoardPolygonOutlines(outline);bb=outline.BBox();bounds=[bb.GetX()/1e6,bb.GetY()/1e6,bb.GetRight()/1e6,bb.GetBottom()/1e6];req(bounds==[0,-6.5,14,93.3],'actual99.8 outline')
sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));from finite_copper import build,components,shape
from native_polygon import native_fractured_once
an=build(a);bn=build(b);graph={}
for n,nd in an.items():
 before=components(nd);after=components(bn[n]);req(before==after,'all physical components preserved '+n);graph[n]=[len(before),len(after)]
core={n:next(c for c in components(bn[n])if anchor in c)for n,anchor in [('GND','J106.3'),('3V3_AON','J106.2'),('SENS_VIO_1V8','J202.23')]};req([len(core[n])for n in ['GND','3V3_AON','SENS_VIO_1V8']]==[92,41,12],'accepted R218 preserved')
# Native refilled plane coverage for all retained segments; modified route coverage separately, not mistaken for unchanged projections.
def planes(board):
 out={}
 for z in board.Zones():
  if not z.GetIsRuleArea():out.setdefault(z.GetLayer(),p.SHAPE_POLY_SET()).BooleanAdd(native_fractured_once(z.GetFilledPolysList(z.GetLayer())))
 return out
pa,pb=planes(a),planes(b);unchanged_loss=[];coverage=[]
refs={p.F_Cu:[p.In1_Cu],p.B_Cu:[p.In4_Cu],p.In3_Cu:[p.In2_Cu,p.In4_Cu]}
for u,t in bt.items():
 if isinstance(t,p.PCB_VIA)or t.GetNetname()in ['GND','3V3_AON','SENS_VIO_1V8']:continue
 for ref in refs.get(t.GetLayer(),[]):
  s=shape(t,t.GetLayer());missing=p.SHAPE_POLY_SET();missing.BooleanSubtract(s,pb[ref]);oldmiss=None
  if u in at:
   st=shape(at[u],at[u].GetLayer());v=p.SHAPE_POLY_SET();v.BooleanSubtract(st,pa[ref]);oldmiss=v.Area()/1e12
   if u not in m['changed']:
    before=p.SHAPE_POLY_SET();before.BooleanIntersection(s,pa[ref]);after=p.SHAPE_POLY_SET();after.BooleanIntersection(s,pb[ref]);before.BooleanSubtract(after)
    if before.Area()/1e12>1e-8:unchanged_loss.append({'uuid':u,'net':t.GetNetname(),'reference':b.GetLayerName(ref),'loss_mm2':before.Area()/1e12,'bbox_mm':[before.BBox().GetX()/1e6,before.BBox().GetY()/1e6,before.BBox().GetWidth()/1e6,before.BBox().GetHeight()/1e6],'polygon_vertices_mm':[[[before.COutline(i).CPoint(j).x/1e6,before.COutline(i).CPoint(j).y/1e6]for j in range(before.COutline(i).PointCount())]for i in range(before.OutlineCount())]})
  if u in m['changed']+m['added'] or missing.Area()/1e12>1e-8:coverage.append({'uuid':u,'net':t.GetNetname(),'reference':b.GetLayerName(ref),'old_uncovered_mm2':oldmiss,'new_uncovered_mm2':missing.Area()/1e12,'modified':u in m['changed']+m['added']})
(D/'reference_diagnostic.json').write_text(json.dumps({'unchanged_loss':unchanged_loss,'coverage':coverage},indent=2)+'\n')
req(not unchanged_loss,'no added unchanged-signal reference loss')
# Union full per-net trace projections avoids double counting overlaps at bends/endcaps.
def unions(board):
 out={}
 for t in board.GetTracks():
  if isinstance(t,p.PCB_VIA)or t.GetNetname()in ['GND','3V3_AON','SENS_VIO_1V8']:continue
  for ref in refs.get(t.GetLayer(),[]):out.setdefault((t.GetNetname(),ref),p.SHAPE_POLY_SET()).BooleanAdd(shape(t,t.GetLayer()))
 return out
ua,ub=unions(a),unions(b);union_report=[]
for key,poly in ub.items():
 net,ref=key;x=p.SHAPE_POLY_SET();x.BooleanSubtract(ua[key],pa[ref]);y=p.SHAPE_POLY_SET();y.BooleanSubtract(poly,pb[ref]);old=x.Area()/1e12;new=y.Area()/1e12
 if abs(new-old)>1e-8:union_report.append({'net':net,'reference':b.GetLayerName(ref),'old_uncovered_union_mm2':old,'new_uncovered_union_mm2':new,'delta_mm2':new-old})
for ref in ['JP201','JP202','JP301']:req(bf[ref].GetValue()==af[ref].GetValue(),'all jumpers remain open')
for stem,expected in [('base',[0,75,0]),('candidate',[0,75,0])]:
 dr=json.loads((D/f'checks/{stem}/drc.json').read_text());req([len(dr[k])for k in ['violations','unconnected_items','schematic_parity']]==expected,'real DRC '+stem)
e=json.loads((D/'checks/candidate/erc.json').read_text());ev=[v for s in e['sheets']for v in s['violations']];req([(v['severity'],v['type'])for v in ev]==[('warning','global_label_dangling')],'ERC')
print(json.dumps({'status':'STATIC_COURTYARD_ESCAPE_EXPERIMENT_NOFAB_NOPOWER','pcb_sha256':sha(B/'mainboard_revD.kicad_pcb'),'parent_sha256':sha(A/'mainboard_revD.kicad_pcb'),'outline_bounds_mm':bounds,'outline_length_mm':99.8,'finished_length_tolerance_qualified':False,'DRC_unconnected_parity':[0,75,0],'all_net_physical_components_exact_parent':graph,'core':core,'changed_copper':actualchanged,'added_copper':m['added'],'unchanged_signal_additional_reference_loss':unchanged_loss,'residual_classification':'COMPARE_FROZEN0927_NO_UNCHANGED_SIGNAL_LOSS_PENDING_REFERENCE_REVIEW','per_net_reference_union_delta':union_report,'modified_and_uncovered_signal_reference_report':coverage,'limits':['No high-speed timing/EMI approval from shortened/reworked routes','Connector actualFPC, body seating, tenting/plugging, soldermask and wire approach gates remain','DynamicOE, loadedVOH, power sequencing, camera, firmware, battery/charging unresolved']},indent=2))
