from pathlib import Path
import os,json
os.environ['XDG_CONFIG_HOME']='/tmp/pen-layout-config'
import pcbnew as p
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D.parent/'j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb'))
rows=[]
for name,ref in [('F.Cu',p.In1_Cu),('In3.Cu',p.In4_Cu),('B.Cu',p.In4_Cu)]:
 q=p.SHAPE_POLY_SET()
 for z in b.Zones():
  if not z.GetIsRuleArea() and z.GetNetname()=='GND' and z.IsOnLayer(ref):q.BooleanAdd(z.GetFilledPolysList(ref))
 for x in [12.6,12.9,13.2,13.5]:
  gaps=[];start=None
  for i in range(5701):
   y=32+i*.01;inside=q.Contains(p.VECTOR2I(round(x*1e6),round(y*1e6)))
   if not inside and start is None:start=y
   if inside and start is not None:gaps.append([start,y]);start=None
  if start is not None:gaps.append([start,89])
  rows.append({'layer':name,'reference':b.GetLayerName(ref),'x':x,'centerline_missing_intervals_mm':gaps,'max_sampled_gap_mm':max([z-a for a,z in gaps],default=0)})
(D/'reference.json').write_text(json.dumps({'status':'READONLY_CACHED_FILL_SCREEN_ONLY_NOT_SI_QUALIFICATION','sampling_mm':.01,'vias_and_layer_change_returns':'not designed; existing drill cutouts are not subtracted in this screening','lanes':rows},indent=2)+'\n');print(json.dumps(rows,indent=2))
