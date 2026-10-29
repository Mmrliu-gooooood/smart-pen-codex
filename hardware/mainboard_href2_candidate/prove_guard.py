from pathlib import Path
import json,subprocess,hashlib,sys
D=Path(__file__).resolve().parent;O=D/'guard_proof';O.mkdir(exist_ok=False);expected=json.loads((D/'new_copper_expected.json').read_text());uid=next(iter(expected));bad=dict(expected);bad[uid]='INTENTIONAL_WRONG_NET';missing={'00000000-0000-0000-0000-000000000000':'CAM_D7'}
for name,contents in [('good',json.dumps(expected)),('bad',json.dumps(bad)),('empty','{}'),('missing',json.dumps(missing)),('duplicate','{"'+uid+'":"CAM_D7","'+uid+'":"GND"}')]: (O/(name+'.json')).write_text(contents)
rows=[]
for optimize in [False,True]:
 for name in ['good','bad','empty','missing','duplicate']:
  tag=name+('_optimized' if optimize else '_normal');marker=O/(tag+'.marker');report=O/(tag+'.rpt');command=f'''#!/bin/bash\nset -euo pipefail\n/usr/bin/python3 {'-O ' if optimize else ''}{D}/validate_expected.py {D}/mainboard_revD.kicad_pcb {O}/{name}.json\nprintf passed > {marker}\nkicad-cli pcb drc --exit-code-violations --all-track-errors --schematic-parity -o {report} {D}/mainboard_revD.kicad_pcb\n''';sh=O/(tag+'.sh');sh.write_text(command);result=subprocess.run(['bash',str(sh)],capture_output=True,text=True);(O/(tag+'.stdout')).write_text(result.stdout);(O/(tag+'.stderr')).write_text(result.stderr);good=name=='good';passed=(result.returncode==5 and marker.exists() and report.exists()) if good else (result.returncode!=0 and not marker.exists() and not report.exists());rows.append({'case':tag,'exit':result.returncode,'post_guard_marker':marker.exists(),'fresh_drc':report.exists(),'expected_outcome':passed})
  if not passed:raise RuntimeError('fail-closed proof failed: '+tag)
r={'candidate_sha256':hashlib.sha256((D/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'validator_sha256':hashlib.sha256((D/'validate_expected.py').read_bytes()).hexdigest(),'cases':rows,'all_expected':True};(O/'proof.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
