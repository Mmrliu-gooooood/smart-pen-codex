#!/usr/bin/env python3
"""Independent hand-written electrical contract. Does not import build.py or design_manifest."""
import os,subprocess,json,xml.etree.ElementTree as E,hashlib,re,csv
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parents[1];env=os.environ.copy()
for x,y in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:env[x]='/tmp/rebuild-kicad/'+y
for args in [['sch','erc','--exit-code-violations','-o',str(P/'erc.rpt'),str(P/'camera_isolation.kicad_sch')],['sch','export','netlist','--format','kicadxml','-o',str(P/'camera_isolation.xml'),str(P/'camera_isolation.kicad_sch')]]:subprocess.run(['kicad-cli']+args,env=env,check=True)
r=E.parse(P/'camera_isolation.xml').getroot();expected={};values={}
def part(ref,pins,value=None):
 for pin,net in (pins.items() if isinstance(pins,dict) else enumerate(pins,1)):expected[ref,str(pin)]=net
 if value:values[ref]=value
part('U1',['3V3_AON','GND','CAM_D0','CAM_D1','CAM_D2','CAM_D3','CAM_D4','CAM_D5','CAM_D6','CAM_D7','GND','GND','GND','SENS_D7','SENS_D6','SENS_D5','SENS_D4','SENS_D3','SENS_D2','SENS_D1','SENS_D0','CAM_ISO_OE_N','SENS_VIO_1V8','SENS_VIO_1V8'],'SN74AXC8T245PWR')
part('U2',['3V3_AON','GND','GND','CAM_PCLK','CAM_VSYNC','CAM_HREF',None,'GND','GND','UNUSED_B_INPUT','SENS_HREF','SENS_VSYNC','SENS_PCLK','CAM_ISO_OE_N','CAM_ISO_OE_N','SENS_VIO_1V8'],'SN74AXC4T245PWR')
part('U3',['3V3_AON','3V3_AON','3V3_AON','CAM_XCLK','CAM_RESET_UART_TX','CAM_PWDN_UART_RX','UNUSED_A_INPUT','GND','GND',None,'SENS_TRIG_IN','SENS_XSHUTDN_N','SENS_EXTCLK','CAM_ISO_OE_N','CAM_ISO_OE_N','SENS_VIO_1V8'],'SN74AXC4T245PWR')
part('U4',['SENS_VIO_1V8','SENS_SCL','SENS_SDA','GND','SCCB_EN_SAFE','CAM_SDA','CAM_SCL','3V3_AON'],'TCA9517DGKR')
part('Q1',['ISO_GATE','GND','CAM_ISO_OE_N'],'PMV30UN2')
part('JP1',['CAM_IO_EN','IO_ENABLE_LINK'],'DNP_IO_COMMISSION');part('JP2',['CAM_BUS_EN','SCCB_ENABLE_LINK'],'DNP_SCCB_COMMISSION')
for i,(a,b,v) in enumerate([('IO_ENABLE_LINK','ISO_GATE','1k 1%'),('ISO_GATE','GND','100k 1%'),('CAM_ISO_OE_N','3V3_AON','10k 1%'),('SCCB_ENABLE_LINK','SCCB_EN_SAFE','100R 1%'),('SCCB_EN_SAFE','GND','4.7k 1%'),('UNUSED_B_INPUT','GND','10k 1%'),('UNUSED_A_INPUT','GND','10k 1%')],1):part('R'+str(i),[a,b],v)
for i in range(1,9):part('C'+str(i),['3V3_AON' if i%2 else 'SENS_VIO_1V8','GND'],'100n X7R')
host=['CAM_D0','CAM_D1','CAM_D2','CAM_D3','CAM_D4','CAM_D5','CAM_D6','CAM_D7','CAM_PCLK','CAM_VSYNC','CAM_HREF','CAM_XCLK','CAM_RESET_UART_TX','CAM_PWDN_UART_RX','CAM_SCL','CAM_SDA','CAM_IO_EN','CAM_BUS_EN','3V3_AON','GND']
sensor=['SENS_D0','SENS_D1','SENS_D2','SENS_D3','SENS_D4','SENS_D5','SENS_D6','SENS_D7','SENS_PCLK','SENS_VSYNC','SENS_HREF','SENS_EXTCLK','SENS_XSHUTDN_N','SENS_TRIG_IN','SENS_SCL','SENS_SDA','SENS_VIO_1V8','GND']
part('J1',host,'HOST_3V3_SEMANTIC');part('J2',sensor,'SENSOR_1V8_SEMANTIC_NOT_FPC')
for i,n in enumerate(host[:14]+sensor[:14],10):part('R'+str(i),[n,'GND'],'4.7k 1% RESET_CANDIDATE' if n=='SENS_XSHUTDN_N' else '100k 1%')
for i,n in enumerate(['CAM_SCL','CAM_SDA','SENS_SCL','SENS_SDA'],40):part('R'+str(i),[n,'3V3_AON' if i<42 else 'SENS_VIO_1V8'],'10k 1% INITIAL_100kHz')
actual={}
for net in r.findall('./nets/net'):
 for node in net.findall('node'):actual[node.get('ref'),node.get('pin')]=net.get('name')
errors=[]
for k,v in expected.items():
 got=actual.get(k)
 if v is None:
  if got and not got.startswith('unconnected-'):errors.append([k,v,got])
 elif got!=v:errors.append([k,v,got])
comps={c.get('ref'):c for c in r.findall('./components/comp')};assert set(comps)=={k[0] for k in expected},'empty/partial/unexpected component list'
for ref,c in comps.items():
 lib=c.find('libsource');lp=r.find(f'./libparts/libpart[@lib="{lib.get("lib")}"][@part="{lib.get("part")}"]')
 for pin in lp.findall('./pins/pin'):assert (ref,pin.get('num')) in expected,'pin omitted from independent contract'
for ref,v in values.items():assert comps[ref].findtext('value')==v,(ref,'wrong value')
assert {ref for ref,c in comps.items() if c.find('property[@name="dnp"]') is not None}=={'JP1','JP2'}
# Assert real symbol pin functions, avoiding silent pin-number permutations.
function_checks={'U1':{'1':'VCCA','2':'DIR1','11':'DIR2','12':'GND','13':'GND','22':'OE_N','23':'VCCB','24':'VCCB'},'U2':{'1':'VCCA','2':'1DIR','3':'2DIR','8':'GND','9':'GND','14':'2OE_N','15':'1OE_N','16':'VCCB'},'U3':{'4':'1A1','5':'1A2','6':'2A1','7':'2A2','10':'2B2','11':'2B1','12':'1B2','13':'1B1'},'U4':{'1':'VCCA','2':'SCLA','3':'SDAA','4':'GND','5':'EN','6':'SDAB','7':'SCLB','8':'VCCB'},'Q1':{'1':'G','2':'S','3':'D'}}
for ref,pins in function_checks.items():
 l=comps[ref].find('libsource');lp=r.find(f'./libparts/libpart[@lib="{l.get("lib")}"][@part="{l.get("part")}"]')
 for pn,name in pins.items():assert lp.find(f'./pins/pin[@num="{pn}"]').get('name')==name
footchecks={}
for ref,c in comps.items():
 fp=c.findtext('footprint')
 if not fp:continue
 lib,name=fp.split(':');path=Path('/usr/share/kicad/footprints')/(lib+'.pretty')/(name+'.kicad_mod');assert path.exists(),str(path)
 pads=set(re.findall(r'\(pad "([^"\n]+)"',path.read_text()));footchecks[ref]=pads=={k[1] for k in expected if k[0]==ref};assert footchecks[ref]
report={'checked_utc':datetime.now(timezone.utc).isoformat(),'component_count':len(comps),'pin_checks':len(expected),'value_checks':len(values),'real_DNP_links_checked':['JP1','JP2'],'mismatches':errors,'footprint_number_sets':footchecks,'status':'PASS' if not errors else 'FAIL','pcb':False,'NOFAB':True,'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in P.glob('*.kicad_sch')}}
(P/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not errors
with (P/'bom_candidates.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['Reference','Candidate_value','Footprint_candidate','DNP','Qualification','Unit_price_CNY'])
 for ref,c in comps.items():w.writerow([ref,c.findtext('value'),c.findtext('footprint',''),ref in ['JP1','JP2'],'NOFAB; sourcing/landpattern/temperature qualification pending','UNQUOTED'])
