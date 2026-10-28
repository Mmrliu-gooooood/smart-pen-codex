#!/usr/bin/env python3
"""Independent pin contract: not imported from generator/design.json."""
import pathlib,subprocess,os,xml.etree.ElementTree as ET,json,datetime,hashlib
P=pathlib.Path(__file__).resolve().parents[1]
os.environ.update(XDG_CONFIG_HOME='/tmp/pen-kicad/config',XDG_CACHE_HOME='/tmp/pen-kicad/cache',XDG_DATA_HOME='/tmp/pen-kicad/data')
subprocess.run(['kicad-cli','sch','erc',str(P/'pickup_contact.kicad_sch'),'-o',str(P/'erc.rpt'),'--exit-code-violations'],check=True)
subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(P/'pickup_contact.xml'),str(P/'pickup_contact.kicad_sch')],check=True)
V='3V3_AON';G='GND';S='AON_I2C_SCL';D='AON_I2C_SDA';N='NIB_CONTACT_N'
expected={'U1':{1:S,2:V,3:V,4:D,5:G,6:G,7:G,8:G,9:V,10:V,12:'PICKUP_INT_N'},'J1':{1:V,2:G,3:S,4:D,5:'PICKUP_INT_N',6:N},'J2':{1:'CONTACT',2:G},'R1':{1:V,2:S},'R2':{1:V,2:D},'R3':{1:V,2:N},'R4':{1:N,2:'CONTACT'},'C1':{1:V,2:G},'C2':{1:V,2:G},'C3':{1:V,2:G},'C4':{1:N,2:G}}
actual={}
for net in ET.parse(P/'pickup_contact.xml').getroot().findall('./nets/net'):
 for node in net.findall('node'):actual[(node.attrib['ref'],int(node.attrib['pin']))]=net.attrib['name']
errors=[]
for ref,pins in expected.items():
 for pin,net in pins.items():
  if actual.get((ref,pin))!=net:errors.append([ref,pin,net,actual.get((ref,pin))])
nc=actual.get(('U1',11),'');ncok=not nc or nc.startswith('unconnected-')
if not ncok:errors.append(['U1',11,'NC',nc])
report={'rebuild_date':'2026-10-28','checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'connected_pins_checked':sum(map(len,expected.values())),'explicit_nc_checked':1,'mismatches':errors,'source_sha256':hashlib.sha256((P/'pickup_contact.kicad_sch').read_bytes()).hexdigest(),'scope':'Fresh schematic ERC and independent XML pin comparison; not a whole-pen validation'}
(P/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not errors
# PCB is checked against the independently specified pins, not only ERC.
import pcbnew as b
bd=b.LoadBoard(str(P/'pickup_contact.kicad_pcb'));pcb_errors=[]
for f in bd.GetFootprints():
 for pad in f.Pads():
  ref=f.GetReference();pin=int(pad.GetNumber());want=expected.get(ref,{}).get(pin)
  if want is not None and pad.GetNetname()!=want:pcb_errors.append([ref,pin,want,pad.GetNetname()])
ends=[p for shape in bd.GetDrawings() if shape.GetLayer()==b.Edge_Cuts for p in (shape.GetStart(),shape.GetEnd())];dimensions=[round(b.ToMM(max(p.x for p in ends)-min(p.x for p in ends)),4),round(b.ToMM(max(p.y for p in ends)-min(p.y for p in ends)),4)]
assert dimensions==[12.,20.],dimensions
assert abs(b.ToMM(bd.GetDesignSettings().GetBoardThickness())-.8)<1e-6
assert not pcb_errors,pcb_errors
subprocess.run(['kicad-cli','pcb','drc','--schematic-parity','--all-track-errors','--exit-code-violations','-o',str(P/'drc.rpt'),str(P/'pickup_contact.kicad_pcb')],check=True)
report.update(pcb_pin_mismatches=pcb_errors,pcb_dimensions_mm=dimensions,pcb_thickness_mm=.8,pcb_sha256=hashlib.sha256((P/'pickup_contact.kicad_pcb').read_bytes()).hexdigest(),pcb_drc='PASS fresh run; no exclusions',scope='Independent XML and PCB pin contracts, fresh ERC and DRC with schematic parity. Not whole-pen validation.')
(P/'verification.json').write_text(json.dumps(report,indent=2));print('PCB contracts and DRC PASS')
