"""Read-only exact-version checker. Never strip net prefixes to infer equivalence."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as E,sys
D=Path(__file__).resolve().parent;ROOT=D.parents[2]
class ContractError(ValueError):pass
def require(ok,msg):
 if not ok:raise ContractError(msg)
def pins(root,xml,ref):
 result={}
 for n in E.parse(root/xml).findall('./nets/net'):
  for x in n:
   if x.get('ref')!=ref:continue
   pin=x.get('pin');require(pin not in result,'duplicate native endpoint '+ref+'.'+str(pin));result[pin]=n.get('name')
 return result
def check_locks(root,version):
 for item in version['files']:
  path=root/item['path'];require(path.is_file(),'missing version file '+item['path']);require(hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256'],'version hash mismatch '+item['path'])
 actual=pins(root,version['xml'],version['reference']);require(actual==version['pins'],'native pin/net mismatch '+version['reference']);return actual
def validate(contract,root=ROOT,target=None):
 target=contract['target'] if target is None else target
 # A legacy four-pin target cannot be substituted even if somebody supplies its correct hashes.
 require(target==contract['target'],'target version mismatch: legacy 4-pin J5 is not this 3-pin NO CE interface')
 src=check_locks(root,contract['mainboard']);dst=check_locks(root,target)
 require(src=={'1':'USB_EN1','2':'USB_EN2','3':'GND'},'unexpected mainboard semantic interface')
 require(dst=={'1':'/core/USB_EN1','2':'/core/USB_EN2','3':'GND'},'unexpected integrated target interface / CE present')
 require(len(contract['wires'])==3,'wire count must be exactly three')
 seen_s=set();seen_d=set();semantic=[]
 for w in contract['wires']:
  s=w['source'];d=w['target'];require(s['ref']=='J107' and d['ref']=='J5','wrong connector refs')
  require(s['pin'] not in seen_s and d['pin'] not in seen_d,'duplicate wire endpoint');seen_s.add(s['pin']);seen_d.add(d['pin'])
  require(src.get(s['pin'])==s['net'] and dst.get(d['pin'])==d['net'],'exact native endpoint/net mismatch')
  expected={'USB_EN1':('1','USB_EN1','1','/core/USB_EN1'),'USB_EN2':('2','USB_EN2','2','/core/USB_EN2'),'GND':('3','GND','3','GND')}
  require(w['signal'] in expected and (s['pin'],s['net'],d['pin'],d['net'])==expected[w['signal']],'signal mapping mismatch')
  semantic.append(w['signal'])
 require(sorted(semantic)==['GND','USB_EN1','USB_EN2'],'missing or duplicate semantic signal')
 return {'logical_mapping':'PASS','physical_harness_released':False,'charge_permission_released':False,'target':'14x45 integrated J5, three-pin NO CE PORT'}
if __name__=='__main__':
 c=json.loads((D/'power_mode_mapping.json').read_text());print(json.dumps(validate(c),indent=2))
