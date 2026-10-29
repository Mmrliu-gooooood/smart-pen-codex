from pathlib import Path
import subprocess,json,os
D=Path(__file__).resolve().parent;B=D.parent/'mainboard_resume_20261028'
env=dict(os.environ,XDG_CONFIG_HOME=str(D/'xdg/config'),XDG_CACHE_HOME=str(D/'xdg/cache'),XDG_DATA_HOME=str(D/'xdg/data'))
cmds=[('export',['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(D/'fresh.xml'),str(B/'mainboard_revD.kicad_sch')]),('erc',['kicad-cli','sch','erc','--severity-all','--exit-code-violations','-o',str(D/'erc.rpt'),str(B/'mainboard_revD.kicad_sch')]),('drc',['kicad-cli','pcb','drc','--severity-all','--all-track-errors','--schematic-parity','--exit-code-violations','-o',str(D/'drc.rpt'),str(B/'mainboard_revD.kicad_pcb')]),('audit',['/usr/bin/python3',str(D/'audit_native.py')]),('audit_optimized',['/usr/bin/python3','-O',str(D/'audit_native.py')]),('guards',['/usr/bin/python3',str(D/'recheck_guards.py')])]
rows=[]
for name,cmd in cmds:
 r=subprocess.run(cmd,capture_output=True,text=True,env=env);(D/(name+'.stdout')).write_text(r.stdout);(D/(name+'.stderr')).write_text(r.stderr);rows.append(dict(name=name,command=cmd,exit=r.returncode));print(name,r.returncode,flush=True)
(D/'exit_statuses.json').write_text(json.dumps(rows,indent=2))
