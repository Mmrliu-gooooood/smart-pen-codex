from pathlib import Path
import json,re,tempfile,subprocess,os
D=Path(__file__).resolve().parent;base=(D/'native/mainboard_revD.kicad_pcb').read_text();delta=json.loads((D/'serialized_delta.json').read_text());names={v:int(n)for n,v in re.findall(r'\(net (\d+) "([^"\n]+)"\)',base)}
blocks={re.search(r'\(uuid "([^"\n]+)"\)',q)[1]:q for q in re.findall(r'\n\t\((?:segment|via)\n.*?\n\t\)',base,re.S)}
new=sorted(delta['added']);old=next(u for u in sorted(blocks)if u not in new and re.search(r'\(net '+str(names['3V3_AON'])+r'\)',blocks[u]));bus=next(u for u in new if re.search(r'\(net '+str(names['GND'])+r'\)',blocks[u]));track=next(u for u in new if blocks[u].startswith('\n\t(segment')and'(width 0.25)'in blocks[u]);via=next(u for u in new if blocks[u].startswith('\n\t(via'))
def changed(u,q):return base.replace(blocks[u],q,1)
cases=[('wrong_old_AON',changed(old,re.sub(r'\(net \d+\)','(net '+str(names['AON_I2C_SCL'])+')',blocks[old])),'SERIALIZED_NET_CHANGED'),('wrong_new_bus',changed(bus,re.sub(r'\(net \d+\)','(net '+str(names['AON_I2C_SDA'])+')',blocks[bus])),'SERIALIZED_NEW_NET_CHANGED'),('thin_new_trace',changed(track,blocks[track].replace('(width 0.25)','(width 0.15)')),'DECLARED_NEW_GEOMETRY_CHANGED'),('wrong_new_drill',changed(via,blocks[via].replace('(drill 0.3)','(drill 0.2)')),'DECLARED_NEW_GEOMETRY_CHANGED')]
cases.append(('missing_explicit_tenting',changed(via,blocks[via].replace('\n\t\t(tenting front back)','')),'NEW_GND_VIA_TENTING_REQUIRED'))
for q in re.findall(r'\n\t\(footprint[^\n]*\n.*?\n\t\)',base,re.S):
 if '(property "Reference" "J202"'in q:
  bad=q.replace('5034802400_NEW_24PIN_SENSOR_HANDOFF','UNKNOWN_30PIN_MODULE',1)
  if bad==q:raise RuntimeError('J202_VALUE_NOT_FOUND')
  cases.append(('wrong_J202_physical_version',base.replace(q,bad,1),'COMPLETE_NATIVE_FOOTPRINT_BLOCK_CHANGED'));break
results=[]
with tempfile.TemporaryDirectory(prefix='i2c-negative-')as tmp:
 for name,raw,reason in cases:
  f=Path(tmp)/(name+'.kicad_pcb');f.write_text(raw);diags=[]
  for flag in [[],['-O']]:
   r=subprocess.run(['/usr/bin/python3']+flag+[str(D/'verify.py'),str(f)],capture_output=True,text=True);last=next((x.split('RuntimeError: ',1)[1]for x in r.stderr.splitlines()if x.startswith('RuntimeError: ')),None)
   if r.returncode==0 or last is None or not last.startswith(reason):raise RuntimeError('NEGATIVE_REASON_MISMATCH '+name+' '+repr(last))
   diags.append(last);results.append({'case':name,'optimized':bool(flag),'exit':r.returncode,'diagnostic':last})
  if diags[0]!=diags[1]:raise RuntimeError('NONDETERMINISTIC_DIAGNOSTIC '+name)
(D/'negative_results.json').write_text(json.dumps({'cases':len(cases),'runs':results,'status':'EXACT_REASON_NORMAL_OPTIMIZED_REJECTIONS'},indent=2));print(len(cases),len(results))
