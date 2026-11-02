"""Portable scoped replay: final1639→f763 only; no full historical replay claim."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile,xml.etree.ElementTree as ET
D=Path(__file__).resolve().parent;R=D.parents[1];N=R/'hardware/mainboard_wip19_20261102/candidate'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,why):
 if not ok:raise RuntimeError(why)
for row in json.loads((D/'PUBLICATION_SOURCES.json').read_text())['mapping']:require(sha(R/row['path'])==row['sha256'],'source hash '+row['path'])
require(sha(N/'mainboard_revD.kicad_pcb')=='f7632bf6296ba212ec59e54edb1dfdb91995f6f4f071a3d9505b6638f3fbf416','current native')
require(sha(D/'parent20.kicad_pcb')=='1639b8db38415f0466c13334add7cd4bfe6708b0caa232e8b1e79a7044fdf8e7','parent native')
with tempfile.TemporaryDirectory(prefix='pen19_replay_')as tmp:
 T=Path(tmp);shutil.copytree(D/'source',T,dirs_exist_ok=True);shutil.copytree(N,T/'candidate');shutil.copytree(N,T/'parent');shutil.copyfile(D/'parent20.kicad_pcb',T/'parent/mainboard_revD.kicad_pcb')
 env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',XDG_CONFIG_HOME=str(T/'config'),XDG_CACHE_HOME=str(T/'cache'),XDG_DATA_HOME=str(T/'data'))
 os.environ.update(env)
 def run(args):
  q=subprocess.run(args,cwd=T,env=env,text=True,capture_output=True)
  if q.returncode:raise RuntimeError(' '.join(args)+'\n'+q.stdout[-3000:]+'\n'+q.stderr[-3000:])
  return q
 for name in ['verify_candidate','references','ground_conductor']:
  run(['/usr/bin/python3',str(T/(name+'.py'))]);normal=json.loads((T/(name+'.json')).read_text());run(['/usr/bin/python3','-O',str(T/(name+'.py'))]);op=T/(name+'_O.json');optimized=json.loads((op if op.exists()else T/(name+'.json')).read_text());require(normal==optimized,name+' normal/-O mismatch')
 for name in ['rigid_transform','reconstruct','inverse','negative_checks']:run(['/usr/bin/python3',str(T/(name+'.py'))])
 require((T/'reconstructed_candidate/mainboard_revD.kicad_pcb').read_bytes()==(N/'mainboard_revD.kicad_pcb').read_bytes(),'reconstruction exact')
 require((T/'inverse_project/mainboard_revD.kicad_pcb').read_bytes()==(D/'parent20.kicad_pcb').read_bytes(),'inverse exact')
 run(['kicad-cli','pcb','drc','--format','json','--schematic-parity','-o',str(T/'native_drc.json'),str(T/'candidate/mainboard_revD.kicad_pcb')])
 for opt in [[],['-O']]:run(['/usr/bin/python3']+opt+[str(T/'strict_drc_gate.py')])
 run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(T/'top.xml'),str(T/'candidate/mainboard_revD.kicad_sch')]);x=ET.parse(T/'top.xml').getroot();require(len(x.findall('./components/comp'))==103,'top103');require(len(x.findall('./design/sheet'))==10,'top10')
 # Strong nonempty raw parsing applies independently to both actual inputs.
 sys.path.insert(0,str(T/'review_dependencies'));from native_blocks import blocks
 import re
 def fps(text):
  out=[v for _,_,v in blocks(text)if v.startswith('(footprint')];require(len(out)==103,'raw103');pairs=[(re.search(r'\(property "Reference" "([^"]+)"',v).group(1),v)for v in out];require(len(dict(pairs))==103,'unique103');return dict(pairs)
 a=fps((T/'parent/mainboard_revD.kicad_pcb').read_text());b=fps((T/'candidate/mainboard_revD.kicad_pcb').read_text())
 def check_pair(a,b):require(set(a)==set(b) and {k for k in a if a[k]!=b[k]}=={'R230','J107'},'exact raw change set')
 check_pair(a,b)
 negatives=0
 for txt in ['',(T/'candidate/mainboard_revD.kicad_pcb').read_text().replace(b['R224'],'',1)]:
  try:fps(txt)
  except RuntimeError:negatives+=1
  else:raise RuntimeError('raw negative accepted')
 altered=dict(b);altered['R224']+=' '
 try:check_pair(a,altered)
 except RuntimeError:negatives+=1
 else:raise RuntimeError('unauthorized raw mutation accepted')
 import pcbnew
 from finite_copper import build,components
 board=pcbnew.LoadBoard(str(T/'candidate/mainboard_revD.kicad_pcb'));nets={n:components(v)for n,v in build(board).items()};open_nets={n:v for n,v in nets.items()if n and len(v)>1};require(len(open_nets)==14 and sum(len(v)-1 for v in open_nets.values())==19,'current14/19 inventory');record=json.loads((D/'recorded/remaining19.json').read_text());require(open_nets=={r['net']:r['islands']for r in record['remaining']},'inventory terminal mismatch')
 print(json.dumps({'status':'PASS','native_sha256':sha(N/'mainboard_revD.kicad_pcb'),'drc':'0 errors /0 warnings /19 items /0 parity','top_components':103,'top_sheets':10,'raw_inputs_each':103,'raw_negative_cases':negatives,'incomplete_named_nets':14,'logical_links':19,'scope':'Final1639→f763 and current inventory only, not all617a→f763 history or full assembly/SI/PDN qualification'},indent=2))
