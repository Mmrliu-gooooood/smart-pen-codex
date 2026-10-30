from pathlib import Path
import json,hashlib,collections,xml.etree.ElementTree as E
import pcbnew as p
from copper_geometry import shape,build,L
D=Path(__file__).resolve().parent;B=D.parent/'j107_mode_port_closure';f=D/'native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f))
def need(x,msg):
 if not x:raise RuntimeError(msg)
need(hashlib.sha256(f.read_bytes()).hexdigest()=='752f83d57fa15450862dcf1c3751041b49f9830fd2c541443d717c6e99d1b229','PCB hash')
for a in (B/'native').rglob('*'):
 if a.is_file()and a.suffix not in ['.kicad_pcb','.kicad_prl']:
  z=D/'native'/a.relative_to(B/'native');need(z.is_file()and z.read_bytes()==a.read_bytes(),'source/library closure')
# Exactly reviewed MEMS and other rule metadata, including allowed pads, not just names.
rb=p.LoadBoard(str(D.parent/'mems_layered_rule_study/native/mainboard_revD.kicad_pcb'))
def rules(board):return{z.GetZoneName():(str(z.Outline().Format()),list(z.GetLayerSet().Seq()),z.GetDoNotAllowTracks(),z.GetDoNotAllowVias(),z.GetDoNotAllowPads(),z.GetDoNotAllowCopperPour(),z.GetDoNotAllowFootprints())for z in board.Zones()if z.GetIsRuleArea()}
need(rules(b)==rules(rb),'Integrated rule contract differs')
# Reference chains must describe every actual IRQ track, with exact nm geometry.
ts={t.m_Uuid.AsString():t for t in b.GetTracks()if t.GetNetname()=='PICKUP_INT_N'};rr=json.loads((D/'irq_simplified_routes.json').read_text());seen=set()
for r in rr:
 t=ts[r['uuid']];need(r['uuid']not in seen,'duplicate declared track');seen.add(r['uuid'])
 if r['type']=='track':
  need(not isinstance(t,p.PCB_VIA),'wrong track class');need([round(v*1e6)for v in r['a']]==[t.GetStart().x,t.GetStart().y]and[round(v*1e6)for v in r['z']]==[t.GetEnd().x,t.GetEnd().y]and r['layer']==b.GetLayerName(t.GetLayer()),'reference chain geometry')
 else:need(isinstance(t,p.PCB_VIA),'wrong via class')
remaining=[t for u,t in ts.items()if u not in seen];extra_vias=[t for t in remaining if isinstance(t,p.PCB_VIA)];need(len(extra_vias)==1 and extra_vias[0].m_Uuid.AsString()=='f5851835-0f12-40ba-899c-e85f34a6b556' and extra_vias[0].GetPosition()==p.VECTOR2I(1850000,9460000),'MCU fanout via');rest=[t for t in remaining if not isinstance(t,p.PCB_VIA)];need(all(not isinstance(t,p.PCB_VIA)and t.GetLayer()==p.F_Cu and t.GetStart().y<20e6 for t in rest),'unreported reference chain copper')
source=sorted(rest,key=lambda t:-t.GetStart().x)
for t,u in zip(source,source[1:]):need(t.GetEnd()==u.GetStart(),'MCU source chain not contiguous')
# Full finite copper check against foreign nets for both touched signals.
nets=build(b);hits=[]
for net in ['PICKUP_INT_N','BOOT_N']:
 for name,_,ss in nets[net]:
  for other,nodes in nets.items():
   if other==net:continue
   for on,_,oo in nodes:
    for layer in ss.keys()&oo.keys():
     if not ss[layer].BBox().Intersects(oo[layer].BBox()):continue
     q=p.SHAPE_POLY_SET();q.BooleanIntersection(ss[layer],oo[layer])
     if q.Area()>1:hits.append([net,name,other,on,int(layer)])
need(not hits,'Touched signal foreign copper intersection')
x=E.parse(D/'fresh.xml');ns={(v.get('ref'),v.get('pin')):(n.get('name'),v.get('pinfunction'))for n in x.findall('./nets/net')for v in n}
need(ns['U101','6'][0]=='PICKUP_INT_N'and ns['U101','6'][1]=='GPIO1'and ns['U501','12'][0]=='PICKUP_INT_N','IRQ source pin identity')
e=json.loads((D/'erc.json').read_text());v=[v for s in e['sheets']for v in s['violations']];need(len(v)==1 and v[0]['severity']=='warning'and 'VBUS_5V'in json.dumps(v),'fresh ERC unexpected')
print(json.dumps({'full_native_source_library_closure_equal':True,'reviewed_layered_rules_exact':True,'reference_chain_matches_all_native_IRQ_tracks':True,'chain_remaining_MCU_tracks':len(rest),'touched_signals_foreign_copper_overlap':hits,'IRQ_native_pinfunctions':{str(k):ns[k]for k in [('U101','6'),('U501','12')]},'ERC_errors':0,'ERC_warnings':1,'NOFAB':True},indent=2))
