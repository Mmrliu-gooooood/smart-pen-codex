from pathlib import Path
import os,json,subprocess,tempfile
os.environ['XDG_CONFIG_HOME']='/tmp/pen-layout-config'
import pcbnew as p
D=Path(__file__).resolve().parent;results=[]
for case,reason in [('move_J301','FOOTPRINT_CHANGE'),('thin_AON','UNRELATED_MODIFICATION')]:
 for opt in [False,True]:
  b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'))
  if case=='move_J301':
   f=next(f for f in b.GetFootprints()if f.GetReference()=='J301');a=f.GetPosition();f.SetPosition(p.VECTOR2I(a.x+100000,a.y))
  else:
   t=next(t for t in b.GetTracks()if not isinstance(t,p.PCB_VIA)and t.GetNetname()=='3V3_AON');t.SetWidth(t.GetWidth()-10000)
  with tempfile.TemporaryDirectory(prefix='pen_low_negative_',dir='/tmp')as td:
   q=Path(td)/'bad.kicad_pcb';p.SaveBoard(str(q),b);cmd=['/usr/bin/python3']+(['-O']if opt else[])+[str(D/'verify.py'),str(q)];r=subprocess.run(cmd,capture_output=True,text=True);log=r.stdout+r.stderr
   (D/f'negative_{case}_{"O"if opt else"normal"}.log').write_text(log)
   if r.returncode==0 or reason not in log:raise RuntimeError('NEGATIVE_NOT_REJECTED '+case)
   results.append({'case':case,'optimized':opt,'exit':r.returncode,'expected_failure':reason})
(D/'negative_results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
