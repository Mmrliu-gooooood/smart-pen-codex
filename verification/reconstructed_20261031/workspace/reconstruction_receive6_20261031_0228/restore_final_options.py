from pathlib import Path
import re,json,shutil
D=Path(__file__).resolve().parent
# Read complete top-level native expressions, respecting escaped quoted strings.
def blocks(s):
 depth=0;quoted=False;escape=False;start=None;out=[]
 for i,c in enumerate(s):
  if quoted:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quoted=False
   continue
  if c=='"':quoted=True;continue
  if c=='(':
   depth+=1
   if depth==2:start=i
  elif c==')':
   if depth==2:out.append((start,i+1,s[start:i+1]))
   depth-=1
 return out
src=(D/'native/mainboard_revD.kicad_pcb').read_text();base=(D/'final_candidate/mainboard_revD.kicad_pcb').read_text();sb=blocks(src);bb=blocks(base)
u=lambda s:re.search(r'\(uuid "([^"]+)"\)',s).group(1)if re.search(r'\(uuid "([^"]+)"\)',s)else None
olds={u(t):t for a,z,t in sb if t.startswith(('(segment','(via'))};newgnd=[t for a,z,t in bb if t.startswith(('(segment','(via'))and u(t)not in olds and '(net 1)'in t] # use exact known UUIDs from author specs below, not net number heuristic
spec=json.load(open(D/'joint_prefilter.json'))['new'];cnew={q['uuid']for q in spec if q['net']=='GND'and((q.get('xy',[0,100])[1]<20)or(q.get('a',[0,100])[1]<20))};rnew={q['uuid']for q in spec if q['net']=='GND'and q.get('layer')=='B.Cu'}
for mode in ['R219','C104']:
 remove=set();restore=[]
 if mode in ['R219','both']:remove|=rnew;restore+=['d52a9418-6d55-5883-abac-3d51ba89aa70','357b6b72-697e-5d26-a707-10cad6f88c47']
 if mode in ['C104','both']:remove|=cnew;restore+=['39c7d991-8635-4232-90dd-155b6366eb15','47b32f57-9185-4b15-9749-eae864f977ff']
 edits=[]
 for a,z,t in bb:
  if u(t)in remove:edits.append((a,z,''))
  elif t.startswith('(footprint')and '(property "Reference" "R219"'in t and mode in ['R219','both']:
   old=next(t for a,z,t in sb if t.startswith('(footprint')and '(property "Reference" "R219"'in t);edits.append((a,z,old))
  elif u(t)=='7dbfff33-878e-48e0-a92a-86ebb50aec88':edits.append((a,z,t.replace('(end 2.8 41.5)','(end 3.1 41.5)')))
 s=base
 for a,z,t in reversed(edits):s=s[:a]+t+s[z:]
 pos=s.rfind(')');s=s[:pos]+'\n'+''.join(olds[u]+'\n'for u in restore)+s[pos:]
 out=D/('final_restore_'+mode+'_DIAGNOSTIC');shutil.copytree(D/'native',out);(out/'mainboard_revD.kicad_pcb').write_text(s)
print({'C104_new_removed':sorted(cnew),'R219_new_removed':sorted(rnew),'variants':['R219','C104'],'new_PCLK_dead_end_trim_mm':.3})
