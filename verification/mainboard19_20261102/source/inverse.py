import os,sys,json,shutil,re,hashlib
from pathlib import Path
os.environ.update(XDG_CONFIG_HOME='/tmp/pcb_interface_clean_617a/config',XDG_CACHE_HOME='/tmp/pcb_interface_clean_617a/cache',XDG_DATA_HOME='/tmp/pcb_interface_clean_617a/data')
import pcbnew as p
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D/'review_dependencies'));from native_blocks import blocks
c=json.loads((D/'native_contract.json').read_text());A=D/'parent/mainboard_revD.kicad_pcb';C=D/'candidate';I=D/'inverse_project'
if I.exists():raise RuntimeError('inverse no overwrite')
shutil.copytree(C,I);Q=I/A.name;old=A.read_text();raw=Q.read_text();added={x['uuid']for x in c['objects']};removed=set(c['removed']);restore=[]
for _,_,v in blocks(old):
 if v.startswith(('(segment','(via')) and re.search(r'\(uuid "([^"]+)"\)',v).group(1)in removed:restore.append(v)
found=set()
for a,z,v in reversed(blocks(raw)):
 if v.startswith(('(segment','(via')):
  u=re.search(r'\(uuid "([^"]+)"\)',v).group(1)
  if u in added:found.add(u);raw=raw[:a]+raw[z:]
if found!=added or len(restore)!=len(removed):raise RuntimeError('inverse delta')
oldfp=next(v for _,_,v in blocks(old)if v.startswith('(footprint')and '(property \"Reference\" \"R230\"'in v)
newfp=next(v for _,_,v in blocks(raw)if v.startswith('(footprint')and '(property \"Reference\" \"R230\"'in v)
raw=raw.replace(newfp,oldfp,1)
oldlabel=next(v for _,_,v in blocks(old)if v.startswith('(footprint')and '(property "Reference" "J107"'in v)
newlabel=next(v for _,_,v in blocks(raw)if v.startswith('(footprint')and '(property "Reference" "J107"'in v)
raw=raw.replace(newlabel,oldlabel,1)
pos=raw.rfind(')');raw=raw[:pos]+'\n'+'\n'.join(restore)+'\n'+raw[pos:];Q.write_text(raw);b=p.LoadBoard(str(Q));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(Q),b)
res={'parent_sha256':hashlib.sha256(A.read_bytes()).hexdigest(),'inverse_sha256':hashlib.sha256(Q.read_bytes()).hexdigest(),'native_exact':Q.read_bytes()==A.read_bytes(),'all_nonpcb_files_exact':all((I/f.relative_to(A.parent)).read_bytes()==f.read_bytes()for f in A.parent.rglob('*')if f.is_file()and f.suffix not in['.kicad_pcb','.kicad_prl'])};(D/'inverse_result.json').write_text(json.dumps(res,indent=2));print(res)
if not res['native_exact']or not res['all_nonpcb_files_exact']:raise RuntimeError('inverse')
