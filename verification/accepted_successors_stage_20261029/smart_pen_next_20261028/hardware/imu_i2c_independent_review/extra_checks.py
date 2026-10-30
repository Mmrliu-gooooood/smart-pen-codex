from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E
import pcbnew as p
from copper_geometry import build,L
from pcb_preflight import verify
D=Path(__file__).resolve().parent;B=D.parent/'imu_irq_layered_candidate';f=D/'native/mainboard_revD.kicad_pcb';a=p.LoadBoard(str(B/'native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(f))
def need(x,m):
 if not x:raise RuntimeError(m)
need(hashlib.sha256(f.read_bytes()).hexdigest()=='6b44e149edf7e3b6c843375125a71247ece6c664eb531686dd3b451e1586ee71','final hash')
for old in (B/'native').rglob('*'):
 if old.is_file()and old.suffix not in ['.kicad_pcb','.kicad_prl']:
  new=D/'native'/old.relative_to(B/'native');need(new.is_file()and new.read_bytes()==old.read_bytes(),'complete source/library closure')
def rules(board):return{z.GetZoneName():(str(z.Outline().Format()),list(z.GetLayerSet().Seq()),z.GetDoNotAllowTracks(),z.GetDoNotAllowVias(),z.GetDoNotAllowPads(),z.GetDoNotAllowCopperPour(),z.GetDoNotAllowFootprints())for z in board.Zones()if z.GetIsRuleArea()}
need(rules(a)==rules(b),'full rule flags/outline changed')
def fill(board):return{(z.m_Uuid.AsString(),int(l)):str(z.GetFilledPolysList(l).Format())for z in board.Zones()if not z.GetIsRuleArea()for l in z.GetLayerSet().Seq()}
x=fill(b);p.ZONE_FILLER(b).Fill(b.Zones());need(x==fill(b),'fresh refill changes final fill')
names=['AON_I2C_SCL','AON_I2C_SDA','CAM_D0','CAM_D7','CAM_PWDN_UART_RX']
def intersections(board):
 nets=build(board);hits=set()
 for net in names:
  for name,_,ss in nets[net]:
   for other,nodes in nets.items():
    if other==net:continue
    for on,_,oo in nodes:
     for l in ss.keys()&oo.keys():
      if not ss[l].BBox().Intersects(oo[l].BBox()):continue
      q=p.SHAPE_POLY_SET();q.BooleanIntersection(ss[l],oo[l])
      if q.Area()>1:hits.add((net,name,other,on,int(l)))
 return hits
oldhits=intersections(a);hits=intersections(b);need(not hits-oldhits,'new touched-net actual short '+str(hits-oldhits))
need(not any(v[0].startswith('AON_I2C')for v in hits),'I2C actual foreign overlap')
x=E.parse(D/'fresh.xml');ns={(v.get('ref'),v.get('pin')):(n.get('name'),v.get('pinfunction'))for n in x.findall('./nets/net')for v in n}
for pin,func,net,imu,r in [('10','GPIO5','AON_I2C_SCL','1','R501'),('11','GPIO6','AON_I2C_SDA','4','R502')]:
 need(ns['U101',pin]==(net,func)and ns['U501',imu][0]==net and ns[r,'2'][0]==net,'real source bus pins')
 c=next(c for c in x.findall('./components/comp')if c.get('ref')==r);need(c.findtext('value')=='10k 1%','pullup changed')
v=[t for t in b.GetTracks()if isinstance(t,p.PCB_VIA)and t.GetNetname()=='AON_I2C_SDA'and t.GetPosition()==p.VECTOR2I(5200000,1350000)];need(len(v)==1,'final RF-adjacent via position')
try:verify(f,json.loads((D/'preflight_lock.json').read_text()),'manufacturing')
except ValueError as e:reason=str(e)
else:raise RuntimeError('Manufacturing release')
print(json.dumps({'final_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'source_library_tree_identical':True,'full_rule_contract_identical':True,'fresh_fill_identical':True,'I2C_source_GPIO5_GPIO6_independent_three_terminal_10k':True,'new_touched_signal_foreign_overlaps':[],'retained_touched_signal_foreign_overlaps':sorted(hits),'baseline_touched_signal_foreign_overlaps':sorted(oldhits),'RF_top_SDA_via_mm':[5.2,1.35],'manufacturing_rejection':reason},indent=2))
