from pathlib import Path
import json,hashlib,collections,xml.etree.ElementTree as E
import pcbnew as p
from pcb_preflight import verify
D=Path(__file__).resolve().parent;H=D.parent;S=H/'j107_mode_port_closure';B=H/'gate_cam_on_path_maintenance'
def need(x,m):
 if not x:raise RuntimeError(m)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
need(sha(D/'native/mainboard_revD.kicad_pcb')=='8aa2581b4df112b979d83e67b9a6a2ddaa70a433c265cdc9849e41b60ff05ab5','Candidate SHA')
for name in ['j107_mode_port_closure','j107_current_revB_harness']:
 m=json.loads((H/name/'manifest.json').read_text())
 for n,v in m['files'].items():need(sha(H/name/n)==(v['sha256']if isinstance(v,dict)else v),'Changed input '+n)
lock=json.loads((D/'preflight_lock.json').read_text());config=verify(D/'native/mainboard_revD.kicad_pcb',lock,'routing')
try:verify(D/'native/mainboard_revD.kicad_pcb',lock,'manufacturing')
except ValueError as e:reject=str(e)
else:raise RuntimeError('Manufacturing unexpectedly approved')
a=p.LoadBoard(str(B/'native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'))
def rule(board):
 return{z.m_Uuid.AsString():(str(z.Outline().Format()),list(z.GetLayerSet().Seq()),z.GetDoNotAllowTracks(),z.GetDoNotAllowVias(),z.GetDoNotAllowPads(),z.GetDoNotAllowCopperPour(),z.GetDoNotAllowFootprints())for z in board.Zones()if z.GetIsRuleArea()}
need(rule(a)==rule(b),'MEMS/RF keepout changed')
x=E.parse(D/'fresh.xml');nets={}
for n in x.findall('./nets/net'):
 for pin in n: nets[(pin.get('ref'),pin.get('pin'))]=(n.get('name'),pin.get('pinfunction'))
need(nets['U101','24'][0]=='USB_EN1' and nets['U101','27'][0]=='USB_EN2','Source mode outputs wrong')
for pin,net in [('1','USB_EN1'),('2','USB_EN2'),('3','GND')]:need(nets['J107',pin][0]==net,'J107 mapping')
need(nets['JP301','1'][0]!=nets['JP301','2'][0],'JP301 source short')
def counter(path):
 q=json.loads(path.read_text());c=collections.Counter()
 for v in q['violations']:
  v=dict(v);v['items']=sorted(v.get('items',[]),key=lambda z:json.dumps(z,sort_keys=True));c[json.dumps(v,sort_keys=True)]+=1
 return q,c
old,oc=counter(B/'preflight.native_drc.json');new,nc=counter(D/'fresh_drc.json')
need(not nc-oc and sum((oc-nc).values())==11,'Full DRC multiset')
need([len(new[k])for k in ['violations','unconnected_items','schematic_parity']]==[17,38,0],'Full counts')
print(json.dumps({'pcb_sha256':sha(D/'native/mainboard_revD.kicad_pcb'),'same_basename_preflight':config,'manufacturing_rejected':reject,'rule_areas_unchanged':list(rule(b)),'source_mode_pinfunctions':{str(k):nets[k]for k in [('U101','24'),('U101','27')]},'fresh_DRC_counts':[17,38,0],'removed_full_findings':[json.loads(v)for v in (oc-nc).elements()],'added_full_findings':[],'source_entities':len(x.findall('./components/comp')),'source_endpoints':len(nets)},indent=2))
