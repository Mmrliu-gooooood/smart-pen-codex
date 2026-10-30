from pathlib import Path
import os,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/indesccb_extra';import pcbnew as p
O=Path(__file__).resolve().parent;W=O.parent;H=W/'smart_pen_next_20261028/hardware';b=p.LoadBoard(str(H/'data_bias_relocate_1242/native/mainboard_revD.kicad_pcb'));old=p.LoadBoard(str(H/'sccb_local_reference_1216/native/mainboard_revD.kicad_pcb'))
def req(x,msg):
 if not x:raise RuntimeError(msg)
def extra(f):return sorted([(z.GetNumber(),int(z.GetAttribute()),z.GetDrillSize().x,z.GetDrillSize().y,int(z.GetDrillShape()),z.GetOffset().x,z.GetOffset().y,z.GetRoundRectRadiusRatio())for z in f.Pads()])
req({f.GetReference():extra(f)for f in b.GetFootprints()}=={f.GetReference():extra(f)for f in old.GetFootprints()},'extra pad changed');req(len(list(b.GetFootprints()))==103,'103')
es=[e for e in b.GetDrawings()if e.GetLayer()==p.Edge_Cuts];req(len(es)==6 and all(e.GetShapeStr()=='Line'for e in es),'6lines');ends={}
for e in es:
 for v in [e.GetStart(),e.GetEnd()]:ends[(v.x,v.y)]=ends.get((v.x,v.y),0)+1
req(all(n==2 for n in ends.values()),'closed outline');bounds=[min(x for x,y in ends)/1e6,min(y for x,y in ends)/1e6,max(x for x,y in ends)/1e6,max(y for x,y in ends)/1e6];req(bounds==[0,-6.5,14,93.3],'bounds')
def ident(t):return(t.GetClass(),t.GetNetname(),t.GetLayerName(),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None)
oldset={ident(t)for t in old.GetTracks()};new=[t for t in b.GetTracks()if ident(t)not in oldset];vias=sum(isinstance(t,p.PCB_VIA)for t in new);outer=sum(not isinstance(t,p.PCB_VIA)and t.GetLayer()in [p.F_Cu,p.B_Cu]for t in new);inner=len(new)-vias-outer;req((vias,outer,inner)==(11,32,7),'counts')
cads=[]
for c in json.load(open(W/'assembly_context_audit_0818_20261030/inventory.json'))['contexts']:
 h=hashlib.sha256(Path(c['path']).read_bytes()).hexdigest();req(h==c['sha256'],'CAD source');cads.append({'context':c['context'],'sha256':h})
(O/'native_extra.json').write_text(json.dumps({'additional_pad_contract_equal':True,'103refs':True,'closed_six_segment_outline':bounds,'outer_tracks':outer,'inner_tracks':inner,'new_vias':vias,'cad_sources':cads},indent=2)+'\n')
print('Native extra checks pass:103,closed14x99.8,32outer7inner11vias,CAD sources')
