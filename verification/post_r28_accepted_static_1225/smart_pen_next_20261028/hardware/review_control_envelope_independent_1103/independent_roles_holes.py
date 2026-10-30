from pathlib import Path
import os,sys,json,xml.etree.ElementTree as ET
os.environ.update(XDG_CONFIG_HOME='/tmp/review1103/config',XDG_DATA_HOME='/tmp/review1103/data',XDG_CACHE_HOME='/tmp/review1103/cache')
import pcbnew as p
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'translator_domain_candidate_0130'))
from finite_copper import build,components,shape
from native_polygon import native_fractured_once
b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));fs={f.GetReference():f for f in b.GetFootprints()};pads={f.GetReference()+'.'+q.GetNumber():q for f in b.GetFootprints()for q in f.Pads()};g={n:components(v)for n,v in build(b).items()}
def req(c,m):
 if not c:raise RuntimeError(m)
for pin,layer in [('U203.5',p.F_Cu),('R222.1',p.B_Cu),('U203.6',p.F_Cu),('R223.1',p.B_Cu)]:req(pads[pin].IsOnLayer(layer),'actual pad side '+pin)
nets=['CAM_RESET_UART_TX','CAM_PWDN_UART_RX'];pairs={'CAM_RESET_UART_TX':['R222.1','U203.5'],'CAM_PWDN_UART_RX':['R223.1','U203.6']}
for net,pair in pairs.items():req(pair in g[net],'exact bias pair; MCU/J104 remain separate '+net)
for pin,net,anchor in [('U203.2','3V3_AON','J106.2'),('U203.3','3V3_AON','J106.2'),('U203.1','3V3_AON','J106.2'),('R222.2','GND','J106.3'),('R223.2','GND','J106.3')]:req(any(pin in c and anchor in c for c in g[net]),'actual direction/VCCA/bias core '+pin)
xml=ET.parse(D/'checks/candidate/netlist.xml').getroot();pinmap={n.get('ref')+'.'+n.get('pin'):{'net':z.get('name'),'function':n.get('pinfunction')}for z in xml.findall('./nets/net')for n in z.findall('node')}
req(pinmap['U203.5']['function']=='1A2'and pinmap['U203.6']['function']=='2A1','actual source pinfunctions');req(fs['U203'].GetValue()=='SN74AXC4T245PWR','actual PW package value')
for ref in ['R222','R223']:req(fs[ref].GetValue()=='100k 1%','existing100k')
info={'pinroles':{n:pinmap[n]for n in ['U203.5','U203.6','U203.2','U203.3','U203.12','U203.11']},'physical_target_net_components':{n:g[n]for n in nets},'actual_direction_VCCA_and_bias_grounds_in_expected_core':True,'pad_sides':{'U203.5':'F','U203.6':'F','R222.1':'B','R223.1':'B'}}
m=json.loads((D/'materialization.json').read_text());vias=[t for t in b.GetTracks()if isinstance(t,p.PCB_VIA)and t.m_Uuid.AsString()in m['added']];req(len(vias)==2,'two vias');removed=[]
for v in vias:
 removed.append({'net':v.GetNetname(),'xy_mm':[v.GetPosition().x/1e6,v.GetPosition().y/1e6],'uuid':v.m_Uuid.AsString()});b.Remove(v)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());dest=D/'diagnostic_both_vias_removed.kicad_pcb';p.SaveBoard(str(dest),b);c=p.LoadBoard(str(dest));rows=[]
for net in nets:
 for layer,ref in [(p.F_Cu,p.In1_Cu),(p.B_Cu,p.In4_Cu)]:
  plane=p.SHAPE_POLY_SET();projection=p.SHAPE_POLY_SET()
  for z in c.Zones():
   if not z.GetIsRuleArea()and z.GetLayer()==ref:plane.BooleanAdd(native_fractured_once(z.GetFilledPolysList(ref)))
  for t in c.GetTracks():
   if not isinstance(t,p.PCB_VIA)and t.GetNetname()==net and t.GetLayer()==layer:projection.BooleanAdd(shape(t,layer))
  missing=p.SHAPE_POLY_SET();missing.BooleanSubtract(projection,plane);req(missing.Area()==0,'new missing removed with own vias '+net);rows.append({'net':net,'reference':c.GetLayerName(ref),'uncovered_without_own_vias_mm2':missing.Area()/1e12})
info.update({'own_via_hole_causal_native_refill_check':rows,'removed_vias':removed,'datasheet_semantics':'Previously visually reviewed same hash TI SCES877B p4,p20: PW pin5=1A2,pin6=2A1,pins2/3=1DIR/2DIR; DIR high selects A as input when enabled. No conclusion from UART RX/TX names.','scope':'Static source/physical topology only. Diagnostic broken specimen, never candidate. No dynamic/loaded/timing/sequence approval.'})
(D/'independent_roles_holes.json').write_text(json.dumps(info,indent=2)+'\n')
