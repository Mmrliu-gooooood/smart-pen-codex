import geometry as g,json,hashlib,sys,re
p=g.p
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def req(c,m):
 if not c:raise RuntimeError(m)
req(sha(g.S)=='69d93e9dfa7afd427110a271d7fbdcdcd3a0841d79b502c436a50572849c08cc','parent immutable')
s=(g.R/'docs/electronics/post_imu_recovery_index_0416/embedded_audit.py').read_text();exec(s[s.index('def parse'):s.index('lookup={}')]);lookup={};sources={}
for f in g.S.parent.rglob('*.kicad_sch'):
 root=parse(f.read_text());lib=children(root,'lib_symbols')
 if not lib:continue
 defs={x[1]:x for x in children(lib[0],'symbol')};sources[str(f.relative_to(g.S.parent))]=sha(f)
 for sym in children(root,'symbol'):
  refs=[x[2]for x in children(sym,'property')if x[1]=='Reference']
  if not refs:continue
  for pin in pins(defs[first(sym,'lib_id')[1]]):lookup[refs[0]+'.'+first(pin,'number')[1]]={'function':first(pin,'name')[1],'type':pin[1],'source':str(f.relative_to(g.S.parent))}
expected={'U101.6':'GPIO1','U101.10':'GPIO5','U101.11':'GPIO6','U501.12':'INT1','U501.1':'SCL','U501.4':'SDA'}
for name,fn in expected.items():req(lookup[name]['function']==fn,'embedded '+name)
for name in ['R501.1','R502.1']:req(g.pm[name].GetParentFootprint().GetValue()=='10k 1%','10kactual')
sys.path.insert(0,str(g.R/'hardware/translator_domain_candidate_0130'));from finite_copper import build,components,shape
ns=build(g.b);nets=['AON_I2C_SCL','AON_I2C_SDA','PICKUP_INT_N'];base={n:components(ns[n])for n in nets};req([len(base[n])for n in nets]==[3,3,2],'actual five signal gaps')
for name in ['R501.1','R502.1']:req([name]in components(ns['3V3_AON']),'two singleton supply gaps')
r=json.loads((g.D/'trial2_parts.json').read_text());remove=['13079769-348d-5142-9cb4-1d44ec56a7b8','fb1700a3-5c27-5c36-9d84-b9492b46b711'];g.old=[t for t in g.old if t.m_Uuid.AsString()not in remove];new=[]
for ts in r.values():
 for t in ts:
  if t['type']=='via':q=g.via(t['net'],t['start']);q.SetWidth(p.F_Cu,round(t['width']*1e6));q.SetDrill(round(t['drill']*1e6))
  else:q=g.track(t['net'],g.b.GetLayerID(t['layer']),t['start'],t['end'],t['width'])
  new.append(q)
e=g.errors(new);req(not e,'partial joint finite')
irqnodes=ns['PICKUP_INT_N']+ [('new'+str(i),False,{l:shape(t,l)for l in g.L if t.IsOnLayer(l)})for i,t in enumerate(new)if t.GetNetname()=='PICKUP_INT_N'];irq=components(irqnodes);req(irq==[['U101.6','U501.12']],'partial irq physicalmodel')
provider=g.R.parent/'smart_pen_app_pipeline_20261028/firmware/application_idf/main/board_provider_absent.c';req('return 0;'in provider.read_text(),'provider remains absent')
print(json.dumps({'status':'READONLY_FAILED_WHOLE_SEVEN_GAP_PLAN_NO_NATIVE','parent_sha':sha(g.S),'parent_native_counts':[0,113,0],'actual_signal_components':base,'actual_additional_supply_gaps':['R501.1','R502.1'],'source_functions':{n:lookup[n]for n in expected},'source_hashes':sources,'partial_topology2_finite_errors':e,'partial_irq_pad_graph':irq,'partial_objects':len(new),'all_layers_via_pad_collision_checked_including_same_net':True,'whole_seven_gap_complete':False,'new_native_created':False,'parent_unchanged':True,'firmware_provider':{'sha256':sha(provider),'contents':provider.read_text()},'limits':['Partial IRQ is model only; no freshfill/DRC or signal qualification','AON replacement full endpoints have geometry but plane/core not refilled','No global routing impossibility claim','Pressure BOOT/NIB merged reference hole and prior DFM gates retained']} ,indent=2))
