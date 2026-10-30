from pathlib import Path
import sys,json,shutil
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'gate_input_local_routing'));import pcb_preflight as pf
lock=json.loads((D.parent/'gate_input_local_routing/preflight_lock.json').read_text());out=[]
for case in ['missing_project','missing_rules','changed_netclass','wrong_centre_dielectric','missing_stackup']:
 F=D/'config_guards'/case;F.mkdir(parents=True,exist_ok=True)
 for ext in ['kicad_pcb','kicad_pro','kicad_dru','kicad_sch']:shutil.copyfile(D/'native_snapshot'/('mainboard_revD.'+ext),F/('mainboard_revD.'+ext))
 if case=='missing_project':(F/'mainboard_revD.kicad_pro').unlink()
 elif case=='missing_rules':(F/'mainboard_revD.kicad_dru').unlink()
 elif case=='changed_netclass':
  f=F/'mainboard_revD.kicad_pro';x=json.loads(f.read_text());x['net_settings']['classes'][0]['clearance']=.01;f.write_text(json.dumps(x))
 else:
  f=F/'mainboard_revD.kicad_pcb';s=f.read_text();stack=pf.block(s,'stackup',2)
  if case=='missing_stackup':s=s.replace(stack,'')
  else:
   if '0.2028' not in stack:raise RuntimeError('fixture missing centre')
   s=s.replace(stack,stack.replace('0.2028','0.2104'))
  f.write_text(s)
 try:pf.verify(F/'mainboard_revD.kicad_pcb',lock)
 except ValueError as e:out.append({'case':case,'rejected':str(e)})
 else:raise RuntimeError('config accepted '+case)
print(json.dumps(out,indent=2))
