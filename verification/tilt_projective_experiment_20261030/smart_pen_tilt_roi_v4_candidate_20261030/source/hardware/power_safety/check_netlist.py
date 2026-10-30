"""Independent expected nets manually transcribed from TI pins + reviewed architecture, not generator data."""
from pathlib import Path
import xml.etree.ElementTree as ET,json,hashlib,datetime
p=Path(__file__).parent
expected={'3V3_AON':'U1.1 C1.1','GND':'U1.2 C1.2 C2.2 C3.2 R1.2 J1.2','CAM_PWR_EN':'R2.1 TP1.1','CAM_ON':'R2.2 R1.1 U1.3','CAM_CT':'U1.4 C3.1','CAM_QOD':'U1.5 R3.2','CAM_3V3_PRELINK':'U1.6 C2.1 R3.1 JP1.1','CAM_3V3_SW':'JP1.2 J1.1'}
root=ET.parse(p/'power_safety_NOFAB.xml').getroot()
actual={n.get('name').lstrip('/'):{x.get('ref')+'.'+x.get('pin') for x in n.findall('node') if not x.get('ref').startswith('#')} for n in root.findall('./nets/net')}
assert actual=={n:set(v.split()) for n,v in expected.items()},actual
values={'TP1':'ENABLE MEASURE','U1':'TPS22918DBVR','R1':'100k 1%','R2':'1k 1%','R3':'100R 1%','C1':'10uF 10V X7R','C2':'1uF 10V X7R','C3':'1nF 25V C0G','JP1':'OPEN / DO NOT BRIDGE','J1':'APPROVED LOAD / TBD'}
comps={c.get('ref'):c for c in root.findall('./components/comp')}
assert set(comps)==set(values)
for ref,value in values.items():assert comps[ref].findtext('value')==value
assert any(x.get('name')=='dnp' for x in comps['JP1'].findall('property'))
assert all(not c.findtext('footprint') for c in comps.values())
sch=(p/'power_safety_NOFAB.kicad_sch').read_text()
assert '(hierarchical_label "CAM_PWR_EN" (shape input)' in sch
# Approximate design calculations, NOT guaranteed timing or actual camera load.
calcs={'ON_low_from_switch_leakage_only_V':.1e-6*101000,'ON_high_at_3V_GPIO_min_resistors_V':3*99000/(99000+1010),'R1_on_bias_at3V3_uA':3.3/101000*1e6,'CT_formula_typ_rise_us':(.55*1000+30)*3.3,'example_CL11uF_ramp_current_mA':11e-6/(580e-6)*1000}
assert calcs['ON_low_from_switch_leakage_only_V']<.5
assert calcs['ON_high_at_3V_GPIO_min_resistors_V']>1
out={'provenance':'NEW CIRCUIT AND NEW CHECK, not restored original','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pins_checked':sum(len(v.split()) for v in expected.values()),'values_checked':len(values),'JP1_DNP':True,'mismatches':[],'calculations_not_measurements':calcs,'schematic_sha256':hashlib.sha256(sch.encode()).hexdigest(),'netlist_sha256':hashlib.sha256((p/'power_safety_NOFAB.xml').read_bytes()).hexdigest(),'release':'NO FAB; no camera or cell approval'}
(p/'netlist_check.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
