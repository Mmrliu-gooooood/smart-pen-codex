from pathlib import Path
import sys,os,json
ROOT=Path('/workspace/scratch/fe148e758944')
ALLOWED=Path(os.environ['ELECTRICAL_RECONSTRUCTION']).resolve()
fd=os.open(os.environ['POSTR28_AUDIT_LOG'],os.O_CREAT|os.O_WRONLY|os.O_APPEND,0o600)
def audit(event,args):
 if event=='open' and args and isinstance(args[0],(str,bytes)):
  p=Path(os.fsdecode(args[0])).resolve()
  if p.is_relative_to(ROOT)and not p.is_relative_to(ALLOWED):
   os.write(fd,(json.dumps({'denied_original_workspace_python_open':str(p)})+'\n').encode());raise PermissionError('moving workspace reads forbidden')
 if event in ('open','subprocess.Popen','import'):os.write(fd,(json.dumps({'event':event,'args':repr(args)[:1200]})+'\n').encode())
sys.addaudithook(audit)
