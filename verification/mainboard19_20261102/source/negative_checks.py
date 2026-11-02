import os,json,re,subprocess,shutil,sys
from pathlib import Path
D=Path(__file__).parent;sys.path.insert(0,str(D/'review_dependencies'));from native_blocks import blocks
c=json.loads((D/'native_contract.json').read_text());src=D/'candidate';raw=(src/'mainboard_revD.kicad_pcb').read_text();parts={re.search(r'\(uuid "([^"]+)"\)',v).group(1):v for _,_,v in blocks(raw)if v.startswith(('(segment','(via'))};fp=next(v for _,_,v in blocks(raw)if v.startswith('(footprint')and '(property "Reference" "R230"'in v);tv=parts[c['objects'][0]['uuid']]
label=next(v for _,_,v in blocks(raw)if v.startswith('(footprint')and '(property "Reference" "J107"'in v)
cases={'J107_content':raw.replace(label,label.replace('1 EN1','1 WRONG')),'missing_signal_branch':raw.replace(tv,''),'branch_width':raw.replace(tv,tv.replace('(width 0.15)','(width 0.16)')),'branch_wrong_layer':raw.replace(tv,tv.replace('(layer "B.Cu")','(layer "In3.Cu")')),'R230_value':raw.replace(fp,fp.replace('100k 1%','10k 1%')),'R230_pose':raw.replace(fp,fp.replace('(at 4.25 36.2)','(at 4.35 36.2)')),'delete_retained_old_ground_via':raw.replace(parts['74ea5a95-f920-42ac-8f11-46f056a91d64'],'')};rows=[];env=os.environ.copy();env.update(XDG_CONFIG_HOME='/tmp/pcb_interface_clean_617a/config',XDG_CACHE_HOME='/tmp/pcb_interface_clean_617a/cache',XDG_DATA_HOME='/tmp/pcb_interface_clean_617a/data')
for name,txt in cases.items():
 if txt==raw:raise RuntimeError('mutation missing '+name)
 T=D/('negative_'+name)
 if T.exists():raise RuntimeError('no overwrite')
 shutil.copytree(src,T);(T/'mainboard_revD.kicad_pcb').write_text(txt);r=subprocess.run(['/usr/bin/python3','-O',str(D/'verify_candidate.py'),str(T)],capture_output=True,text=True,env=env);(D/('negative_'+name+'.log')).write_text(r.stdout+r.stderr);rows.append({'case':name,'exit':r.returncode,'explicit_guard':r.returncode!=0 and ('RuntimeError: raw contract'in r.stderr or'RuntimeError: R230 rigid transform mismatch'in r.stderr or'RuntimeError: J107 label transform mismatch'in r.stderr)})
 for f in T.rglob('*'):
  if f.is_file()and f.name!='mainboard_revD.kicad_pcb':f.unlink()
 if not rows[-1]['explicit_guard']:raise RuntimeError('negative guard failed '+name)
(D/'negative_checks.json').write_text(json.dumps(rows,indent=2));print(rows)
