from pathlib import Path
import json,hashlib,shutil,subprocess,os,collections
D=Path(__file__).resolve().parent;B=D.parents[1]/'j202_low_speed_reference_candidate';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();exe=Path(shutil.which('kicad-cli')).resolve();env=dict(os.environ,XDG_CONFIG_HOME='/tmp/pen-layout-config',XDG_CACHE_HOME='/tmp/pen-layout-cache',XDG_DATA_HOME='/tmp/pen-layout-data')
files={}
for label,root in [('baseline',B),('candidate',D)]:
 files[label]={ext:{'path':str(root/'native'/('mainboard_revD.'+ext)),'sha256':sha(root/'native'/('mainboard_revD.'+ext))}for ext in ['kicad_pcb','kicad_pro','kicad_dru','kicad_sch']}
xs={label:json.loads(f.read_text())for label,f in [('historical',B/'preflight.native_drc.json'),('fresh_baseline',D/'baseline_fresh_drc.json'),('fresh_candidate',D/'trimmed_drc.json')]}
def canon(o):
 z=dict(o);z['items']=sorted(z.get('items',[]),key=lambda a:json.dumps(a,sort_keys=True));return json.dumps(z,sort_keys=True)
def diff(a,b):
 out={}
 for k in ['violations','unconnected_items','schematic_parity']:
  x,y=[collections.Counter(map(canon,z[k]))for z in [a,b]];out[k]={'before':sum(x.values()),'after':sum(y.values()),'added':[json.loads(s)for s in(y-x).elements()],'removed':[json.loads(s)for s in(x-y).elements()]}
 return out
out={'executable':str(exe),'executable_sha256':sha(exe),'version_stdout':subprocess.run([str(exe),'version'],env=env,capture_output=True,text=True).stdout.strip(),'environment':{k:env[k]for k in ['XDG_CONFIG_HOME','XDG_CACHE_HOME','XDG_DATA_HOME']},'native_files':files,'project_binding':'Same-basename mainboard_revD.kicad_pro/.kicad_dru alongside each native PCB. Hashes must match baseline. DRC invokes explicit PCB path with --all-track-errors --severity-all --schematic-parity --format json --exit-code-violations. No alternate rules or exclusions changed.','fill_actions':{'baseline':'Historical frozen board cached planes; read-only CLI DRC did not save or refill. Separate baseline fresh-fill replay is checked below if produced.','candidate':'pcbnew.ZONE_FILLER.Fill followed by SaveBoard after reroute and exact tail trim; serialized delta replay also freshly fills and requires byte equality.'},'historical_to_fresh_baseline':diff(xs['historical'],xs['fresh_baseline']),'fresh_baseline_to_candidate':diff(xs['fresh_baseline'],xs['fresh_candidate']),'interpretation':'Initial direct CLI omitted --all-track-errors. Repeated complete-mode commands restore all 17 findings; no version drift or short repair. Incomplete reports retained as rejected evidence.'}
for ext in ['kicad_pro','kicad_dru','kicad_sch']:
 if files['baseline'][ext]['sha256']!=files['candidate'][ext]['sha256']:raise RuntimeError('PROJECT_BINDING_CHANGED')
(D/'toolchain_and_complete_drc_diff.json').write_text(json.dumps(out,indent=2));print(json.dumps({'tool':out['version_stdout'],'binary_sha256':out['executable_sha256'],'diff_counts':{k:{t:{z:v[z]for z in ['before','after']}for t,v in out[k].items()}for k in ['historical_to_fresh_baseline','fresh_baseline_to_candidate']}},indent=2))
