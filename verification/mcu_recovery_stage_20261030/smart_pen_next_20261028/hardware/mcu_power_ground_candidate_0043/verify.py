from pathlib import Path
import os,json,hashlib,math
os.environ['XDG_CONFIG_HOME']='/tmp/pen-mcuverify0043'
import pcbnew as p
from finite_copper import build,components,shape,L
from native_polygon import native_fractured_once
D=Path(__file__).resolve().parent;R=D.parents[1];B=R/'hardware/gnd_conservative_recovery_2305/native/mainboard_revD.kicad_pcb';O=R/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb';F=D/'native/mainboard_revD.kicad_pcb';m=json.loads((D/'materialization.json').read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();uid=lambda t:t.m_Uuid.AsString()
def req(x,msg):
 if not x:raise RuntimeError(msg)
a=p.LoadBoard(str(B));b=p.LoadBoard(str(F));old=p.LoadBoard(str(O));bn=build(b);an=build(a);at={uid(t):t for t in a.GetTracks()};bt={uid(t):t for t in b.GetTracks()};ot={uid(t):t for t in old.GetTracks()}
def ts(t):return(t.GetClass(),t.GetNetname(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetLayerSet().FmtHex(),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None)
def fps(board):return sorted((f.GetReference(),f.m_Uuid.AsString(),f.GetValue(),(str(f.GetFPID().GetLibNickname()),str(f.GetFPID().GetLibItemName())),f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees(),f.GetLayer(),sorted((uid(q),q.GetNumber(),q.GetNetname(),q.GetPosition().x,q.GetPosition().y,q.GetOrientationDegrees(),q.GetSize().x,q.GetSize().y,q.GetLayerSet().FmtHex())for q in f.Pads()))for f in board.GetFootprints())
req(fps(a)==fps(b),'footprint/pad changed');req(set(bt)-set(at)==set(m['AON_added']+m['EP_GND_added']),'extra copper');req(all(ts(t)==ts(bt[u])for u,t in at.items()),'old copper changed');req(len(bt)==680,'object count')
for u in m['AON_added']+m['EP_GND_added']:
 x=list(ts(ot[u]));y=list(ts(bt[u]));
 if u in m['widened_254um']:x[-2]=254000
 req(x==y,'source object changed beyond width '+u)
for ext in ['kicad_pro','kicad_dru','kicad_sch']:
 req((B.parent/('mainboard_revD.'+ext)).read_bytes()==(F.parent/('mainboard_revD.'+ext)).read_bytes(),'source copy '+ext)
def reach(nodes,start,omit=set()):
 nodes=[n for n in nodes if n[0]not in omit];lookup={n[0]:n for n in nodes};seen={start};todo=[start]
 while todo:
  _,_,x=lookup[todo.pop()]
  for name,_,y in nodes:
   if name in seen:continue
   for l in x.keys()&y.keys():
    if not x[l].BBox().Intersects(y[l].BBox()):continue
    z=p.SHAPE_POLY_SET();z.BooleanIntersection(x[l],y[l])
    if z.Area()>1:seen.add(name);todo.append(name);break
 return seen
# Preserve each existing same-net physical pad component, not just nominal airwire totals.
retained={}
for net,ns in an.items():
 before=components(ns);after=components(bn[net]);req(all(any(set(c)<=set(d)for d in after)for c in before),'prior component broken '+net);retained[net]=[len(before),len(after)]
core={};neg=[]
for net,start in [('3V3_AON','J106.2'),('GND','J106.3')]:
 seen=reach(bn[net],start);before=reach(an[net],start);pp=sorted(n for n,pad,_ in bn[net]if pad and n in seen);oldpp=sorted(n for n,pad,_ in an[net]if pad and n in before);req(set(oldpp)<=set(pp),'core regressed');core[net]={'before':oldpp,'after':pp,'total':sum(pad for _,pad,_ in bn[net])}
(D/'core_diagnostic.json').write_text(json.dumps(core,indent=2));req(len(core['3V3_AON']['after'])==14,'AON pads');req(len(core['GND']['after'])==40,'GND pads');ep=sorted(n for n,ispad,_ in bn['GND']if ispad and n.startswith('U101.57#'));req(len(ep)==9 and set(ep)<=set(core['GND']['after']),'EP not grounded')
rows=json.loads((R/'docs/electronics/aon_branch_reuse_plan_2318/evaluation.json').read_text())['geometrically_screened_groups']
for g in rows:
 r=reach(bn['3V3_AON'],'J106.2',set(g['objects']));req(not set(g['pads'])&r,'AON group not causal');neg.append({'kind':'AON_group','id':g['id'],'pads_disconnect':g['pads']})
for u in m['EP_GND_added']:
 t=bt[u];f=next(f for f in b.GetFootprints()if f.GetReference()=='U101');pad=next(q for q in f.Pads()if q.GetNetname()=='GND'and q.GetPosition()==t.GetPosition());name='U101.57#'+uid(pad);r=reach(bn['GND'],'J106.3',{u});req(name not in r,'EP negative not causal');neg.append({'kind':'EP_via','uuid':u,'pad_disconnect':name})
# True native filled polygons converted once from fractured encoding. Never re-Unfracture a Boolean result.
za={uid(z):z for z in a.Zones()if not z.GetIsRuleArea()};zb={uid(z):z for z in b.Zones()if not z.GetIsRuleArea()};planes=[];groundA={};groundB={}
for u,z in za.items():
 nz=zb[u];l=z.GetLayer();x=native_fractured_once(z.GetFilledPolysList(l));y=native_fractured_once(nz.GetFilledPolysList(l));lost=p.SHAPE_POLY_SET();lost.BooleanSubtract(x,y);gained=p.SHAPE_POLY_SET();gained.BooleanSubtract(y,x);xe=p.SHAPE_POLY_SET(x);ye=p.SHAPE_POLY_SET(y);xe.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000);ye.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000)
 planes.append({'uuid':u,'net':z.GetNetname(),'layer':b.GetLayerName(l),'removed_mm2':lost.Area()/1e12,'added_mm2':gained.Area()/1e12,'normalized_025_eroded_components_before':xe.OutlineCount(),'after':ye.OutlineCount(),'before_holes':sum(x.HoleCount(i)for i in range(x.OutlineCount())),'after_holes':sum(y.HoleCount(i)for i in range(y.OutlineCount()))})
 if z.GetNetname()=='GND':groundA.setdefault(l,p.SHAPE_POLY_SET()).BooleanAdd(x);groundB.setdefault(l,p.SHAPE_POLY_SET()).BooleanAdd(y)
projection=[]
for t in a.GetTracks():
 if isinstance(t,p.PCB_VIA)or t.GetNetname()in ['GND','3V3_AON','CAM_3V3_SW']:continue
 ref=p.In1_Cu if t.GetLayer()==p.F_Cu else p.In4_Cu;raw=shape(t,t.GetLayer());x=p.SHAPE_POLY_SET();x.BooleanIntersection(raw,groundA[ref]);y=p.SHAPE_POLY_SET();y.BooleanIntersection(raw,groundB[ref]);lost=p.SHAPE_POLY_SET();lost.BooleanSubtract(x,y)
 if lost.Area()/1e12>1e-8:projection.append({'uuid':uid(t),'net':t.GetNetname(),'layer':b.GetLayerName(t.GetLayer()),'reference':b.GetLayerName(ref),'additional_uncovered_projection_mm2':lost.Area()/1e12})
req(not projection,'existing signal reference newly lost')
drc=json.loads((D/'drc.json').read_text());counts=[len(drc[k])for k in['violations','unconnected_items','schematic_parity']];req(counts==[0,180,0],'native counts')
print(json.dumps({'status':'NOFAB_NO_FULL_POWER_QUALIFICATION','sha':sha(F),'base_sha':sha(B),'old_source_sha':sha(O),'objects':len(bt),'footprints':len(fps(b)),'physical_pads':sum(len(list(f.Pads()))for f in b.GetFootprints()),'all_prior_pad_components_preserved':retained,'core':core,'negative_checks':neg,'plane_delta':planes,'all_existing_signal_reference_additional_losses':projection,'full_DRC':counts,'limits':['Pin2/3 analog main feed still missing; AON25/39 pads unconnected','C207 GND absent; not all added AON branches have complete decoupling returns','Nine original EP vias restored in-pad geometrically; solder-via process remains unqualified','0.254mm branches follow general guide suggestion; no domain current/thermal/transient guarantee','Plane erosion is representation-guarded geometric screening, not current rating']},indent=2))
