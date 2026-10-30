from pathlib import Path
import os,subprocess,json,shutil
from materialize import D,BASE,req,children
replay=D/'replay/native'
env={**os.environ,'PRESSURE_NATIVE_OUTPUT':str(replay)}
r=subprocess.run(['python',str(D/'materialize.py')],env=env,capture_output=True,text=True);req(r.returncode==0,'replay materialize');(D/'replay/materialize.log').write_text(r.stdout+r.stderr)
for p in (D/'native').rglob('*'):
 if p.is_file():req(p.read_bytes()==(replay/p.relative_to(D/'native')).read_bytes(),'replay exact '+str(p))
negative=D/'native_negative/pcb_value_only_100k';shutil.copytree(D/'native',negative,dirs_exist_ok=True)
p=negative/'mainboard_revD.kicad_pcb';s=p.read_text()
for a,b,block in children(s):
 if block.startswith('(footprint ') and '(property "Reference" "R503"' in block:
  req('(property "Value" "47k 1%"' in block,'negative source');s=s[:a]+block.replace('(property "Value" "47k 1%"','(property "Value" "100k 1%"')+s[b:];break
else:raise RuntimeError('R503 missing')
p.write_text(s)
out=D/'checks/negative_pcb_value_only_100k';out.mkdir(exist_ok=True)
cmd=['kicad-cli','pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','-o',str(out/'drc.json'),str(p)]
r=subprocess.run(cmd,capture_output=True,text=True);(out/'drc.log').write_text(r.stdout+r.stderr)
j=json.loads((out/'drc.json').read_text());req(r.returncode==5,'negative return5');req(len(j['schematic_parity'])>=1,'negative parity caught');req(any('R503' in str(v) for v in j['schematic_parity']),'negative R503 parity caught')
result=dict(replay_all_native_bytes_equal=True,negative_name='PCB R503 100k versus schematic 47k',negative_returncode=r.returncode,negative_counts=[len(j[k]) for k in ['violations','unconnected_items','schematic_parity']],command=cmd)
(D/'replay_and_negative.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
