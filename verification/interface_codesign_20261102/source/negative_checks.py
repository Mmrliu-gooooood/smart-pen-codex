from pathlib import Path
import json,sys,re,shutil,subprocess
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D/'review_dependencies'));from native_blocks import blocks
base=(D/'candidate/mainboard_revD.kicad_pcb').read_text();c=json.loads((D/'native_contract.json').read_text());fp=next(v for _,_,v in blocks(base)if v.startswith('(footprint')and '(property "Reference" "J107"'in v)
def padmove():
 old='(at 0.8 -6.28 270)'
 if fp.count(old)!=1:raise RuntimeError('pad mutation anchor')
 return base.replace(fp,fp.replace(old,'(at 0.81 -6.28 270)'))
def padnet():return base.replace(fp,fp.replace('(net 33 "USB_EN2")','(net 30 "USB_EN1")'))
def trackmove():
 v=next(v for _,_,v in blocks(base)if v.startswith('(segment')and not any(x['uuid']in v for x in c['objects']));w=re.search(r'\(width ([0-9.]+)\)',v).group(1);return base.replace(v,v.replace('(width '+w+')','(width '+str(float(w)+.001)+')'))
def deletefeed():
 u=next(x['uuid']for x in c['objects']if x['net']=='GND');v=next(v for _,_,v in blocks(base)if u in v);return base.replace(v,'')
recipes=[('wrong_J107_pose',padmove,'J107_all_three_exact_new_poses'),('wrong_J107_net',padnet,'J107_pad_sizes_shapes_masks_nets_unchanged'),('retained_copper_changed',trackmove,'all_retained_copper_raw_exact'),('missing_new_GND_feed',deletefeed,'exact_23_removals_20_additions')];results=[]
for name,fn,key in recipes:
 T=D/'negative_work'/name
 if T.exists():raise RuntimeError('no overwrite fixture')
 shutil.copytree(D/'candidate',T);(T/'mainboard_revD.kicad_pcb').write_text(fn())
 for opt in [[],['-O']]:
  r=subprocess.run(['/usr/bin/python3',*opt,str(D/'verify_candidate.py'),str(T)],text=True,capture_output=True);text=r.stdout+r.stderr;ok=r.returncode!=0 and "'"+key+"': False"in text and 'raw contract' in text
  results.append({'case':name,'optimized':bool(opt),'expected_failed_guard':key,'exit_code':r.returncode,'explicit_guard_rejected':ok})
  if not ok:raise RuntimeError('negative did not reject expected guard: '+text[-2000:])
 shutil.rmtree(T)
(D/'negative_checks.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
