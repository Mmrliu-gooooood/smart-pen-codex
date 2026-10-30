from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E
from sexpr import *
D=Path(__file__).resolve().parents[1];old=D.parent/'camera_isolation_control_native_0628';a=E.parse(old/'checks/candidate/netlist.xml').getroot();b=E.parse(D/'mainboard_revD.xml').getroot()
def pinmap(r):return {(n.get('ref'),n.get('pin')):(net.get('name'),n.get('pintype'),n.get('pinfunction')) for net in r.findall('./nets/net') for n in net.findall('node')}
def comps(r):return {c.get('ref'):c for c in r.findall('./components/comp')}
x,y=pinmap(a),pinmap(b);ca,cb=comps(a),comps(b)
if set(ca)-set(cb)!={'Q201'} or set(cb)-set(ca)!={'U205','C209'}:raise RuntimeError('ref delta')
for p,v in x.items():
 if p[0]=='Q201':continue
 if y.get(p)!=v:raise RuntimeError(('oldnetchanged',p,v,y.get(p)))
expected={'1':('unconnected-(U205-NC-Pad1)','no_connect','NC'),'2':('ISO_GATE','input','A'),'3':('GND','power_in','GND'),'4':('CAM_ISO_OE_N','output','Y'),'5':('3V3_AON','power_in','VCC')}
for pin,v in expected.items():
 if y.get(('U205',pin))!=v:raise RuntimeError(('U205pin',pin,y.get(('U205',pin))))
for p,n in [('1','3V3_AON'),('2','GND')]:
 if y[('C209',p)][0]!=n:raise RuntimeError('C209pin')
changed=[]
for ref in set(ca)&set(cb):
 for tagname in ['value','footprint','sheetpath','tstamps']:
  av=E.tostring(ca[ref].find(tagname));bv=E.tostring(cb[ref].find(tagname))
  if av!=bv:
   if ref!='R202' or tagname!='value':raise RuntimeError(('oldcompchanged',ref,tagname,av,bv))
   changed.append([ref,tagname,ca[ref].findtext(tagname),cb[ref].findtext(tagname)])
erc=(D/'erc.rpt').read_text()
if '** ERC messages: 1  Errors 0  Warnings 1' not in erc or "Global Label 'VBUS_5V'" not in erc:raise RuntimeError('unexpected ERC report')
# Footprint pad dimensions checked from actual generated library.
f=parse((D/'native/SmartPenIO.pretty/TI_DCK0005A_Schmitt_OfficialLand.kicad_mod').read_text());pads={val(p[1]):p for p in children(f,'pad')}
for pn,xx,yy in [('1',-1.1,-.65),('2',-1.1,0),('3',-1.1,.65),('4',1.1,.65),('5',1.1,-.65)]:
 p=pads[pn]
 if list(map(float,child(p,'at')[1:]))!=[xx,yy] or list(map(float,child(p,'size')[1:]))!=[.95,.4]:raise RuntimeError('padgeometry')
# Source-only no PCB; confirm frozen manifest all files unchanged.
m=json.loads((old/'manifest.json').read_text())
for row in m['files']:
 if hashlib.sha256((old/row['path']).read_bytes()).hexdigest()!=row['sha256']:raise RuntimeError('frozenchanged '+row['path'])
print(json.dumps({'status':'SOURCE_ONLY_CHECK_PASS_NOFAB_NOPOWER','old_component_count':len(ca),'new_component_count':len(cb),'old_pins_except_Q201_preserved':len(x)-3,'removed_refs':['Q201'],'added_refs':['U205','C209'],'changed_old_fields':changed,'U205_expected_netlist':expected,'C209_netlist':{p:y[('C209',p)] for p in ['1','2']},'official_lands_verified':True,'ERC_errors':0,'ERC_warnings':1,'ERC_warning':'pre-existing dangling VBUS_5V label','frozen_native_manifest_files_rehashed':len(m['files'])},indent=2))
