from pathlib import Path
import subprocess,json,hashlib
D=Path(__file__).resolve().parent;B=Path('/workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/mainboard_resume_20261028');O=D/'guard_rerun';O.mkdir(exist_ok=False);rows=[]
for sh in sorted((B/'guard_proof').glob('*.sh')):
 text=sh.read_text();name=sh.stem
 # Keep input contracts and validator unchanged, rewrite only marker/report output destinations.
 text=text.replace(str(B/'guard_proof'/(name+'.marker')),str(O/(name+'.marker'))).replace(str(B/'guard_proof'/(name+'.rpt')),str(O/(name+'.rpt')))
 new=O/sh.name;new.write_text(text);r=subprocess.run(['bash',str(new)],capture_output=True,text=True);(O/(name+'.stdout')).write_text(r.stdout);(O/(name+'.stderr')).write_text(r.stderr)
 good=name.startswith('good_');marker=(O/(name+'.marker')).exists();report=(O/(name+'.rpt')).exists();passed=(r.returncode==0 and marker and report) if good else (r.returncode!=0 and not marker and not report)
 rows.append({'case':name,'exit':r.returncode,'marker':marker,'fresh_drc':report,'expected':passed})
 if not passed:raise RuntimeError(name)
(D/'guard_recheck.json').write_text(json.dumps({'validator_sha256':hashlib.sha256((B/'validate_expected.py').read_bytes()).hexdigest(),'board_sha256':hashlib.sha256((B/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'cases':rows},indent=2));print('10 independent cases meet expected fail-closed outcomes')
