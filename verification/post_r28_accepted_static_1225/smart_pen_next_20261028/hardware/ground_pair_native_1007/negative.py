from pathlib import Path
import subprocess,sys,json
D=Path(__file__).resolve().parent;rows=[]
for target in ['R219.2','R229.2','BOTH']:
 cmd=[sys.executable]+(['-O']if sys.flags.optimize else[])+[str(D/'cut_one.py'),target];r=subprocess.run(cmd,capture_output=True,text=True);(D/('negative_'+target+('_O'if sys.flags.optimize else'')+'.log')).write_text(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError('isolated cut failed '+target)
 rows.append(json.loads((D/'negative_cuts'/target/'result.json').read_text()))
(D/('negative_optimized.json'if sys.flags.optimize else'negative.json')).write_text(json.dumps({'status':'THREE_REAL_NATIVE_GROUND_CUTS_TEST_SPECIMENS_NOFAB','cuts':rows},indent=2)+'\n');print('three isolated cuts pass')
