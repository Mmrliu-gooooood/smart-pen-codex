from pathlib import Path
import os,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/pen-erosion-erratum2321'
import pcbnew as p
from native_polygon import native_fractured_once
D=Path(__file__).resolve().parent;R=D.parents[2];rows=[]
for name in ['power_zone_freshfill_candidate_2150','aon_entry_bridge_candidate_2156','gnd_fixed_branch_candidate_2159','gnd_conservative_recovery_2305']:
 f=R/'hardware'/name/'native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f));before=hashlib.sha256(f.read_bytes()).hexdigest()
 for z in b.Zones():
  if z.GetIsRuleArea():continue
  for l in z.GetLayerSet().Seq():
   raw=p.SHAPE_POLY_SET(z.GetFilledPolysList(l));norm=native_fractured_once(raw);difference=p.SHAPE_POLY_SET();difference.BooleanSubtract(norm,raw);reverse=p.SHAPE_POLY_SET();reverse.BooleanSubtract(raw,norm)
   a=p.SHAPE_POLY_SET(raw);a.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000);n=p.SHAPE_POLY_SET(norm);n.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000)
   rows.append(dict(candidate=name,pcb_sha256=before,zone_uuid=z.m_Uuid.AsString(),net=z.GetNetname(),layer=b.GetLayerName(l),raw_outlines=raw.OutlineCount(),raw_holes=sum(raw.HoleCount(i)for i in range(raw.OutlineCount())),unfractured_outlines=norm.OutlineCount(),unfractured_holes=sum(norm.HoleCount(i)for i in range(norm.OutlineCount())),area_difference_mm2=(norm.Area()-raw.Area())/1e12,boolean_norm_minus_raw_mm2=difference.Area()/1e12,boolean_raw_minus_norm_mm2=reverse.Area()/1e12,erosion_radius_mm=.25,raw_eroded_pieces=a.OutlineCount(),normalized_eroded_pieces=n.OutlineCount(),raw_eroded_area_mm2=a.Area()/1e12,normalized_eroded_area_mm2=n.Area()/1e12))
 if hashlib.sha256(f.read_bytes()).hexdigest()!=before:raise RuntimeError('input mutated')
print(json.dumps(dict(status='CORRECTION_OF_RAW_FRACTURED_POLYGON_EROSION_SCREEN_ONLY',kicad_version=p.Version(),rows=rows,limits=['Unfracture changes hole encoding, not the native PCB or DRC.','Numerical polygon differences recorded; no claim of exact set equality.','A single normalized eroded component is not load-path width, ampacity, return-current or thermal qualification.','No rejected ground branch automatically reinstated.']),indent=2))
