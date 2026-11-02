"""Read-only current-native candidate topology checks with temporary output."""
from pathlib import Path
import subprocess,tempfile
D=Path(__file__).resolve().parent;R=D.parents[1]
main=R/'hardware/mainboard_wip_20261102/candidate/mainboard_revD.kicad_pcb'
power=R/'hardware/power14_single_feed_revB/power_integrated_study.kicad_pcb'
with tempfile.TemporaryDirectory(prefix='pen_return_current_')as t:
 t=Path(t)
 for opt in[[],['-O']]:
  out=t/('optimized.json'if opt else'normal.json')
  q=subprocess.run(['/usr/bin/python3']+opt+[str(D/'check.py'),'--main',str(main),'--power',str(power),'--output',str(out)],capture_output=True,text=True)
  print(q.stdout)
  if q.returncode:raise RuntimeError(q.stderr)
 if (t/'normal.json').read_bytes()!=(t/'optimized.json').read_bytes():raise RuntimeError('Normal/-O mismatch')
 print('PASS: current-native logical candidate only, not final harness or safety qualification.')
