from pathlib import Path
import os,sys,json
ORIG=Path('/workspace/scratch/fe148e758944');ROOT=Path(os.environ['MECH_ROOT']);FROZEN=Path(os.environ['MECH_FROZEN']);HELP=Path(__file__).resolve().parent
old=json.load
def load(fp,*a,**kw):
 v=old(fp,*a,**kw)
 if Path(getattr(fp,'name','')).name=='inventory.json' and isinstance(v,dict)and 'contexts'in v:
  for c in v['contexts']:
   p=Path(c['path']);c['path']=str(ROOT/p.relative_to(ORIG))
 return v
json.load=load
def audit(event,args):
 if event=='open'and args and isinstance(args[0],(str,bytes,os.PathLike)):
  p=Path(os.fsdecode(args[0])).resolve();mode=args[1];flags=args[2]if len(args)>2 else 0
  if p.is_relative_to(ORIG) or (os.environ.get('MECH_SOURCE') and p.is_relative_to(Path(os.environ['MECH_SOURCE']))):
   allowed=p.is_relative_to(ROOT)or p.is_relative_to(FROZEN)or p in [HELP/'sitecustomize.py',HELP/'launcher.py']
   if not allowed:raise RuntimeError('movingworkspace read denied: '+str(p))
   write=(isinstance(mode,str)and any(c in mode for c in 'wax+'))or(isinstance(flags,int)and bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC)))
   if write and not p.is_relative_to(ROOT):raise RuntimeError('frozen write denied: '+str(p))
sys.addaudithook(audit)
with open(ROOT/'.audit_processes.jsonl','a') as f:
 f.write(json.dumps({'pid':os.getpid(),'argv':sys.argv,'inventory_relocation':'memory_only','guard':'deny_live_workspace_and_frozen_writes'})+'\n')
