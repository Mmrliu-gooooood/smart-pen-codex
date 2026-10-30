import json,sys,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'width14_qualified_resistor_screen'))
from screen import evaluate,optimum
D=json.loads((R/'input.json').read_text());C=json.loads((R.parent/'width14_qualified_resistor_screen/contract_snapshot.json').read_text())
def req(x,m):
 if not x:raise RuntimeError(m)
req(hashlib.sha256(Path(D['source']).read_bytes()).hexdigest()==D['sha256'],'Native hash')
contracts={c['ref']:c for c in C['resistors']};parts=[]
for old in D['parts']:
 p=dict(old);p['bounds']=old['bounds'].copy()
 if p['ref'] in contracts:
  c=contracts[p['ref']]
  req(p['value']==c['source_value'],'Value mismatch '+p['ref'])
  req(p['nets']==c['source_net_by_pin'],'Net mismatch '+p['ref'])
  req('R_0603' in p['footprint'],'Package mismatch')
  p['height_total']=.7
 if p['ref']=='J109':
  req(p['bounds']==[11.3,18.3,12.7,24.9],'Unexpected port location')
  p['bounds']=[11.1,18.1,12.9,25.1]
 parts.append(p)
dictout=dict(status='NOFAB conditional native prelayout check',native_sha256=D['sha256'],source_contract_sha256=hashlib.sha256((R.parent/'width14_qualified_resistor_screen/contract_snapshot.json').read_bytes()).hexdigest(),changed_height_refs=sorted(contracts),best=optimum(parts),fixed_B2p288511=evaluate(2.288511,parts),applied_parts=parts)
print(json.dumps(dictout,indent=2))
