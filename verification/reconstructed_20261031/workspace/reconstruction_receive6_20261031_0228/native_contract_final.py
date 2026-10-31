from pathlib import Path
import os,json,hashlib,re
os.environ.update(XDG_CONFIG_HOME='/tmp/newreconstruct/config',XDG_CACHE_HOME='/tmp/newreconstruct/cache',XDG_DATA_HOME='/tmp/newreconstruct/data')
import pcbnew as p
D=Path(__file__).resolve().parent;a=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(D/'final_candidate/mainboard_revD.kicad_pcb'))
def drawings(q):return sorted((d.GetLayer(),str(d.GetShape()),d.GetStart().x,d.GetStart().y,d.GetEnd().x,d.GetEnd().y,d.GetWidth())for d in q.GetDrawings() if d.GetLayer()==p.Edge_Cuts)
def zones(q):
 out=[]
 for owner,z in [('board',z)for z in q.Zones()]+[(f.GetReference(),z)for f in q.GetFootprints()for z in f.Zones()]:
  poly=z.Outline();verts=[[(poly.Outline(i).CPoint(k).x,poly.Outline(i).CPoint(k).y)for k in range(poly.Outline(i).PointCount())]for i in range(poly.OutlineCount())]
  out.append([owner,z.GetNetname(),z.GetLayer(),z.GetIsRuleArea(),z.GetDoNotAllowTracks(),z.GetDoNotAllowVias(),z.GetDoNotAllowCopperPour(),verts])
 return out
checks={'all_drawings_outline_exact':drawings(a)==drawings(b),'all_zone_definitions_and_footprint_keepout_flags_exact':zones(a)==zones(b),'native_board_thickness_exact':a.GetDesignSettings().GetBoardThickness()==b.GetDesignSettings().GetBoardThickness(),'project_rule_files_exact':True}
for f in (D/'native').iterdir():
 if f.is_file()and f.suffix in ['.kicad_pro','.kicad_dru','.kicad_sch','.kicad_sym']:
  t=D/'final_candidate'/f.name
  if not t.exists()or f.read_bytes()!=t.read_bytes():checks['project_rule_files_exact']=False
r={'checks':checks,'zone_contract':zones(b),'board_thickness_mm':b.GetDesignSettings().GetBoardThickness()/1e6,'stackup_note':'No stackup or rule changes. Existing supplier-null stackup remains unqualified; In2 new signals explicitly occupy mixed AON layer, dominant adjacent GND In1.'};(D/'final_native_contract.json').write_text(json.dumps(r,indent=2));print(json.dumps(checks));
if not all(checks.values()):raise RuntimeError('contract failure')
