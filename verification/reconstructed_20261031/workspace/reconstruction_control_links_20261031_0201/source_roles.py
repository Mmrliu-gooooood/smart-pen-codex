from pathlib import Path
import json,xml.etree.ElementTree as E,hashlib
D=Path(__file__).resolve().parent;f=D/'review_dependencies/source_netlist.xml';x=E.parse(f).getroot();pins={a.get('ref')+'.'+a.get('pin'):{'net':n.get('name'),'function':a.get('pinfunction')}for n in x.findall('./nets/net')for a in n.findall('node')};values={a.get('ref'):a.findtext('value')for a in x.findall('./components/comp')};checks={}
def req(k,v):
 checks[k]=bool(v)
 if not v:raise RuntimeError(k)
for n,m,u,r in [('CAM_SCL','U101.44','U204.7','R240'),('CAM_SDA','U101.45','U204.6','R241')]:
 req(n,all(pins[a]['net']==n for a in [m,u,r+'.1']));req(r+'_pullup',values[r]=='10k 1% INITIAL_100kHz'and pins[r+'.2']['net']=='3V3_AON')
for pin,net in [('U204.8','3V3_AON'),('U204.1','SENS_VIO_1V8'),('U204.5','SCCB_EN_SAFE')]:req(pin,pins[pin]['net']==net)
r={'checks':checks,'netlist_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'values':{r:values[r]for r in ['U101','U204','R240','R241']},'pins':{r:pins[r]for r in ['U101.44','U101.45','U204.7','U204.6','U204.8','U204.1','U204.5']},'scope':'Static original roles only; actual open-drain GPIO/JTAG startup ownership, loaded VOL<0.4V and RC/edge/power/EN behavior remain open.'};(D/'source_roles.json').write_text(json.dumps(r,indent=2));print(checks)
