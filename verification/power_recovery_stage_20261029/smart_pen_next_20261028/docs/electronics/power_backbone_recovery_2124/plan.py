from pathlib import Path
import json,hashlib,os,math,collections
os.environ['XDG_CONFIG_HOME']='/tmp/pen-powerplan2022-config'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[2];S=R/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb';N=R/'hardware/complete_net_restore_candidate_2014/native/mainboard_revD.kicad_pcb';P=R/'docs/electronics/copper_recovery_plan_2005/recovery_plan.json'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();before={str(f):sha(f)for f in [S,N,P]}
a=p.LoadBoard(str(S));b=p.LoadBoard(str(N));prior=json.loads(P.read_text());uid=lambda t:t.m_Uuid.AsString();L=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu];nets=['3V3_AON','GND','CAM_3V3_SW','CAM_3V3_PRELINK','CAM_CT','CAM_QOD','SENS_VIO_1V8'];power=set(nets[:3]);records={o['uuid']:o for o in prior['objects']};old={uid(t):t for t in a.GetTracks()};current=list(b.GetTracks());pads=[q for f in b.GetFootprints()for q in f.Pads()];safe=[t for u,t in old.items()if t.GetNetname()in power and records[u]['geometry_candidate']];obs=current+pads+safe

def xy(v):return [v.x/1e6,v.y/1e6]
def poly(t,l,margin=0):
 z=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(z,l,margin,50,p.ERROR_OUTSIDE);return z
cache={}
def geom(t,l,margin=0):
 k=(id(t),l,margin)
 if k not in cache:cache[k]=poly(t,l,margin)
 return cache[k]
def check(ts):
 out=[]
 for i,t in enumerate(ts):
  for q in obs+ts[:i]:
   if t.GetNetname()!=q.GetNetname():
    layers=[]
    for l in L:
     if t.IsOnLayer(l)and q.IsOnLayer(l):
      z=p.SHAPE_POLY_SET();z.BooleanIntersection(geom(t,l,150000),geom(q,l));
      if z.Area()>1:layers.append(b.GetLayerName(l))
    if layers:out.append({'candidate_index':i,'kind':'copper','other_uuid':uid(q),'other_net':q.GetNetname(),'layers':layers})
   if isinstance(t,p.PCB_VIA):
    if isinstance(q,p.PCB_VIA):
     gap=math.hypot(t.GetPosition().x-q.GetPosition().x,t.GetPosition().y-q.GetPosition().y)-(t.GetDrillValue()+q.GetDrillValue())/2
     if gap<249999:out.append({'candidate_index':i,'kind':'drill','other_uuid':uid(q),'edge_mm':gap/1e6})
    elif isinstance(q,p.PAD):
     h=p.PCB_VIA(b);h.SetPosition(t.GetPosition());h.SetWidth(p.F_Cu,t.GetDrillValue());h.SetDrill(t.GetDrillValue());h.SetLayerPair(p.F_Cu,p.B_Cu)
     for l in [p.F_Cu,p.B_Cu]:
      if q.IsOnLayer(l):
       z=p.SHAPE_POLY_SET();z.BooleanIntersection(poly(h,l),geom(q,l));
       if z.Area()>1:out.append({'candidate_index':i,'kind':'drill_pad_overlap','other_uuid':uid(q)});break
 return out
V=lambda xy:p.VECTOR2I(round(xy[0]*1e6),round(xy[1]*1e6))
def track(n,l,x,y,w=.5):
 t=p.PCB_TRACK(b);t.SetNetCode(b.GetNetcodeFromNetname(n));t.SetLayer(l);t.SetStart(V(x));t.SetEnd(V(y));t.SetWidth(round(w*1e6));return t
def via(n,x):
 t=p.PCB_VIA(b);t.SetNetCode(b.GetNetcodeFromNetname(n));t.SetPosition(V(x));t.SetWidth(p.F_Cu,600000);t.SetDrill(300000);t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetViaType(p.VIATYPE_THROUGH);return t
cases=[]
def add(name,ts,scope):
 # Keep object references alive: cache keyed by identity.
 cases.append({'name':name,'scope':scope,'objects':ts,'conflicts':check(ts)})
for x in [(11.9,83.9),(11.8,84.6),(10.6,82.6),(11.8,83.2)]:add('AON_core_'+str(x),[track('3V3_AON',p.F_Cu,(10.6,83.9),x),via('3V3_AON',x)],'Only J106.2 to new plane-entry via; no plane connectivity yet')
for x in [(5.8,87.6),(5.8,86.8),(6.1,87.2),(5.0,87.6)]:add('SW_lower_'+str(x),[track('CAM_3V3_SW',p.F_Cu,(5.8,88.7),x),via('CAM_3V3_SW',x),track('CAM_3V3_SW',p.In2_Cu,x,(6.85,82.05))],'Replacement J301.1 to old retained In2 junction; full JP301.2 path not instantiated')
for x in [10.7,11.2,12.5]:add('AON_bridge_In2_'+str(x),[track('3V3_AON',p.In2_Cu,(11.2,55.75),(x,56.5)),track('3V3_AON',p.In2_Cu,(x,56.5),(x,64)),track('3V3_AON',p.In2_Cu,(x,64),(11.3,64.8))],'Replace obstructed B trunk by 0.5mm In2 path using existing endpoint vias; not proof of plane neck/current')
# Direct local decap links: no via or neck thinning; same-width 0.5 supply entry and separate ground plan required.
f={f.GetReference():f for f in b.GetFootprints()};pad=lambda r,n:next(q for q in f[r].Pads()if q.GetNumber()==n)
for u,c in [('U201','C201'),('U202','C203'),('U203','C205')]:add(u+'_decap',[track('3V3_AON',p.F_Cu,xy(pad(u,'1').GetPosition()),xy(pad(c,'1').GetPosition()))],'Local VCCA to capacitor only; no AON plane/ground return claim')
result={'status':'READ_ONLY_NOFAB_NOT_ROUTED','inputs':before,'current_drc_fact':[0,233,0],'pad_contract':[],'zones':[],'conflict_groups':{},'bounded_candidates':[],'limits':['No native save, fill, full DRC or current/thermal qualification','Candidate checks only current 468 copper + all actual pads + prior safe AON/GND/SW fragments; fragments not added','Same-net via-pad overlap checked; no edge/rule-area/old-planes acceptance; no whole-net pass from local clear','No inferred short across JP301 OPEN; external VIO remains reference input']}
for q in pads:
 if q.GetNetname()in nets:result['pad_contract'].append({'uuid':uid(q),'ref':q.GetParentFootprint().GetReference(),'value':q.GetParentFootprint().GetValue(),'pin':q.GetNumber(),'net':q.GetNetname(),'xy_mm':xy(q.GetPosition()),'side':b.GetLayerName(q.GetLayer()),'size_mm':xy(q.GetSize()),'moved_ref':q.GetParentFootprint().GetReference()in prior['changed_refs']})
for z in a.Zones():
 if not z.GetIsRuleArea():result['zones'].append({'uuid':uid(z),'net':z.GetNetname(),'layers':[a.GetLayerName(l)for l in L if z.IsOnLayer(l)],'clearance_mm':z.GetLocalClearance()/1e6,'minimum_thickness_mm':z.GetMinThickness()/1e6,'thermal_gap_mm':z.GetThermalReliefGap()/1e6,'thermal_spoke_mm':z.GetThermalReliefSpokeWidth()/1e6,'old_fill_not_inherited':True})
for n in sorted(power):
 oo=[o for o in prior['objects']if o['net']==n and(o['new_conflicts']or o['original_violations'])];result['conflict_groups'][n]={'objects':oo,'by_cause':dict(collections.Counter(c['kind']for o in oo for c in o['new_conflicts']))}
for c in cases:
 result['bounded_candidates'].append({'name':c['name'],'scope':c['scope'],'finite_geometry_clear':not c['conflicts'],'conflicts':c['conflicts'],'objects':[{'type':'via'if isinstance(t,p.PCB_VIA)else'track','net':t.GetNetname(),'layer':'through'if isinstance(t,p.PCB_VIA)else b.GetLayerName(t.GetLayer()),'start_mm':xy(t.GetStart()),'end_mm':xy(t.GetEnd()),'width_mm':(t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth())/1e6,'drill_mm':t.GetDrillValue()/1e6 if isinstance(t,p.PCB_VIA)else None}for t in c['objects']]})
if any(sha(Path(f))!=h for f,h in before.items()):raise RuntimeError('INPUT MUTATED')
(D/'plan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print([(c['name'],not c['conflicts'],len(c['conflicts']))for c in cases])
