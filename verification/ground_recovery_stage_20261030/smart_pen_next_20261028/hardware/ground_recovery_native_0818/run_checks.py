from pathlib import Path
import subprocess,os,json
D=Path(__file__).resolve().parent;BASE=D.parent/'camera_schmitt_native_0745/native';env=dict(os.environ,XDG_CONFIG_HOME='/tmp/ground0818/config',XDG_CACHE_HOME='/tmp/ground0818/cache',XDG_DATA_HOME='/tmp/ground0818/data')
for x in ['config','cache','data']:Path('/tmp/ground0818/'+x).mkdir(parents=True,exist_ok=True)
rows=[]
for label,native in [('base',BASE),('candidate',D/'native')]:
 out=D/'checks'/label;out.mkdir(parents=True,exist_ok=True);sch=native/'mainboard_revD.kicad_sch';pcb=native/'mainboard_revD.kicad_pcb'
 commands={
 'netlist':['sch','export','netlist','--format','kicadxml','-o',str(out/'netlist.xml'),str(sch)],
 'bom':['sch','export','bom','--fields','Reference,Value,Footprint,MPN,MPN_candidate,${QUANTITY},${DNP}','--labels','Reference,Value,Footprint,MPN,MPN_candidate,Qty,DNP','-o',str(out/'bom.csv'),str(sch)],
 'erc':['sch','erc','--format','json','--severity-all','--exit-code-violations','-o',str(out/'erc.json'),str(sch)],
 'drc':['pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','-o',str(out/'drc.json'),str(pcb)]}
 for kind,args in commands.items():
  r=subprocess.run(['kicad-cli']+args,env=env,capture_output=True,text=True);(out/(kind+'.log')).write_text(r.stdout+r.stderr);rows.append(dict(label=label,kind=kind,command=['kicad-cli']+args,exit=r.returncode));print(label,kind,r.returncode,flush=True)
(D/'cli_results.json').write_text(json.dumps(rows,indent=2)+'\n')
