from pathlib import Path
import re,json,hashlib
D=Path(__file__).resolve().parent;A=D.parent/'ground_pair_native_1007/native';B=D/'native'
def blocks(s):
 depth=0;quote=False;esc=False;start=0
 for i,c in enumerate(s):
  if quote:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':quote=False
  elif c=='"':quote=True
  elif c=='(':
   depth+=1
   if depth==2:start=i
  elif c==')':
   if depth==2:yield s[start:i+1]
   depth-=1
get=lambda f:{re.search(r'\(uuid "([^"]+)"\)',b).group(1):b for b in blocks(f.read_text())if b.startswith(('(segment','(via','(footprint','(gr_line'))}
a,b=get(A/'mainboard_revD.kicad_pcb'),get(B/'mainboard_revD.kicad_pcb');changed=[u for u in a if b.get(u)!=a[u]];added=sorted(set(b)-set(a));m=json.loads((D/'materialization.json').read_text())
if changed or added!=m['added']:raise RuntimeError([changed,added])
def inv(d):return{str(f.relative_to(d)):hashlib.sha256(f.read_bytes()).hexdigest()for f in d.rglob('*')if f.is_file()}
x,y=inv(A),inv(B);diff=[n for n in sorted(set(x)|set(y))if x.get(n)!=y.get(n)]
if diff!=['mainboard_revD.kicad_pcb']:raise RuntimeError(diff)
provider=D.parents[2]/'smart_pen_app_pipeline_20261028/firmware/application_idf/main/board_provider_absent.c'
if 'return 0;'not in provider.read_text():raise RuntimeError('provider NULL')
print(json.dumps({'old_raw_copper_footprints_and_drawings_changed':changed,'added_raw_blocks':added,'only_native_changed':diff,'native_files':len(y),'provider_sha256':hashlib.sha256(provider.read_bytes()).hexdigest(),'provider_returns_NULL':True},indent=2))
