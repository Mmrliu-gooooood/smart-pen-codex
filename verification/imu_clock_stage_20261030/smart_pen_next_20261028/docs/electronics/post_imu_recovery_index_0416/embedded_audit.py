from pathlib import Path
import re,json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2];N=R/'hardware/imu_j107_clock_native_0405/native';idx=json.loads((D/'index.json').read_text())
def parse(s):
 ts=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s);stack=[];root=None
 for t in ts:
  if t=='(':
   v=[]
   if stack:stack[-1].append(v)
   else:root=v
   stack.append(v)
  elif t==')':stack.pop()
  else:stack[-1].append(json.loads(t)if t.startswith('"')else t)
 if stack:raise RuntimeError('unbalanced')
 return root
def children(a,key):return[x for x in a if isinstance(x,list)and x and x[0]==key]
def first(a,key):return children(a,key)[0]
def pins(a):
 for x in a:
  if isinstance(x,list):
   if x and x[0]=='pin'and any(isinstance(y,list)and y[0]=='number'for y in x):yield x
   else:yield from pins(x)
lookup={};files={}
for f in N.rglob('*.kicad_sch'):
 root=parse(f.read_text());lib=children(root,'lib_symbols')
 if not lib:continue
 defs={x[1]:x for x in children(lib[0],'symbol')};files[str(f.relative_to(N))]=hashlib.sha256(f.read_bytes()).hexdigest()
 for sym in children(root,'symbol'):
  refs=[x[2]for x in children(sym,'property')if x[1]=='Reference']
  if not refs:continue
  ref=refs[0];libid=first(sym,'lib_id')[1];definition=defs[libid]
  for pin in pins(definition):lookup[(ref,first(pin,'number')[1])]={'function':first(pin,'name')[1],'type':pin[1],'source_file':str(f.relative_to(N)),'embedded_lib_id':libid,'instance_uuid':first(sym,'uuid')[1]}
rows=[];mechanical=[]
for name,p in idx['all_physical_pads'].items():
 if p['pin']=='':mechanical.append(name);continue
 a=lookup[(p['ref'],p['pin'])]
 if a['function']!=(p['source_pinfunction']if p['source_pinfunction']is not None else '~')or a['type']not in p['source_pintype'].split('+'):raise RuntimeError('embedded mismatch '+name+' '+str(a)+' '+str(p['source_pinfunction']))
 rows.append({'physical_pad':name,**a})
print(json.dumps({'status':'DIRECT_EMBEDDED_LIB_SYMBOL_PIN_AUDIT','matched_physical_electrical_pads':len(rows),'mechanical_unnumbered_not_symbol_pins':mechanical,'source_files':files,'rows':rows},indent=2))
