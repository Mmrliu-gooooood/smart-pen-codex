"""Run a frozen mechanical check from an isolated copy, relocating only CAD paths.
Usage: /usr/bin/python3 [-O] run_isolated_mechanics.py ISOLATED_ROOT SCRIPT_RELATIVE
This does NOT copy source inputs. Caller must reconstruct exact listed files first.
"""
from pathlib import Path
import sys,os,json,hashlib,runpy
HERE=Path(__file__).resolve().parent
REPORT=json.loads((HERE/'MECHANICAL_INPUTS.json').read_text())
ROOT=Path(sys.argv[1]).resolve();REL=sys.argv[2];SCRIPT=(ROOT/REL).resolve()
ORIGINAL=Path('/workspace/scratch/fe148e758944').resolve()
def require(ok,msg):
 if not ok: raise RuntimeError(msg)
require(ROOT!=ORIGINAL and SCRIPT.is_relative_to(ROOT),'isolated root/script required')
require(ROOT.is_dir() and SCRIPT.is_file(),'reconstruction missing')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
entry=next(x for x in REPORT['scripts']if x['path']==REL)
require(sha(SCRIPT)==entry['sha256'],'frozen script changed')
for row in REPORT['inputs']:
 q=(ROOT/row['path']).resolve();require(q.is_relative_to(ROOT),'root escape')
 require(q.is_file() and q.stat().st_size==row['bytes'] and sha(q)==row['sha256'],'input mismatch '+row['path'])
MAP={r['original_absolute']:str((ROOT/r['path']).resolve())for r in REPORT['inputs']if 'original_absolute'in r}
old_load=json.load
# Frozen source inventory remains byte-exact; only loaded context path values change.
def relocated_load(fp,*args,**kwargs):
 value=old_load(fp,*args,**kwargs)
 name=Path(getattr(fp,'name','')).resolve()
 if name==ROOT/'assembly_context_audit_0818_20261030/inventory.json':
  require(len(value['contexts'])==4,'four contexts')
  for c in value['contexts']:
   original=c['path'];require(original in MAP,'unexpected context source')
   c['path']=MAP[original]
 return value
json.load=relocated_load
os.environ['QT_QPA_PLATFORM']='offscreen'
# No Python imports or data may fall back to the live moving workspace.
sys.path=[str(SCRIPT.parent)]+[p for p in sys.path if p and not Path(p).resolve().is_relative_to(ORIGINAL)]
def audit(event,args):
 if event=='open' and args and isinstance(args[0],(str,bytes,os.PathLike)):
  p=Path(os.fsdecode(args[0])).resolve()
  if p.is_relative_to(ORIGINAL) and not p.is_relative_to(ROOT):raise RuntimeError('original workspace access forbidden: '+str(p))
sys.addaudithook(audit)
sys.argv=[str(SCRIPT)]
runpy.run_path(str(SCRIPT),run_name='__main__')
