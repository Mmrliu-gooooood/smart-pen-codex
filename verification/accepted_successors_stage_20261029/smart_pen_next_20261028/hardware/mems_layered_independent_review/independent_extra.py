from pathlib import Path
import json,hashlib,re
import pcbnew as p
from finite_shapes import shape,L
D=Path(__file__).resolve().parent;B=D.parent/'j107_mode_port_closure';f=D/'native/mainboard_revD.kicad_pcb';a=p.LoadBoard(str(B/'native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(f))
def need(v,s):
 if not v:raise RuntimeError(s)
need(hashlib.sha256(f.read_bytes()).hexdigest()=='619a1307b7eb18c27d34f323e511726d95b373cca4e4dd2c11e284f03501eaf0','candidate hash')
# Serialized conductor blocks cannot be silently normalized on load.
def blocks(path,kind):return re.findall(r'\n\t\('+kind+r'\n.*?\n\t\)',path.read_text(),re.S)
for k in ['segment','via','footprint']:need(blocks(f,k)==blocks(B/'native/mainboard_revD.kicad_pcb',k),'raw object mismatch '+k)
# Exact immutable source/library/project closure.
for old in (B/'native').rglob('*'):
 if old.is_file() and old.suffix not in ['.kicad_pcb','.kicad_prl']:
  new=D/'native'/old.relative_to(B/'native');need(new.is_file() and new.read_bytes()==old.read_bytes(),'source closure '+str(old))
# Fill must regenerate exactly using native matching project.
def fill(board):return{(z.m_Uuid.AsString(),int(l)):str(z.GetFilledPolysList(l).Format())for z in board.Zones()if not z.GetIsRuleArea()for l in z.GetLayerSet().Seq()}
oldfill=fill(b);p.ZONE_FILLER(b).Fill(b.Zones());need(oldfill==fill(b),'fresh refill differs')
rules={z.GetZoneName():z for z in b.Zones()if z.GetIsRuleArea()};body=rules['LIS2DW12_F_BODY_NO_POUR_OR_THROUGH_VIA'].Outline();center=rules['LIS2DW12_F_CENTRAL_NO_TRACK_PROJECT_SCREEN'].Outline()
u=next(x for x in b.GetFootprints()if x.GetReference()=='U501');pads=[]
for pad in u.Pads():
 box=shape(pad,p.F_Cu).BBox();pads.append({'pin':pad.GetNumber(),'net':pad.GetNetname(),'bounds_nm':[box.GetX(),box.GetY(),box.GetRight(),box.GetBottom()]})
# Body peripheral copper is deliberately outside central enforcement; enumerate, not hide.
peripheral=[]
for t in b.GetTracks():
 if not t.IsOnLayer(p.F_Cu):continue
 q=shape(t,p.F_Cu);clip=p.SHAPE_POLY_SET();clip.BooleanIntersection(q,body)
 if clip.Area()>1:
  c=p.SHAPE_POLY_SET();c.BooleanIntersection(q,center)
  peripheral.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'type':t.GetClass(),'body_overlap_mm2':clip.Area()/1e12,'central_overlap_mm2':c.Area()/1e12,'start_mm':[t.GetStart().x/1e6,t.GetStart().y/1e6],'end_mm':[t.GetEnd().x/1e6,t.GetEnd().y/1e6]})
need(all(v['central_overlap_mm2']<=1e-12 for v in peripheral),'peripheral intrusion')
# Full rule flags outside MEMS unchanged, including pads/footprints, not partial checks.
def rule(z):return(str(z.Outline().Format()),list(z.GetLayerSet().Seq()),z.GetDoNotAllowTracks(),z.GetDoNotAllowVias(),z.GetDoNotAllowPads(),z.GetDoNotAllowCopperPour(),z.GetDoNotAllowFootprints())
for z in a.Zones():
 if z.GetIsRuleArea() and 'LIS2DW12'not in z.GetZoneName():need(rule(z)==rule(rules[z.GetZoneName()]),'outside rule full flags changed')
print(json.dumps({'candidate_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'raw_segments_vias_footprints_identical':True,'all_source_library_project_bytes_identical':True,'fresh_fill_identical':True,'U501_pad_bounds':pads,'peripheral_F_copper_under_body_manual_gate':peripheral,'peripheral_object_count':len(peripheral),'other_rule_flags_all_identical':True,'limits':'Central screen not manufacturer full same-side approval. Peripheral list must remain manual gate; inner plane permission engineering inference.'},indent=2))
