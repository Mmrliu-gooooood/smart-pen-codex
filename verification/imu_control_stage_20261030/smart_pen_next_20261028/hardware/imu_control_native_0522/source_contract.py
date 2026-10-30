from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent;r=E.parse(D/'checks/candidate/netlist.xml');expect={'AON_I2C_SCL':{('U101','10'):'GPIO5',('U501','1'):'SCL',('R501','2'):'2'},'AON_I2C_SDA':{('U101','11'):'GPIO6',('U501','4'):'SDA',('R502','2'):'2'},'PICKUP_INT_N':{('U101','6'):'GPIO1',('U501','12'):'INT1'}};rows={}
for net,want in expect.items():
 n=next(n for n in r.findall('.//nets/net')if n.get('name')==net);actual={(n.get('ref'),n.get('pin')):n.get('pinfunction')for n in n.findall('node')}
 if actual!=want:raise RuntimeError('source '+net)
 rows[net]=[n.attrib for n in n.findall('node')]
parts={c.get('ref'):c.findtext('value')for c in r.findall('.//components/comp')}
for ref in['R501','R502']:
 if parts[ref]!='10k 1%':raise RuntimeError('actual pullup value')
print(json.dumps({'status':'ACTUAL_NATIVE_MATCHED_EXPORTED_SOURCE_CONTRACT','nets':rows,'pullups':{ref:parts[ref]for ref in['R501','R502']},'source_netlist_sha256':hashlib.sha256((D/'checks/candidate/netlist.xml').read_bytes()).hexdigest(),'limits':['GPIO routing is not firmware implementation','IRQ effective polarity/latching is not inferred from net spelling; no firmware commands executed']},indent=2))
