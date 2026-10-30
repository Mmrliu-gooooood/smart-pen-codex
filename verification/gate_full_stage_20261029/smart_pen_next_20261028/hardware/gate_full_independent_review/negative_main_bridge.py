from pathlib import Path
import json,re,subprocess,hashlib
D=Path(__file__).resolve().parent;O=D/'guard_boards';O.mkdir(exist_ok=True);pcb=D/'native_snapshot/mainboard_revD.kicad_pcb';rows=json.loads((D.parent/'gate_control_output_candidate/new_routes.json').read_text());ids={r['uuid']for r in rows if r['net']=='3V3_AON'and r['type']=='track'and r['width']==.5}
if not ids:raise RuntimeError('No designated load bridge')
raw=re.sub(r'\n\t\(segment\n.*?\n\t\)',lambda m:''if any(u in m[0]for u in ids)else m[0],pcb.read_text(),flags=re.S);f=O/'without_main_bridge.kicad_pcb';f.write_text(raw);out=[]
for opt in [[],['-O']]:
 r=subprocess.run(['/usr/bin/python3']+opt+[str(D/'main_feed.py'),str(f)],capture_output=True,text=True)
 if r.returncode!=1 or 'Main AON needs the removed thin pull-up branch'not in r.stderr:raise RuntimeError('Missing main bridge was not rejected by real load topology '+r.stderr)
 out.append({'optimized':bool(opt),'exit':r.returncode,'expected_error':'Main AON needs the removed thin pull-up branch','removed_main_bridge_track_UUIDs':sorted(ids),'mechanism':'Test also removes thin pull-up branch and fresh fills, so an accidental thin backup cannot pass the main-load test.'})
print(json.dumps(out,indent=2))
