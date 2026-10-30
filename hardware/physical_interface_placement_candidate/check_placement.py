from pathlib import Path
import pcbnew as p,xml.etree.ElementTree as E,json,hashlib,sys,math,re,collections
D=Path(__file__).resolve().parent;S=D.parent/'rf_width14_selected_board_candidate';I=D.parent/'physical_interface_study';sys.path.insert(0,str(D));from physical_graph_interface import graph
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
if sha(S/'mainboard_revD.kicad_pcb')!='016d963f764430b6122da29039a5573792e3f0c78078180b18582af69b044c7e':raise ValueError('Baseline version')
a=p.LoadBoard(str(S/'mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(D/'mainboard_revD.kicad_pcb'));fa={f.GetReference():f for f in a.GetFootprints()};fb={f.GetReference():f for f in b.GetFootprints()}
def copper(b):return {t.m_Uuid.AsString():(t.GetNetname(),t.GetLayer(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth()) for t in b.GetTracks()}
if copper(a)!=copper(b):raise ValueError('Old actual copper changed')
def pads(f):return [(z.GetNumber(),z.GetNetname(),z.GetPosition().x,z.GetPosition().y,z.GetSize().x,z.GetSize().y,tuple(z.GetLayerSet().Seq())) for z in f.Pads()]
for ref,f in fa.items():
 if pads(f)!=pads(fb[ref]):raise ValueError('Old footprint changed '+ref)
if set(fb)-set(fa)!={'J103','J104','J105','J202','J110'} or len(fb)!=84:raise ValueError('New physical set')
x=E.parse(D/'mainboard_revD.xml');nodes={(z.get('ref'),z.get('pin')):n.get('name') for n in x.findall('./nets/net') for z in n};cs={z.get('ref'):z for z in x.findall('./components/comp')}
if len(cs)!=84 or len(nodes)!=312:raise ValueError('Fresh v4 source shape')
for ref,f in fb.items():
 z=cs[ref];path='/cebe562b-54ce-58d7-a4f0-094e70dd7d0a'+z.find('sheetpath').get('tstamps')+z.findtext('tstamps')
 if f.GetPath().AsString()!=path:raise ValueError('Full source path '+ref)
 for pad in f.Pads():
  if pad.GetNumber() and pad.GetNetname()!=nodes.get((ref,pad.GetNumber())):raise ValueError('Native source pad '+ref)
rpt=(D/'drc.rpt').read_text();counts=collections.Counter(re.findall(r'^\[([^]]+)\]',rpt,re.M))
if counts!={'unconnected_items':37}:raise ValueError('Fresh native DRC categories '+str(counts))
if 'Found 0 schematic parity issues' not in (D/'drc.log').read_text() or (D/'drc.exit').read_text().strip()!='5':raise ValueError('Native parity/exit')
g=graph(b);oldpadids={z.m_Uuid.AsString() for f in a.GetFootprints() for z in f.Pads()};bad=[]
for n in g:
 groups=[[z for z in comp if z.split('@')[1] in oldpadids] for comp in n['components']];groups=[z for z in groups if z]
 if len(groups)>1:bad.append((n['net'],groups))
if bad:raise ValueError('Previously connected actual pads split '+str(bad))
# Source geometry lower bounds, not routed timing or connector/flex propagation proof.
rows=[];j=fb['J202'];alloldpads=[z for f in a.GetFootprints() for z in f.Pads()]
for pad in sorted([z for z in j.Pads() if z.GetNumber()],key=lambda z:int(z.GetNumber())):
 net=pad.GetNetname()
 if net in ['GND','SENS_VIO_1V8']:continue
 origins=[z for z in alloldpads if z.GetNetname()==net and z.GetParentFootprint().GetReference().startswith('U')]
 if len(origins)!=1:raise ValueError('Ambiguous translation endpoint '+net)
 z=origins[0];distance=math.hypot(pad.GetPosition().x-z.GetPosition().x,pad.GetPosition().y-z.GetPosition().y)/1e6
 rows.append({'net':net,'translator_ref':z.GetParentFootprint().GetReference(),'translator_pin':z.GetNumber(),'translator_xy_mm':[z.GetPosition().x/1e6,z.GetPosition().y/1e6],'translator_copper_layers':[b.GetLayerName(k) for k in z.GetLayerSet().CuStack()],'connector_pin':pad.GetNumber(),'connector_xy_mm':[pad.GetPosition().x/1e6,pad.GetPosition().y/1e6],'connector_layer':'B.Cu','IC_to_connector_Euclidean_lower_bound_mm':distance,'at_least_one_layer_transition':True})
pclk=next(z['IC_to_connector_Euclidean_lower_bound_mm'] for z in rows if z['net']=='SENS_PCLK')
for z in rows:z['straight_distance_difference_from_PCLK_mm']=z['IC_to_connector_Euclidean_lower_bound_mm']-pclk
result={'status':'PLACEMENT_ONLY_NOFAB_NOT_ROUTED','pcb_sha256':sha(D/'mainboard_revD.kicad_pcb'),'old_footprints_unchanged':79,'old_copper_items_unchanged':len(copper(a)),'new_physical_ports':5,'native_footprints':84,'native_source_endpoints':312,'native_DRC_exit':5,'native_DRC_counts':dict(counts),'native_parity_issues':0,'old_actual_pad_components_preserved':True,'all_pad_graph':g,'DVP_geometry_lower_bounds':rows,'timing_claim':'None: Euclidean geometry only; actual routes, buffers, flex stack and setup/hold require analysis/measurement'}
print(json.dumps(result,indent=2))
