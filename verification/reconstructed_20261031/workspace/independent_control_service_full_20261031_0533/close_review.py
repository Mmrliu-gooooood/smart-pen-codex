from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;W=D.parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def req(v,n):
 if not v:raise RuntimeError(n)
closures=[]
for root,name,expected,count in [('reconstruction_control_service_20261031_0510','review_manifest.json','bec167d27945b9d4af03171fd7f0c457315ffc82333d178ececc6063f2f86614',192),('independent_control_service_advisory_20261031_0521','manifest.json','ac111af161fa07cd7665c71f2321206209f869f5530afeff69005942ba6e871c',60),('reconstruction_control_service_final_mechanics_20261031_0524','manifest.json','767f9b90fac6214d1dc45ed15f817281f616d27770f4468c8e42025ee05ceb58',28)]:
 p=W/root;req(sha(p/name)==expected,root+' manifest');m=json.loads((p/name).read_text());fs=m['files'];fs=[dict(v,path=k)if isinstance(v,dict)else{'path':k,'sha256':v}for k,v in fs.items()]if isinstance(fs,dict)else fs;req(len(fs)==count,root+' count')
 for f in fs:req(sha(p/f['path'])==f['sha256'],root+'/'+f['path'])
 closures.append({'root':root,'manifest':name,'sha256':expected,'files_verified':count})
cutrows=[]
for mode in ['normal','optimized']:
 for i in range(4):
  p=D/'independent_native_cuts'/mode/str(i);r=json.loads((p/'result.json').read_text());req(r['DRC']==([0,38,0]if i==3 else[1,38,0]),'owncutDRC');req(r['all_unrelated_partitions_unchanged'],'partitions');cutrows.append(dict(r,mode=mode,index=i))
for i in range(4):req({k:v for k,v in cutrows[i].items()if k!='mode'}=={k:v for k,v in cutrows[i+4].items()if k!='mode'},'owncut modes')
req(all(r['all53_manifest_native_files_exact']for r in json.loads((D/'independent_replay.json').read_text())),'replay53')
cf=[]
for mode in ['NONE','EDGE_VIA','IOEN_SOURCE','IN2']:
 a=json.loads((W/'independent_control_service_advisory_20261031_0521'/f'causal_{mode}.json').read_text());b=json.loads((D/'causal_recheck'/f'causal_{mode}.json').read_text());req(a==b,'causal equality '+mode);cf.append(mode)
for f in ['feed_paths.json','bridge.json','plane_islands_final.json','pdn_advisory.json']:
 req(json.loads((W/'independent_control_service_advisory_20261031_0521'/f).read_text())==json.loads((D/'causal_recheck'/f).read_text()),'PDN equality '+f)
req(json.loads((D/'independent_paths.json').read_text())==json.loads((W/'independent_control_service_advisory_20261031_0521/clock_centerline.json').read_text()),'independent branch articulation')
agg=json.loads((D/'aggregate_checks.json').read_text());req(agg['count']==42 and all(agg['checks'].values()),'aggregate')
(D/'REVIEW.json').write_text(json.dumps({'verdict':'ACCEPT_SCOPED_STATIC_FOUR_CONTROL_SERVICE_JOINS','candidate_sha256':sha(D/'final_candidate/mainboard_revD.kicad_pcb'),'closures':closures,'own_actual_saved_cuts':cutrows,'matched_refill_counterfactuals_equal':cf,'source_roles_fresh_export_verified':True,'native_replay_file_count':53,'boundary':'No validated sensor PWDN; no operating UART/control, SI/PDN/power/fab/process acceptance. All advisory/source/mechanical exceptions retained.'},indent=2));print('CLOSED_SCOPED_STATIC')
