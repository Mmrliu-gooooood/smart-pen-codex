#!/usr/bin/env python3
from pathlib import Path
import os,subprocess,xml.etree.ElementTree as E,json,hashlib,csv
from datetime import datetime,timezone
P=Path(__file__).resolve().parent
env=os.environ.copy()
for k,t in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:env[k]='/tmp/illum-kicad/'+t
for args in [['sch','erc','--exit-code-violations','-o','erc.rpt','illumination_NOFAB.kicad_sch'],['sch','export','netlist','--format','kicadxml','-o','illumination_NOFAB.xml','illumination_NOFAB.kicad_sch'],['sch','export','pdf','-o','review.pdf','illumination_NOFAB.kicad_sch']]:subprocess.run(['kicad-cli']+args,cwd=P,env=env,check=True)
r=E.parse(P/'illumination_NOFAB.xml').getroot()
# Independent hand-entered contract, not build.py or its manifest.
expected={'J1':{'1':'3V3_AON','2':'GND','3':'ILLUM_STROBE'},'JP1':{'1':'3V3_AON','2':'LED_COMMISSIONED'},'R1':{'1':'LED_COMMISSIONED','2':'LED_A'},'J2':{'1':'LED_A','2':'LED_K'},'Q1':{'1':'LED_GATE','2':'GND','3':'LED_K'},'R2':{'1':'ILLUM_STROBE','2':'LED_GATE'},'R3':{'1':'LED_GATE','2':'GND'}}
actual={};names={}
for n in r.findall('./nets/net'):
 for p in n.findall('node'):actual[(p.get('ref'),p.get('pin'))]=n.get('name').removeprefix('/');names[(p.get('ref'),p.get('pin'))]=p.get('pinfunction')
exp={(ref,pin):net for ref,ps in expected.items() for pin,net in ps.items()}
assert actual==exp,(actual,exp)
assert {k[1]:v for k,v in names.items() if k[0]=='Q1'}=={'1':'G','2':'S','3':'D'}
components={c.get('ref'):c for c in r.findall('./components/comp')};assert set(components)==set(expected)
values={'R1':'330R 1% >=0.1W','R2':'1k 1%','R3':'100k 1%','Q1':'PMV30UN2'}
for ref,value in values.items():assert components[ref].findtext('value')==value
assert components['JP1'].find('property[@name="dnp"]') is not None
# Only external two-terminal passive LED load allowed; no module power pin aliases.
assert len([k for k in actual if k[0]=='J2'])==2
Rmin=330*.99;imax=3.6/Rmin;pmax=3.6**2/Rmin
report={'checked_utc':datetime.now(timezone.utc).isoformat(),'status':'PASS','pins_checked':len(exp),'component_count':len(components),'values_checked':len(values),'mosfet_pin_functions_verified':True,'JP1_actual_DNP':True,'shorted_load_current_bound_mA':imax*1000,'R1_short_load_power_bound_mW':pmax*1000,'bounds_conditions':'3V3_AON <= 3.6V; R1 330R +/-1%; no bypass of resistor; not single-fault-safe if R1 shorts','schematic_sha256':hashlib.sha256((P/'illumination_NOFAB.kicad_sch').read_bytes()).hexdigest(),'netlist_sha256':hashlib.sha256((P/'illumination_NOFAB.xml').read_bytes()).hexdigest(),'PCB_present':False,'optical_safety_qualified':False}
(P/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
with (P/'bom_candidates.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['Ref','Value','Footprint_candidate','DNP','Status'])
 for ref,c in components.items():w.writerow([ref,c.findtext('value'),c.findtext('footprint',''),c.find('property[@name="dnp"]') is not None,'NOFAB; quote/assembly/optical qualification not complete'])
print(json.dumps(report,indent=2))
