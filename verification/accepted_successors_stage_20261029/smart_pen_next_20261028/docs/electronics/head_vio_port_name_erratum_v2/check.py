from pathlib import Path
import xml.etree.ElementTree as E
import hashlib,json
root=Path(__file__).resolve().parents[3]; d=root/'hardware/j202_low_speed_reference_candidate';m=json.loads((d/'manifest.json').read_text()); entry=m['files']['fresh.xml']; expected=entry if isinstance(entry,str) else entry['sha256'];p=d/'fresh.xml'
if hashlib.sha256(p.read_bytes()).hexdigest()!=expected:raise RuntimeError('source binding')
contract=d/'interface_reference_contract.json'
contract_sha='65eca5fea27c4aca954e7a3438e52ac3cc6300b87fd4d6b5686e3f5071c58e23'
if hashlib.sha256(contract.read_bytes()).hexdigest()!=contract_sha:raise RuntimeError('contract identity')
r=E.parse(p).getroot(); comps={c.attrib['ref']:(c.find('libsource').attrib['lib'],c.find('libsource').attrib['part']) for c in r.findall('./components/comp')};libs={(x.attrib['lib'],x.attrib['part']):{p.attrib['num']:p.attrib['name'] for p in x.findall('./pins/pin')} for x in r.findall('./libparts/libpart')};net={ (x.attrib['ref'],x.attrib['pin']):n.attrib['name'] for n in r.findall('./nets/net') for x in n.findall('node')};out=[]
for ref,pin,want in [('U201','23','VCCB'),('U201','24','VCCB'),('U202','16','VCCB'),('U203','16','VCCB'),('U204','1','VCCA')]:
 name=libs[comps[ref]][pin]
 if name!=want or net[(ref,pin)]!='SENS_VIO_1V8':raise RuntimeError(ref+'.'+pin)
 out.append({'ref':ref,'pin':pin,'source_pin_name':name,'net':net[(ref,pin)]})
print(json.dumps({'status':'READ_ONLY_SOURCE_PIN_NAME_CORRECTION_NOT_A_WIRING_CHANGE','source_sha256':expected,'corrected_contract_sha256':contract_sha,'pins':out},indent=2))
