from pathlib import Path
import os,json,sys,hashlib,xml.etree.ElementTree as ET
os.environ['XDG_CONFIG_HOME']='/tmp/data1226source'
import pcbnew as p
D=Path(__file__).resolve().parent;A=D.parent/'sccb_local_reference_1216';sys.path.insert(0,str(D.parent/'translator_domain_candidate_0130'));from finite_copper import build,components
f=A/'native/mainboard_revD.kicad_pcb'
def req(c,s):
 if not c:raise RuntimeError(s)
req(hashlib.sha256(f.read_bytes()).hexdigest()=='dcbd2e6501c8294ece5ecf7b41ffcc86ccc7f58f7cb54ececfdf24962a50f697','accepted parent');b=p.LoadBoard(str(f));fp={x.GetReference():x for x in b.GetFootprints()};nodes=build(b);ground=next(c for c in components(nodes['GND'])if'J106.3'in c);aon=next(c for c in components(nodes['3V3_AON'])if'J106.2'in c);sens=next(c for c in components(nodes['SENS_VIO_1V8'])if'J202.23'in c)
req({'U201.2','U201.11','U201.12','U201.13'}<=set(ground),'both DIR and GND pins physically grounded');req('U201.1'in aon and{'U201.23','U201.24'}<=set(sens),'actual supply cores');req(fp['U201'].GetValue()=='SN74AXC8T245PWR','PW24 device')
xml=ET.parse(A/'checks/candidate/netlist.xml').getroot();pins={n.get('ref')+'.'+n.get('pin'):{'net':net.get('name'),'function':n.get('pinfunction')}for net in xml.findall('./nets/net')for n in net.findall('node')};rows=[]
for i in range(8):
 ref='R'+str(210+i);pin='U201.'+str(3+i);net='CAM_D'+str(i);req(pins[pin]=={'net':net,'function':'A'+str(i+1)},'pin role '+pin);req(fp[ref].GetValue()=='100k 1%','bias value');req(ref+'.2'in ground,'bias resistor ground physically connected')
 cs=components(nodes[net]);req([pin]in cs and[ref+'.1']in cs,'both known endpoints currently isolated');rows.append({'net':net,'pin':pin,'function':'A'+str(i+1),'resistor':ref,'value':fp[ref].GetValue(),'resistor_ground_in_main_core':True,'before_components':cs,'bias_side':b.GetLayerName(fp[ref].GetLayer())})
print(json.dumps({'status':'EXACT_PW_ROLE_AND_PHYSICAL_CORE_VERIFIED_NOT_DYNAMIC_QUALIFICATION','rows':rows,'both_direction_inputs_main_GND':True,'AON_core_count':len(aon),'SENS_core_count':len(sens),'GND_core_count':len(ground),'enabled_role':'A outputs with B-to-A direction; disabled I/O input circuits remain active','manufacturer_source':'TI SCES875C Table4-1,7-1 and sections7.3.4/8.4; external100k unchanged, typical internal288k not worst-case assurance','limits':['No asserted sensor/MCU functionality','No universal leakage/loadedVOH/edge/stub acceptance','Full pad islands not merely logical GND labels']},indent=2))
