from pathlib import Path
import pcbnew as p,json,hashlib
D=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(D/'baseline_12mm.kicad_pcb'))
for s in b.GetDrawings():
 if s.GetLayer()!=p.Edge_Cuts:continue
 for getter,setter in [(s.GetStart,s.SetStart),(s.GetEnd,s.SetEnd)]:
  q=getter()
  if q.x==12000000:setter(p.VECTOR2I(14000000,q.y))
for z in b.Zones():
 if z.GetNetname()!='GND':continue
 for i in range(z.Outline().OutlineCount()):
  c=z.Outline().Outline(i)
  for j in range(c.PointCount()):
   q=c.CPoint(j)
   if q.x==11500000:c.SetPoint(j,p.VECTOR2I(13500000,q.y))
r=next(f for f in b.GetFootprints() if f.GetReference()=='R105');old=[p.ToMM(r.GetPosition().x),p.ToMM(r.GetPosition().y),r.GetOrientationDegrees()];r.SetPosition(p.VECTOR2I(12500000,4500000));r.SetOrientationDegrees(90)
f=D/'power_integrated_study.kicad_pcb';p.SaveBoard(str(f),b);b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
(D/'expansion_contract.json').write_text(json.dumps({'source_12mm_sha256':hashlib.sha256((D/'baseline_12mm.kicad_pcb').read_bytes()).hexdigest(),'board_mm':[14,45,.8],'edge_only_x12_to14':True,'ground_definition_maxx11p5_to13p5':True,'SYS_zone_definition_unchanged':True,'R105_old_xyz':old,'R105_new_xyz':[12.5,4.5,90],'reason':'conditional wider routing comparison, not approved 18mm pen envelope','core_tracks_vias_untouched':True},indent=2))
