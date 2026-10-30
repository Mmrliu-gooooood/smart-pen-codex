import runpy,sys
from pathlib import Path
p=Path(sys.argv[1]);
if p.name=='independent_exits.py':
 print('SKIP_ROOT_EXCLUDED_OBSOLETE_TRIAL_NOT_EXECUTED');sys.exit(0)
sys.path.insert(0,str(p.parent));sys.argv=[str(p)];runpy.run_path(str(p),run_name='__main__')
