from pathlib import Path
import json,hashlib,shutil,uuid,os
D=Path(__file__).resolve().parent; BASE=D.parent/'mcu_supply_access_candidate_0300/native'; N=Path(os.environ.get('PRESSURE_NATIVE_OUTPUT',str(D/'native')))
MPN='RC0603FR-0747KL'
def req(x,m):
 if not x: raise RuntimeError(m)
def children(s):
 depth=0;start=None;quote=False;escape=False
 for i,c in enumerate(s):
  if quote:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quote=False
   continue
  if c=='"':quote=True;continue
  if c=='(':
   depth+=1
   if depth==2:start=i
  elif c==')':
   if depth==2:yield start,i+1,s[start:i+1]
   depth-=1
 req(depth==0 and not quote,'balanced sexpr')
def replace_r503(s,pcb):
 found=[]
 for a,b,block in children(s):
  kind='(footprint ' if pcb else '(symbol '
  if block.startswith(kind) and '(property "Reference" "R503"' in block:
   found.append((a,b,block))
 req(len(found)==1,'exactly one R503 instance');a,b,old=found[0]
 req(old.count('(property "Value" "100k 1%"')==1,'R503 original value');req('(property "MPN"'not in old,'original MPN absent')
 new=old.replace('(property "Value" "100k 1%"','(property "Value" "47k 1%"')
 if pcb:
  prop='\n\t\t(property "MPN" "'+MPN+'" (at 0 0 180) (layer "B.Fab") (hide yes) (uuid "'+str(uuid.uuid5(uuid.NAMESPACE_URL,'smart-pen/pressure-r503-47k-mpn'))+'") (effects (font (size 1.27 1.27) (thickness 0.15)) (justify mirror)))\n'
 else:prop=' (property "MPN" "'+MPN+'" (at 64.77 124.46000000000001 0) (effects (font (size 1.27 1.27)) (hide yes))) '
 new=new[:-1]+prop+')'
 return s[:a]+new+s[b:],dict(reference='R503',old_value='100k 1%',new_value='47k 1%',old_mpn=None,new_mpn=MPN,old_block_sha=hashlib.sha256(old.encode()).hexdigest(),new_block_sha=hashlib.sha256(new.encode()).hexdigest())
if __name__=='__main__':
 req(hashlib.sha256((BASE/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest()=='8fe809b685633dd86dddc36ec33961d61ef7fad9fca52286bc47bd72a4f614e5','base board hash')
 shutil.copytree(BASE,N,dirs_exist_ok=True)
 changes=[]
 for rel,pcb in [('mainboard_revD.kicad_pcb',True),('schematic/pickup_on_main.kicad_sch',False)]:
  p=N/rel;s=p.read_text();v,e=replace_r503(s,pcb);p.write_text(v);e['path']=rel;changes.append(e)
 (N.parent/'source_delta.json').write_text(json.dumps(dict(allowed_changes=changes,status='NOFAB_NOPOWER_CONDITIONAL_PRESSURE_LOAD_FIX_ONLY',geometry_net_and_wiring_changes=[]),indent=2)+'\n')
 print(json.dumps(changes,indent=2))
