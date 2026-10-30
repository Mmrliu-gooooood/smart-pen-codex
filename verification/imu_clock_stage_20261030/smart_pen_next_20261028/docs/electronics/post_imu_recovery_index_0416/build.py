from pathlib import Path
import os,sys,json,hashlib,collections,xml.etree.ElementTree as ET
os.environ['XDG_CONFIG_HOME']='/tmp/imu-recovery0416';D=Path(__file__).resolve().parent;R=D.parents[2];N=R/'hardware/imu_j107_clock_native_0405';F=N/'native/mainboard_revD.kicad_pcb';sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));import pcbnew as p
from finite_copper import build,components
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def req(c,m):
 if not c:raise RuntimeError(m)
req(sha(F)=='d6c91327a9335a0039c10cd34943664095ca476524b7b5bced8afa4dc0219c22','PCB hash');b=p.LoadBoard(str(F));nodes=build(b);cs={n:components(v)for n,v in nodes.items()};xml=ET.parse(N/'checks/candidate/netlist.xml').getroot();src={};comp={}
for c in xml.findall('./components/comp'):
 comp[c.get('ref')]={'value':c.findtext('value'),'sheet':c.find('sheetpath').get('names'),'sheetfile':next((x.get('value')for x in c.findall('property')if x.get('name')=='Sheetfile'),None),'libsource':c.find('libsource').attrib,'symbol_timestamp':c.findtext('tstamps')}
for n in xml.findall('./nets/net'):
 for node in n.findall('node'):src[(node.get('ref'),node.get('pin'))]={**node.attrib,'net':n.get('name')}
obj={t.m_Uuid.AsString():t.GetNetname()for t in b.GetTracks()};pads={};uidpad={}
for f in b.GetFootprints():
 for pad in f.Pads():
  ref=f.GetReference();num=pad.GetNumber();uid=pad.m_Uuid.AsString();name=ref+'.'+num
  names=[q[0]for q in nodes[pad.GetNetname()]if q[1]and q[0].split('#')[0]==name];name=name+'#'+uid if len(names)>1 else name
  sr=src.get((ref,num))
  if sr is None and num=='' and pad.GetNetname()=='':sr={'net':'','pinfunction':'MECHANICAL_UNNUMBERED_NO_SYMBOL_PIN','pintype':'mechanical'}
  req(sr is not None,'embedded symbol source pin missing '+name);req(sr['net']==pad.GetNetname(),'source PCB net mismatch '+name)
  pads[name]={'physical_pad':name,'uuid':uid,'ref':ref,'pin':num,'net':pad.GetNetname(),'source_pinfunction':sr.get('pinfunction'),'source_pintype':sr.get('pintype'),'source_component':comp[ref],'xy_mm':[pad.GetPosition().x/1e6,pad.GetPosition().y/1e6],'layers':[b.GetLayerName(l)for l in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]if pad.IsOnLayer(l)]};obj[uid]=pad.GetNetname();uidpad[uid]=name
j=json.loads((N/'checks/candidate/drc.json').read_text());air=[];counts=collections.Counter()
for i,v in enumerate(j['unconnected_items']):
 nets={obj[x['uuid']]for x in v['items']};req(len(nets)==1,'airwire multi-net');net=nets.pop();counts[net]+=1;air.append({'index':i,'net':net,'items':[{'uuid':x['uuid'],'physical_pad':uidpad.get(x['uuid']),'description':x['description'],'xy':x['pos']}for x in v['items']]})
rows=[]
for net,groups in sorted(cs.items()):
 if net not in counts:continue
 rows.append({'net':net,'actual_DRC_airwire_count':counts[net],'physical_pad_components':[[pads[x]for x in g]for g in groups],'physical_pad_count':sum(map(len,groups)),'source_sheet_categories':sorted({pads[x]['source_component']['sheet']for g in groups for x in g})})
cores={}
for net,start,total,missing in [('3V3_AON','J106.2',39,4),('GND','J106.3',102,34),('SENS_VIO_1V8','J202.23',12,0)]:
 core=next(g for g in cs[net]if start in g);off=[x for g in cs[net]if g!=core for x in g];req(len(off)==missing and len(core)+missing==total,'corecount');cores[net]={'core_start':start,'core_count':len(core),'total_physical_pads':total,'outside_core':[pads[x]for x in off],'outside_core_components':[g for g in cs[net]if g!=core]}
req(sum(counts.values())==120,'120total')
result={'status':'READ_ONLY_SOURCE_CLASSIFIED_RECOVERY_INDEX_NOFAB_NOPOWER','pcb_sha256':sha(F),'DRC_counts':[len(j[k])for k in ['violations','unconnected_items','schematic_parity']],'source_method':'physical finite copper components + exported netlist pinfunction/pintype derived from retained embedded schematic symbol definitions; NOT PCB GetPinFunction','airwires_by_net':dict(sorted(counts.items())),'net_component_inventory':rows,'cores':cores,'all_120_raw_airwire_mapping':air,'all_physical_pads':pads,'boundary':'Different nets on JP301 remain deliberately OPEN; this index does not instruct bridging/commissioning'}
print(json.dumps(result,indent=2))
