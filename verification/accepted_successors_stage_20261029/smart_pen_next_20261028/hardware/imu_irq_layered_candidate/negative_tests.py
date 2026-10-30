from pathlib import Path
import tempfile,subprocess,re,json,hashlib,os
D=Path(__file__).resolve().parent;raw=(D/'native/mainboard_revD.kicad_pcb').read_text();delta=json.loads((D/'routing_delta.json').read_text());irq=next(u for u,r in delta['added'].items()if r[0]=='PCB_TRACK'and r[1]=='PICKUP_INT_N');names={n:v for n,v in re.findall(r'\(net (\d+) "([^"\n]+)"\)',raw)};codes={v:n for n,v in names.items()};oldraw=(D.parent/'j107_mode_port_closure/native/mainboard_revD.kicad_pcb').read_text();aon=next(re.search(r'\(uuid "([^"\n]+)"\)',q)[1]for q in re.findall(r'\n\t\(segment\n.*?\n\t\)',oldraw,re.S)if '(net '+codes['3V3_AON']+')'in q)
def modify(text,kind,uid,fn):
 found=[]
 def go(m):
  if uid in m[0]:found.append(1);return fn(m[0])
  return m[0]
 out=re.sub(r'\n\t\('+kind+r'\n.*?\n\t\)',go,text,flags=re.S)
 if len(found)!=1:raise RuntimeError('Mutation target not unique '+uid)
 return out
cases={
 'wrong_existing_AON_identity':(modify(raw,'segment',aon,lambda q:re.sub(r'\(net \d+\)','(net '+codes['AON_I2C_SCL']+')',q)),'SERIALIZED_NET_CHANGED'),
 'wrong_IRQ_identity':(modify(raw,'segment',irq,lambda q:re.sub(r'\(net \d+\)','(net '+codes['BOOT_N']+')',q)),'SERIALIZED_NEW_NET_CHANGED'),
 'thin_IRQ_trace':(modify(raw,'segment',irq,lambda q:q.replace('(width 0.15)','(width 0.127)')),'DECLARED_NEW_GEOMETRY_CHANGED'),
 'BOOT_wrong_drill':(modify(raw,'via','57b8c53a-6394-4dd8-9f05-1b30c6aa5006',lambda q:q.replace('(drill 0.2)','(drill 0.3)')),'BOOT_VIA_OVERRIDE'),
 'weaken_MEMS_via_rule':(modify(raw,'zone','2a715b0e-d7bf-49ab-b132-f7f180326c33',lambda q:q.replace('(vias not_allowed)','(vias allowed)')),'MEMS_LAYER_OR_FLAGS')}
results=[]
with tempfile.TemporaryDirectory(prefix='irq-negative-')as td:
 for name,(text,expected)in cases.items():
  if text==raw:raise RuntimeError('Mutation ineffective '+name)
  f=Path(td)/(name+'.kicad_pcb');f.write_text(text)
  for optimized in[False,True]:
   cmd=['/usr/bin/python3']+(['-O']if optimized else[])+[str(D/'verify.py'),str(f)];r=subprocess.run(cmd,capture_output=True,text=True);reason=next((v.removeprefix('RuntimeError: ')for v in reversed(r.stderr.splitlines())if v.startswith('RuntimeError: ')),None)
   if r.returncode==0 or reason is None or not reason.startswith(expected):raise RuntimeError('Wrong failure class '+name+' '+str(reason)+' '+r.stderr[-1000:])
   results.append({'case':name,'optimized':optimized,'exit_code':r.returncode,'expected_reason_prefix':expected,'actual_reason':reason,'mutant_sha256':hashlib.sha256(text.encode()).hexdigest()});print(results[-1],flush=True)
(D/'negative_results.json').write_text(json.dumps(results,indent=2))
