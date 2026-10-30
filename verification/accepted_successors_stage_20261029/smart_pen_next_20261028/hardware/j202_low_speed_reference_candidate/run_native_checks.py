from pathlib import Path
import subprocess,json,os
D=Path(__file__).resolve().parent;env=dict(os.environ,XDG_CONFIG_HOME='/tmp/rf-independent/config',XDG_CACHE_HOME='/tmp/rf-independent/cache',XDG_DATA_HOME='/tmp/rf-independent/data');sch=D/'native/mainboard_revD.kicad_sch';pcb=D/'native/mainboard_revD.kicad_pcb';runs=[]
commands=[('netlist',['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(D/'fresh.xml'),str(sch)],0),('erc',['kicad-cli','sch','erc','--severity-all','--exit-code-violations','--format','json','-o',str(D/'fresh_erc.json'),str(sch)],5),('preflight_full_drc',['/usr/bin/python3',str(D/'pcb_preflight.py'),str(pcb),'--lock',str(D/'preflight_lock.json'),'--report',str(D/'preflight.json'),'--run-drc'],5)]
for name,cmd,expected in commands:
 r=subprocess.run(cmd,env=env,capture_output=True,text=True);(D/(name+'_native.log')).write_text(r.stdout+r.stderr);runs.append({'name':name,'command':cmd,'exit':r.returncode,'expected_exit':expected})
 if r.returncode!=expected:raise RuntimeError('NATIVE_EXIT_MISMATCH '+name)
x=json.loads((D/'preflight.native_drc.json').read_text());counts=[len(x[k])for k in['violations','unconnected_items','schematic_parity']]
if counts!=[17,21,0]:raise RuntimeError('FULL_DRC_COUNT_CHANGED')
e=json.loads((D/'fresh_erc.json').read_text());vv=[v for s in e['sheets']for v in s['violations']]
if len(vv)!=1 or vv[0]['severity']!='warning' or vv[0]['type']!='global_label_dangling':raise RuntimeError('ERC_CHANGED')
(D/'native_command_results.json').write_text(json.dumps({'status':'EXPECTED_REMAINING_VIOLATIONS_NOFAB','runs':runs,'full_drc_counts':counts,'ERC_errors':0,'ERC_warnings':1},indent=2));print(json.dumps(runs,indent=2))
