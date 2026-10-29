from pathlib import Path
import hashlib,json,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent;R=D.parents[2]
def lock(p):
 f=R/p;return {'path':p,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
def pins(xml,ref):
 t=E.parse(R/xml);return {x.get('pin'):n.get('name') for n in t.findall('./nets/net') for x in n if x.get('ref')==ref}
main='hardware/mainboard_resume_20261028';power='hardware/power_integrated_layout_14x45';old='hardware/power_core_layout_candidate'
def version(prefix,basename,ref,extra=[]):
 files=[f'{prefix}/{basename}.{ext}' for ext in ['kicad_pcb','kicad_sch','xml']]+[f'{prefix}/{x}' for x in extra]
 return {'reference':ref,'files':[lock(x) for x in files],'xml':files[2],'pins':pins(files[2],ref)}
m=version(main,'mainboard_revD','J107',['schematic/'+n for n in ['mcu_core.kicad_sch','usb_entry.kicad_sch','dvp_translation.kicad_sch','controls_sccb.kicad_sch','safe_bias_interfaces.kicad_sch']])
p=version(power,'power_integrated_study','J5',['core.kicad_sch','thermal.kicad_sch']);o=version(old,'power_core_NOFAB','J5')
c={'schema':1,'status':'NOFAB logical contract only; mainboard J107 physical footprint absent','mainboard':m,'target':p,'explicitly_incompatible_legacy':o,'wires':[{'signal':sig,'source':{'ref':'J107','pin':str(i),'net':sig},'target':{'ref':'J5','pin':str(i),'net':p['pins'][str(i)]}} for i,sig in enumerate(['USB_EN1','USB_EN2','GND'],1)],'requirements':['No external CE pin exists on this integrated target','No charge permission is conveyed by this 3-wire interface','Mainboard physical lands/connector, return path, strain relief, default/brownout behavior still required','No battery, camera or commissioning bridge is authorized by contract success']}
(D/'power_mode_mapping.json').write_text(json.dumps(c,indent=2)+'\n')
print('Written exact version locks; target pins',p['pins'],'legacy pins',o['pins'])
