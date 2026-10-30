from pathlib import Path
import os,json,math
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache';os.environ['XDG_DATA_HOME']='/tmp/rf-independent/data'
import pcbnew as p
from copper_geometry import shape
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));j=next(f for f in b.GetFootprints()if f.GetReference()=='J202');links=json.loads((D/'ground_links.json').read_text());items={t.m_Uuid.AsString():t for t in b.GetTracks()};vias=[]
for q in links:
 if q['via']is None:continue
 v=items[q['via']];pos=v.GetPosition();r=v.GetDrillValue()/2e6;vias.append({'pin':q['pin'],'via':q['via'],'xy_mm':[pos.x/1e6,pos.y/1e6],'diameter_mm':v.GetWidth(p.F_Cu)/1e6,'drill_mm':2*r,'explicit_front_tented':v.GetFrontTentingMode()==p.TENTING_MODE_TENTED,'explicit_back_tented':v.GetBackTentingMode()==p.TENTING_MODE_TENTED,'actual_front_is_tented':v.IsTented(p.F_Cu),'actual_back_is_tented':v.IsTented(p.B_Cu),'drill_to_nominal_body_y90_edge_mm':90-(pos.y/1e6+r)})
 for l in[p.F_Cu,p.B_Cu]:
  if not v.IsTented(l):raise RuntimeError('VIA_MASK_NOT_TENTED')
exposed=[]
for q in links:
 for u in q['tracks']:
  if items[u].HasSolderMask():exposed.append(u)
if exposed:raise RuntimeError('NEW_TRACK_HAS_EXPOSED_MASK')
bar=next(items[u]for q in links if q['pin']=='13'for u in q['tracks']if items[u].GetStart().y==91200000 and items[u].GetEnd().y==91200000);copper=shape(bar,p.B_Cu);mask=p.SHAPE_POLY_SET()
for pad in j.Pads():
 if not pad.IsOnLayer(p.B_Mask):continue
 x=shape(pad,p.B_Cu);e=pad.GetSolderMaskExpansion(p.B_Cu)
 if e:x.Inflate(e,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,250,True)
 mask.BooleanAdd(x)
inter=p.SHAPE_POLY_SET();inter.BooleanIntersection(copper,mask)
if inter.Area()>1:raise RuntimeError('INNER_GROUND_BAR_EXPOSED_IN_CONNECTOR_MASK')
lengths={q['pin']:sum(math.dist(a,z)for a,z in zip(q['path'],q['path'][1:]))for q in links};out={'status':'NATIVE_MASK_AND_CONNECTOR_GEOMETRY_SCREEN_NOT_ASSEMBLY_RELEASE','connector':'Molex 5034802400, original 24pin unchanged','closed_native_Fab_body_xy_mm':[.05,90,13.95,94],'new_vias':vias,'new_track_explicit_mask_openings':exposed,'pin13_inner_bar_intersection_with_J202_mask_mm2':inter.Area()/1e12,'pin13_shared_branch_mm':lengths['13'],'shared_pin10_to_via_mm':lengths['10'],'pin13_total_to_shared_via_mm':lengths['13']+lengths['10'],'all_branch_lengths_mm':lengths,'nominal_signal_pad_mask_gap_mm':.2,'nominal_inner_bar_to_signal_pad_mask_edge_mm':.225,'native_global_mask_expansion_mm':b.GetDesignSettings().m_SolderMaskExpansion/1e6,'native_global_mask_min_width_mm':b.GetDesignSettings().m_SolderMaskMinWidth/1e6,'gates':['Native tenting is specified but board-house tenting reliability on .30mm holes is not approved. No filled or resin-plugged vias requested.','All new drilled bores nominally outside native Fab rectangle; minimum .05mm is not a tolerance-backed physical underside clearance.','Manufacturer bottom view shows contacts/windows but lacks all underside clearance dimensions. Removing pin13 internal hole avoids relying on guessed insulation. Covered branch under connector still needs actual assembly/underside inspection.','Mask global min-width=0 is no manufacturer process claim. Native adjacent signal mask web .2mm and inner bar gap .225mm must be checked against fabrication tolerances.','Pin13 shares finite impedance with pin10; no unlimited-ground or high-frequency equivalence claim.']};(D/'connector_mask_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
