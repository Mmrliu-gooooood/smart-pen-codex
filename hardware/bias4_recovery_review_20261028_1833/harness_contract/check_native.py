from pathlib import Path
import os,subprocess,json,xml.etree.ElementTree as E
D0=Path(__file__).resolve().parent
for key,part in [("XDG_CONFIG_HOME","config"),("XDG_CACHE_HOME","cache"),("XDG_DATA_HOME","data")]:os.environ[key]=str(D0/"xdg"/part)
import pcbnew as p
from verify_mapping import ROOT,D,validate,pins,ContractError
c=json.loads((D/'power_mode_mapping.json').read_text());validate(c)
env=dict(os.environ,XDG_CONFIG_HOME=str(D/'xdg/config'),XDG_CACHE_HOME=str(D/'xdg/cache'),XDG_DATA_HOME=str(D/'xdg/data'));rows=[]
for label,v in [('mainboard',c['mainboard']),('integrated_target',c['target']),('legacy_incompatible',c['explicitly_incompatible_legacy'])]:
 sch=next(x['path'] for x in v['files'] if x['path'].endswith('.kicad_sch'));out=D/(label+'_fresh.xml')
 r=subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(out),str(ROOT/sch)],capture_output=True,text=True,env=env)
 (D/(label+'_export.log')).write_text(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError('fresh XML export failed '+label)
 actual=pins(D,out.name,v['reference'])
 if actual!=v['pins']:raise RuntimeError('Fresh native endpoint mismatch '+label)
 board=next(x['path'] for x in v['files'] if x['path'].endswith('.kicad_pcb'));b=p.LoadBoard(str(ROOT/board));fps=[x for x in b.GetFootprints() if x.GetReference()==v['reference']]
 if label=='mainboard':
  if fps:raise RuntimeError('Mainboard state changed: repeat integration review')
  rows.append({'label':label,'fresh_pins':actual,'footprint_present':False,'physical_harness_blocker':'J107 mainboard footprint still absent'})
 else:
  if len(fps)!=1:raise RuntimeError('Target footprint count '+label)
  pd={a.GetNumber():a.GetNetname() for a in fps[0].Pads()}
  if pd!=actual:raise RuntimeError('Actual PCB pad/net mismatch '+label)
  rows.append({'label':label,'fresh_pins':actual,'footprint_present':True,'actual_pad_nets':pd,'footprint':str(fps[0].GetFPID().GetLibNickname())+':'+str(fps[0].GetFPID().GetLibItemName())})
(D/'native_port_evidence.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
