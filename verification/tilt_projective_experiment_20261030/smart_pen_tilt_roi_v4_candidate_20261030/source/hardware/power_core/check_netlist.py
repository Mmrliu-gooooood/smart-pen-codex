"""Independent hand-reviewed network expectations; does not import generator or its data."""
from pathlib import Path
import json,hashlib,datetime,xml.etree.ElementTree as E
p=Path(__file__).parent
expected={
'PACK_NTC':'U1.1 J1.1',
'PACK_PLUS_PROTECTED':'U1.2 U1.3 C2.1',
'CHARGE_DISABLE':'U1.4 R6.2 JP1.1',
'USB_EN2':'U1.5 R5.1','USB_EN1':'U1.6 R4.1',
'GND':'U1.8 U1.17 U2.2 U2.3 U2.8 C1.2 C2.2 C3.2 C4.2 C5.2 C6.2 R1.2 R2.2 R3.2 R4.2 R5.2 R8.2 JP1.2 J1.2',
'SYS_RAW':'U1.10 U1.11 U2.1 U2.10 C3.1 C4.1',
'CHG_ILIM':'U1.12 R2.1','VBUS_5V':'U1.13 C1.1 R6.1',
'CHG_TMR':'U1.14 R3.1','CHG_ISET':'U1.16 R1.1',
'REG_FB':'U2.4 R7.2 R8.1','3V3_AON':'U2.6 R7.1 C5.1 C6.1',
'SW_L1':'U2.9 L1.1','SW_L2':'U2.7 L1.2'}
nc={'U1.7','U1.9','U1.15','U2.5'}
actual={};actual_nc=set()
xmlroot=E.parse(p/'power_core_NOFAB.xml').getroot()
comps={c.get('ref'):c for c in xmlroot.findall('./components/comp')}
required_values={'U1':'BQ24074RGTR','U2':'TPS63802DLAR','R1':'8.66k 1%','R2':'3.24k 1%','R3':'68k 1%','R4':'100k','R5':'100k','R6':'10k 1%','R7':'511k 1%','R8':'91k 1%','JP1':'OPEN / DO NOT BRIDGE'}
for ref,value in required_values.items():assert comps[ref].findtext('value')==value,(ref,value)
assert any(x.get('name')=='dnp' for x in comps['JP1'].findall('property'))
assert all(not c.findtext('footprint') and not c.findtext("./fields/field[@name='Footprint']") for c in comps.values())
for n in E.parse(p/'power_core_NOFAB.xml').findall('./nets/net'):
 name=n.get('name').lstrip('/');nodes={z.get('ref')+'.'+z.get('pin') for z in n.findall('node') if not z.get('ref').startswith('#')}
 if name.startswith('unconnected-'):
  assert len(nodes)==1;actual_nc|=nodes
 else:actual[name]=nodes
errors=[]
for name,nodes in expected.items():
 if actual.get(name)!=set(nodes.split()):errors.append({'net':name,'expected':nodes.split(),'actual':sorted(actual.get(name,[]))})
if set(actual)!=set(expected):errors.append({'extra_or_missing_nets':sorted(set(actual)^set(expected))})
if actual_nc!=nc:errors.append({'NC_mismatch':sorted(actual_nc^nc)})
sch=(p/'power_core_NOFAB.kicad_sch').read_text()
assert '(dnp yes)' in sch
assert 'OPEN / DO NOT BRIDGE' in sch
values={'iset_min_mA':797/(8660*1.01)*1000,'iset_nom_mA':890/8660*1000,'iset_max_mA':975/(8660*.99)*1000,'ilim_max_mA':1720/(3240*.99)*1000,'CE_open_5V_typ_uA':5/(10000+285000)*1e6,'CE_open_5V_typ_V':5*285000/(10000+285000),'CE_closed_5V_nom_mA':5/10000*1000,'Vout_nom_V':.5*(1+511000/91000)}
assert 91.11<values['iset_min_mA']<91.13 and 113.72<values['iset_max_mA']<113.74
assert 536.22<values['ilim_max_mA']<536.24
out={'provenance':'NEW 2026-10-28 RECONSTRUCTION CHECK, not old results','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'schematic_sha256':hashlib.sha256(sch.encode()).hexdigest(),'netlist_sha256':hashlib.sha256((p/'power_core_NOFAB.xml').read_bytes()).hexdigest(),'value_checks':len(required_values),'JP1_DNP_checked_from_export':True,'pins_checked':sum(len(x.split()) for x in expected.values())+len(nc),'mismatches':errors,'calculations':values,'release_status':'NO FAB; battery/NTC/footprints/USB-total-current unqualified'}
(p/'netlist_check.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(json.dumps(out,indent=2,ensure_ascii=False));raise SystemExit(bool(errors))
