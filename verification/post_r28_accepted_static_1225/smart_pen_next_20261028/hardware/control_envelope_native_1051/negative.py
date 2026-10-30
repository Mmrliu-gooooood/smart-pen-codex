from pathlib import Path
import subprocess,sys,json
D=Path(__file__).resolve().parent;rows=[]
for target in ['CAM_PWDN_UART_RX','CAM_RESET_UART_TX','BOTH','VIA_CAM_RESET_UART_TX','VIA_CAM_PWDN_UART_RX']:
 cmd=[sys.executable]+(['-O']if sys.flags.optimize else[])+[str(D/'cut_one.py'),target];r=subprocess.run(cmd,capture_output=True,text=True);(D/('negative_'+target+('_O'if sys.flags.optimize else'')+'.log')).write_text(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError('isolated cut failed '+target)
 rows.append(json.loads((D/'negative_cuts'/target/'result.json').read_text()))
(D/('negative_optimized.json'if sys.flags.optimize else'negative.json')).write_text(json.dumps({'status':'FIVE_REAL_NATIVE_CONTROL_BIAS_CUTS_TEST_SPECIMENS_NOFAB','cuts':rows},indent=2)+'\n');print('five isolated cuts pass')
