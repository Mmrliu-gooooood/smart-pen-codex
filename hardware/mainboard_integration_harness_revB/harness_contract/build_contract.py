from pathlib import Path
import hashlib,json,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent;R=D.parents[2]
def lock(p):
 f=R/p;return {'path':p,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
def pins(xml,ref):
 t=E.parse(R/xml);return {x.get('pin'):n.get('name') for n in t.findall('./nets/net') for x in n if x.get('ref')==ref}
main='hardware/rf_width14_selected_board_candidate';power='hardware/power14_single_feed_revB';old='hardware/power_core_layout_candidate'
def version(prefix,basename,ref,extra=[]):
 files=[f'{prefix}/{basename}.{ext}' for ext in ['kicad_pcb','kicad_sch','xml']]+[f'{prefix}/{x}' for x in extra]
 return {'reference':ref,'files':[lock(x) for x in files],'xml':files[2],'pins':pins(files[2],ref)}
require_hash=hashlib.sha256((R/main/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest()
if require_hash!='016d963f764430b6122da29039a5573792e3f0c78078180b18582af69b044c7e':raise RuntimeError('selected board revision mismatch')
m=version(main,'mainboard_revD','J107',[str(p.relative_to(R/main)) for p in sorted((R/main/'schematic').glob('*.kicad_sch'))])
if hashlib.sha256((R/power/'power_integrated_study.kicad_pcb').read_bytes()).hexdigest()!='94ced2bd4100ba6fd8d9a9af11f101cc091a4c112a1bb3c8bb5dec2b2dedcdbc':raise RuntimeError('Rev B power board changed')
p=version(power,'power_integrated_study','J5',['core.kicad_sch','thermal.kicad_sch']);o=version(old,'power_core_NOFAB','J5')
c={'schema':1,'status':'NOFAB source-version mapping; present mainboard J107 pads routed, physical harness not qualified','mainboard':m,'target':p,'explicitly_incompatible_legacy':o,'wires':[{'signal':sig,'source':{'ref':'J107','pin':str(i),'net':sig},'target':{'ref':'J5','pin':str(i),'net':p['pins'][str(i)]}} for i,sig in enumerate(['USB_EN1','USB_EN2','GND'],1)],'historical_original_14x45':version('hardware/power_integrated_layout_14x45','power_integrated_study','J5',['core.kicad_sch','thermal.kicad_sch']),'requirements':['No external CE pin exists on this integrated target','No charge permission is conveyed by this 3-wire interface','Present mainboard EN1/EN2 copper checked separately; physical harness, strain relief, defaults/brownout still require qualification','No battery, camera or commissioning bridge is authorized by contract success']}
(D/'power_mode_mapping.json').write_text(json.dumps(c,indent=2)+'\n')
print('Written exact version locks; target pins',p['pins'],'legacy pins',o['pins'])
