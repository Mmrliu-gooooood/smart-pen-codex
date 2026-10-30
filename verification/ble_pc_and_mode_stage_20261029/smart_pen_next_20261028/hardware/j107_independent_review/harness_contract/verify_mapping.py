"""Read-only exact-version checker. Never strip net prefixes to infer equivalence."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as E,sys,os
os.environ.setdefault("XDG_CONFIG_HOME","/tmp/rebuild-kicad/config")
os.environ.setdefault("XDG_CACHE_HOME","/tmp/rebuild-kicad/cache")
import pcbnew
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
 actual=pins(root,version['xml'],version['reference']);require(actual==version['pins'],'native pin/net mismatch '+version['reference'])
 boardfile=[x['path'] for x in version['files'] if x['path'].endswith('.kicad_pcb')]
 require(len(boardfile)==1,'exactly one native PCB required')
 board=pcbnew.LoadBoard(str(root/boardfile[0]));fps=[f for f in board.GetFootprints() if f.GetReference()==version['reference']]
 require(len(fps)==1,'native footprint missing/duplicate')
 copper={p.GetNumber():p.GetNetname() for p in fps[0].Pads()}
 require(copper==actual,'native PCB pad/net differs from source XML')
 return actual
def validate(contract,root=ROOT,target=None):
 target=contract['target'] if target is None else target
 # A legacy four-pin target cannot be substituted even if somebody supplies its correct hashes.
 require(target==contract['target'],'target version mismatch: exact Rev B PCB/source required, even when another board has identical pins')
 main_pcbs=[f['sha256'] for f in contract['mainboard']['files'] if f['path'].endswith('.kicad_pcb')]
 target_pcbs=[f['sha256'] for f in target['files'] if f['path'].endswith('.kicad_pcb')]
 require(main_pcbs==['8aa2581b4df112b979d83e67b9a6a2ddaa70a433c265cdc9849e41b60ff05ab5'],'current mainboard version required')
 require(target_pcbs==['94ced2bd4100ba6fd8d9a9af11f101cc091a4c112a1bb3c8bb5dec2b2dedcdbc'],'exact Rev B target identity required')
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
 return {'logical_mapping':'PASS','physical_harness_released':False,'charge_permission_released':False,'target':'power14_single_feed_revB J5, three-pin NO CE PORT'}
if __name__=='__main__':
 c=json.loads((D/'power_mode_mapping.json').read_text());print(json.dumps(validate(c),indent=2))
