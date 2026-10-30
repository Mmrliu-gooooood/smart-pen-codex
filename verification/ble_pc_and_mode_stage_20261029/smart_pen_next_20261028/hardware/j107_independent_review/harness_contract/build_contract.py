from pathlib import Path
import hashlib,json,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent;R=D.parents[2]
old=R/'hardware/mainboard_integration_harness_revB/harness_contract/power_mode_mapping.json'
c=json.loads(old.read_text());prefix='hardware/j107_mode_port_closure';p=R/prefix
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if sha(p/'native/mainboard_revD.kicad_pcb')!='8aa2581b4df112b979d83e67b9a6a2ddaa70a433c265cdc9849e41b60ff05ab5':raise RuntimeError('Wrong current board')
if sha(p/'fresh.xml')!='ac032f04e770941067d7ddd6991356d58827c5b55932ba895a2d862eb1ee97d9':raise RuntimeError('Wrong fresh XML')
files=[p/'native/mainboard_revD.kicad_pcb',p/'fresh.xml',*sorted((p/'native').rglob('*.kicad_sch')),p/'manifest.json']
if sha(p/'manifest.json')!='49250127029a2e9ab5c8399eb0ada354b18050e716fcc94a3bfe79e35cd73c64':raise RuntimeError('Wrong frozen routing stage')
pins={x.get('pin'):n.get('name') for n in E.parse(p/'fresh.xml').findall('./nets/net') for x in n if x.get('ref')=='J107'}
if pins!={'1':'USB_EN1','2':'USB_EN2','3':'GND'}:raise RuntimeError('Wrong J107 native source')
c['mainboard']={'reference':'J107','files':[{'path':str(f.relative_to(R)),'sha256':sha(f)} for f in files],'xml':str((p/'fresh.xml').relative_to(R)),'pins':pins}
c['status']='NOFAB current 102-footprint J107 source/PCB identity; physical three-wire harness and charge permission not qualified'
c['historical_selected016d_mainboard']=json.loads(old.read_text())['mainboard']
c['requirements'] += ['Each mainboard native pad net is cross-checked against fresh XML, not only pin numbers','Current 102-footprint board must not be substituted by earlier 016d mainboard identity','No physical polarity key, wire gauge, strain relief or assembly proof is implied by logical map']
(D/'power_mode_mapping.json').write_text(json.dumps(c,indent=2)+'\n')
print('Prepared exact frozen current native identity')
