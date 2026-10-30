from pathlib import Path
import re,json,hashlib
D=Path(__file__).resolve().parent;A=D.parent/'ground_local_native_0920/native';B=D/'native';m=json.loads((D/'materialization.json').read_text())
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
a,b=get(A/'mainboard_revD.kicad_pcb'),get(B/'mainboard_revD.kicad_pcb');changed=[u for u in a if b.get(u)!=a[u]];fp=[u for u in changed if a[u].startswith('(footprint')]
if len(fp)!=1 or '(property "Reference" "J202"'not in a[fp[0]]:raise RuntimeError('only J202 footprint')
if a[fp[0]]!=b[fp[0]].replace('(at 7 88.8 180)','(at 7 90.5 180)',1):raise RuntimeError('only J202 rigid position raw')
if set(changed)!=set(m['changed']+m['edge_changed']+fp):raise RuntimeError('exact raw change set')
for u in m['edge_changed']:
 if a[u]!=b[u].replace('93.3','95'):raise RuntimeError('outline only tail')
added=sorted(set(b)-set(a))
if added!=m['added']:raise RuntimeError('new raw blocks')
def inv(d):return{str(f.relative_to(d)):hashlib.sha256(f.read_bytes()).hexdigest()for f in d.rglob('*')if f.is_file()}
x,y=inv(A),inv(B);diff=[n for n in sorted(set(x)|set(y))if x.get(n)!=y.get(n)]
if diff!=['mainboard_revD.kicad_pcb']:raise RuntimeError('source native changed')
provider=D.parents[2]/'smart_pen_app_pipeline_20261028/firmware/application_idf/main/board_provider_absent.c'
if 'return 0;'not in provider.read_text():raise RuntimeError('provider NULL')
print(json.dumps({'changed_raw_copper_count':len(m['changed']),'added_raw_copper_count':len(added),'only_J202_rigid_translation_raw':True,'only_three_tail_outline_segments':m['edge_changed'],'all_other_raw_copper_footprints_outline_unchanged':True,'only_native_changed':diff,'native_files':len(y),'provider_sha256':hashlib.sha256(provider.read_bytes()).hexdigest(),'provider_returns_NULL':True},indent=2))
