from pathlib import Path
import pcbnew as p,json
D=Path(__file__).resolve().parents[1];fn=D/'power_integrated_study.kicad_pcb';b=p.LoadBoard(str(fn));fs={f.GetReference():f for f in b.GetFootprints()};changes=[]
def move(r,x,y,angle):
 f=fs[r];changes.append({'ref':r,'old':[p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y),f.GetOrientationDegrees()],'new':[x,y,angle]});f.SetPosition(p.VECTOR2I(round(x*1e6),round(y*1e6)));f.SetOrientationDegrees(angle)
move('R103',12.5,30,90);move('U104',12.35,16,90)
p.SaveBoard(str(fn),b);b=p.LoadBoard(str(fn));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(fn),b);(D/'local_changes.json').write_text(json.dumps(changes,indent=2))
