from pathlib import Path
import os,json
os.environ['XDG_CONFIG_HOME']='/tmp/pen-layout-config'
import pcbnew as p
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D.parent/'j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb'))
refs={f.GetReference():f for f in b.GetFootprints()}
for ref in ['U201','U202','U203']:
 f=refs[ref];f.SetOrientationDegrees(-90)
 print(ref)
 for q in f.Pads():
  print(q.GetNumber(),q.GetNetname(),[q.GetPosition().x/1e6,q.GetPosition().y/1e6])
