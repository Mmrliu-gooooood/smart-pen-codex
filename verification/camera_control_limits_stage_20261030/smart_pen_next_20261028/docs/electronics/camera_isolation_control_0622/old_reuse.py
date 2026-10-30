import geometry as g,json
from pathlib import Path
p=g.p
old=p.LoadBoard(str(g.R/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb'))
out={}
for n in ['CAM_ISO_OE_N','CAM_IO_EN','IO_ENABLE_LINK']:
 ts=[t for t in old.GetTracks()if t.GetNetname()==n]
 out[n]={'objects':len(ts),'errors':g.errors(ts)}
print(json.dumps(out,indent=2))
