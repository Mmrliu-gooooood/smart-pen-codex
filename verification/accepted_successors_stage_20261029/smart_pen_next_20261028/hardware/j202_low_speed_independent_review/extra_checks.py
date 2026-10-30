from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E,math
import pcbnew as p
from copper_geometry import build,shape,L
from pcb_preflight import verify
D=Path(__file__).resolve().parent;B=D.parent/'j202_ground_return_candidate';f=D/'native/mainboard_revD.kicad_pcb';a=p.LoadBoard(str(B/'native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(f))
def need(x,m):
 if not x:raise RuntimeError(m)
need(hashlib.sha256(f.read_bytes()).hexdigest()=='9a0335443167a4395431cb78abfab959893060d82a7b4da9e5fcd861bc40c038','final hash')
for old in (B/'native').rglob('*'):
 if old.is_file()and old.suffix not in ['.kicad_pcb','.kicad_prl']:
  new=D/'native'/old.relative_to(B/'native');need(new.is_file()and new.read_bytes()==old.read_bytes(),'all source/library closure')
def rules(board):return{z.GetZoneName():(str(z.Outline().Format()),list(z.GetLayerSet().Seq()),z.GetDoNotAllowTracks(),z.GetDoNotAllowVias(),z.GetDoNotAllowPads(),z.GetDoNotAllowCopperPour(),z.GetDoNotAllowFootprints())for z in board.Zones()if z.GetIsRuleArea()}
need(rules(a)==rules(b),'full rules changed')
def fill(board):return{(z.m_Uuid.AsString(),int(l)):str(z.GetFilledPolysList(l).Format())for z in board.Zones()if not z.GetIsRuleArea()for l in z.GetLayerSet().Seq()}
x=fill(b);p.ZONE_FILLER(b).Fill(b.Zones());need(x==fill(b),'freshfill differs')
nets=build(b);hits=[];target=['SENS_XSHUTDN_N','SENS_TRIG_IN','SENS_SCL','SENS_SDA','SENS_VIO_1V8']
for net in target:
 for name,_,ss in nets[net]:
  for other,nodes in nets.items():
   if other==net:continue
   for on,_,oo in nodes:
    for l in ss.keys()&oo.keys():
     if not ss[l].BBox().Intersects(oo[l].BBox()):continue
     q=p.SHAPE_POLY_SET();q.BooleanIntersection(ss[l],oo[l])
     if q.Area()>1:hits.append([net,name,other,on,int(l)])
need(not hits,'five nets physical foreign overlap')
oldids={t.m_Uuid.AsString()for t in a.GetTracks()};new=[t for t in b.GetTracks()if t.m_Uuid.AsString()not in oldids];vias=[t for t in new if isinstance(t,p.PCB_VIA)];need(len(vias)==14,'via count');borehits=[];mask=[]
for t in vias:
 need(t.GetFrontTentingMode()==p.TENTING_MODE_TENTED and t.GetBackTentingMode()==p.TENTING_MODE_TENTED and t.IsTented(p.F_Cu)and t.IsTented(p.B_Cu),'native tenting')
 pos=t.GetPosition();disc=p.SHAPE_POLY_SET();disc.NewOutline()
 for k in range(256):disc.Append(round(pos.x+t.GetDrillValue()/2*math.cos(2*math.pi*k/256)),round(pos.y+t.GetDrillValue()/2*math.sin(2*math.pi*k/256)))
 for fp in b.GetFootprints():
  for pad in fp.Pads():
   for l in[p.F_Cu,p.B_Cu]:
    if pad.IsOnLayer(l):
     q=p.SHAPE_POLY_SET();q.BooleanIntersection(disc,shape(pad,l))
     if q.Area()>1:borehits.append([t.m_Uuid.AsString(),fp.GetReference(),pad.GetNumber(),int(l)])
 mask.append({'net':t.GetNetname(),'xy_mm':[pos.x/1e6,pos.y/1e6],'drill_mm':t.GetDrillValue()/1e6,'diameter_mm':t.GetWidth(p.F_Cu)/1e6})
need(not borehits,'new bore SMT pad overlap')
need(sum(t.GetDrillValue()==200000 for t in vias)==3 and all(t.GetNetname()=='SENS_XSHUTDN_N'for t in vias if t.GetDrillValue()==200000),'small-hole scope')
reset=next(t for t in vias if t.GetPosition()==p.VECTOR2I(3875000,89850000));gap=90-(reset.GetPosition().y+reset.GetDrillValue()/2)/1e6;need(abs(gap-.05)<1e-8,'edge reset via clearance')
x=E.parse(D/'fresh.xml');cs={c.get('ref'):c for c in x.findall('./components/comp')};ns={(v.get('ref'),v.get('pin')):n.get('name')for n in x.findall('./nets/net')for v in n};contract=json.loads((D/'interface_reference_contract.json').read_text())
for pin,net in contract['pins'].items():need(ns['J202',pin]==net,'source mapping')
for net,ends in contract['actual_endpoints'].items():need({(r['ref'],r['pin'])for r in ends}=={v for v,n in ns.items()if n==net},'complete actual source endpoints')
for ref,val in [('R236','4.7k'),('R237','100k'),('R242','10k'),('R243','10k')]:need(cs[ref].findtext('value').startswith(val),'bias value')
need(ns['R242','2']=='SENS_VIO_1V8'and ns['R243','2']=='SENS_VIO_1V8','pullup VIO destination')
need(ns['JP301','1']!=ns['JP301','2']and 'OPEN'in cs['JP301'].findtext('value'),'OPEN source')
try:verify(f,json.loads((D/'preflight_lock.json').read_text()),'manufacturing')
except ValueError as e:reason=str(e)
else:raise RuntimeError('manufacturing released')
print(json.dumps({'complete_source_library_rules_unchanged':True,'fresh_fill_unchanged':True,'five_complete_nets_foreign_copper_overlap':hits,'new_via_bore_SMT_pad_overlap':borehits,'all_new_vias_both_sides_tented':True,'vias':mask,'reset_via_bore_to_nominal_body_mm':gap,'five_source_endpoints_and_bias_contract_exact':True,'VIO_semantics':'External head input reference supply; no qualified external source established; never AON/local LDO output','manufacturing_rejection':reason},indent=2))
