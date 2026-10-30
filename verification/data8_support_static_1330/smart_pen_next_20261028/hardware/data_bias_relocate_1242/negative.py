from pathlib import Path
import subprocess,sys,json
D=Path(__file__).resolve().parent;rows=[]
for target in (['CAM_D'+str(i)for i in range(8)]+['ALL8','R210_GND_VIA','R217_GND_VIA']):
 r=subprocess.run([sys.executable]+(['-O']if sys.flags.optimize else[])+[str(D/'cut_one.py'),target],capture_output=True,text=True);(D/('negative_'+target+('_O'if sys.flags.optimize else'')+'.log')).write_text(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError('negative failed '+target)
 rows.append(json.loads((D/'negative_cuts'/target/'result.json').read_text()))
print(json.dumps({'status':'ELEVEN_ACTUAL_NATIVE_CUT_TESTS_ONLY','cuts':rows},indent=2))
