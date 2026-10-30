from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E,math
import pcbnew as p
from copper_geometry import build,shape,L
from pcb_preflight import verify
D=Path(__file__).resolve().parent;B=D.parent/'imu_i2c_completed_candidate';f=D/'native/mainboard_revD.kicad_pcb';a=p.LoadBoard(str(B/'native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(f))
def need(x,m):
 if not x:raise RuntimeError(m)
need(hashlib.sha256(f.read_bytes()).hexdigest()=='4994ba2d8810b2f44434bd43f7cecfaab16aa601a0837c9923883613583554f6','final hash')
for old in (B/'native').rglob('*'):
 if old.is_file()and old.suffix not in ['.kicad_pcb','.kicad_prl']:
  new=D/'native'/old.relative_to(B/'native');need(new.is_file()and new.read_bytes()==old.read_bytes(),'all source/library closure')
def rules(board):return{z.GetZoneName():(str(z.Outline().Format()),list(z.GetLayerSet().Seq()),z.GetDoNotAllowTracks(),z.GetDoNotAllowVias(),z.GetDoNotAllowPads(),z.GetDoNotAllowCopperPour(),z.GetDoNotAllowFootprints())for z in board.Zones()if z.GetIsRuleArea()}
need(rules(a)==rules(b),'full rule flags changed')
def fill(board):return{(z.m_Uuid.AsString(),int(l)):str(z.GetFilledPolysList(l).Format())for z in board.Zones()if not z.GetIsRuleArea()for l in z.GetLayerSet().Seq()}
x=fill(b);p.ZONE_FILLER(b).Fill(b.Zones());need(x==fill(b),'freshfill changed')
oldids={t.m_Uuid.AsString()for t in a.GetTracks()};new=[t for t in b.GetTracks()if t.m_Uuid.AsString()not in oldids];nets=build(b);hits=[];borepads=[];bodygap=[]
for t in new:
 for other,nodes in nets.items():
  if other=='GND':continue
  for on,_,oo in nodes:
   for l in oo:
    if not t.IsOnLayer(l):continue
    s=shape(t,l)
    if not s.BBox().Intersects(oo[l].BBox()):continue
    q=p.SHAPE_POLY_SET();q.BooleanIntersection(s,oo[l])
    if q.Area()>1:hits.append([t.m_Uuid.AsString(),other,on,int(l)])
 if isinstance(t,p.PCB_VIA):
  need(t.GetFrontTentingMode()==p.TENTING_MODE_TENTED and t.GetBackTentingMode()==p.TENTING_MODE_TENTED and t.IsTented(p.F_Cu)and t.IsTented(p.B_Cu),'native tenting')
  pos=t.GetPosition();gap=90-(pos.y+t.GetDrillValue()/2)/1e6;bodygap.append(gap);need(gap>=.049999,'body bore margin')
  disc=p.SHAPE_POLY_SET();disc.NewOutline()
  for k in range(256):disc.Append(round(pos.x+t.GetDrillValue()/2*math.cos(2*math.pi*k/256)),round(pos.y+t.GetDrillValue()/2*math.sin(2*math.pi*k/256)))
  for fp in b.GetFootprints():
   for pad in fp.Pads():
    for l in [p.F_Cu,p.B_Cu]:
     if not pad.IsOnLayer(l):continue
     q=p.SHAPE_POLY_SET();q.BooleanIntersection(disc,shape(pad,l))
     if q.Area()>1:borepads.append([t.m_Uuid.AsString(),fp.GetReference(),pad.GetNumber(),int(l)])
need(not hits,'new GND foreign net actual overlap');need(not borepads,'new drill intersects actual SMT pad')
x=E.parse(D/'fresh.xml');ns={(v.get('ref'),v.get('pin')):n.get('name')for n in x.findall('./nets/net')for v in n};gp={pin for(ref,pin),net in ns.items()if ref=='J202'and net=='GND'};need(gp=={'1','4','7','10','13','17','24'},'source ground pin set')
j=next(fp for fp in b.GetFootprints()if fp.GetReference()=='J202');need(len([pad for pad in j.Pads()if pad.GetNumber().isdigit()])==24,'not 24pin')
try:verify(f,json.loads((D/'preflight_lock.json').read_text()),'manufacturing')
except ValueError as e:reason=str(e)
else:raise RuntimeError('Manufacturing released')
print(json.dumps({'source_library_rules_identical':True,'freshfill_identical':True,'new_ground_foreign_copper_overlap':hits,'new_bores_actual_SMT_pad_overlap':borepads,'new_via_bore_to_nominal_body_gap_mm':bodygap,'explicit_both_surface_tenting_verified':True,'J202_exact_native_GND_pins':sorted(gp),'manufacturing_rejected':reason,'warning':'Fab rectangle/nominal mask not underside metal tolerance qualification; shared pin13/pin10 ground remains finite impedance.'},indent=2))
