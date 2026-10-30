from pathlib import Path
import os,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/tail100'
import pcbnew as p
O=Path(__file__).resolve().parent;W=O.parents[1];src=W/'smart_pen_next_20261028/hardware/ground_recovery_native_0818/native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(src));f=next(f for f in b.GetFootprints()if f.GetReference()=='J202');pads=[]
for x in f.Pads():
 bb=x.GetBoundingBox();pads.append({'pad':x.GetNumber(),'net':x.GetNetname(),'bounds_mm':[bb.GetX()/1e6,bb.GetY()/1e6,bb.GetRight()/1e6,bb.GetBottom()/1e6]})
rows=[]
for tail,shift in [(93.5,0),(93.3,0),(93.5,1.5),(93.3,1.7)]:
 rows.append({'tail_edge_y':tail,'board_length':tail+6.5,'shift':shift,'mount_pad_to_edge_mm':tail-(93.65-shift),'body_to_edge_mm':tail-(94-shift),'retained_open_budget_to_edge_mm':tail-(95-shift),'note':'negative = clipped/outside; retained open operating envelope need not sit over substrate but must clear enclosure/FFC'})
r={'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'J202_pads':pads,'cases':rows,'source_unmodified':True}
(O/'native_limits.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
