import re,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent;S=Path('/workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/gate_input_local_routing/mainboard_revD.kicad_pcb');F=R/'fresh_fill_equal_project_audit/mainboard_revD.kicad_pcb'
def blocks(text,token):
 out=[];start=0
 while True:
  p=text.find('('+token+'\n',start)
  if p<0:break
  level=0;quote=False;escaped=False
  for i in range(p,len(text)):
   c=text[i]
   if quote:
    if escaped:escaped=False
    elif c=='\\':escaped=True
    elif c=='"':quote=False
   elif c=='"':quote=True
   elif c=='(':level+=1
   elif c==')':
    level-=1
    if level==0:break
  out.append(re.sub(r'\s+',' ',text[p:i+1]).strip());start=i+1
 return sorted(out)
a=S.read_text();b=F.read_text();out={}
for kind in ['segment','via','arc','zone','filled_polygon']:
 x=blocks(a,kind);y=blocks(b,kind);out[kind]=dict(original_count=len(x),fresh_count=len(y),exact_normalized_geometry_and_net_tokens_equal=x==y)
net=lambda s:sorted(set(re.findall(r'\(net\s+(\d+)\s+"([^"\n]+)"\)',s)))
out['netnumber_to_name_equal']=net(a)==net(b)
if not all(x['exact_normalized_geometry_and_net_tokens_equal']for k,x in out.items()if isinstance(x,dict))or not out['netnumber_to_name_equal']:raise ValueError('primitive drift')
(R/'fill_primitive_equivalence.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
