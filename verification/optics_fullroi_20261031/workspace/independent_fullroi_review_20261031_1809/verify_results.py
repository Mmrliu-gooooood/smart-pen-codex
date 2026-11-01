from pathlib import Path
import json,hashlib,collections
O=Path(__file__).resolve().parent;W=O.parent;A=W/'orthogonal_refine_fullroi_candidate_20261031_1806';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();report={}
report['candidate_copy_matches']={p:h(O/p)==h(A/p) for p in ['candidate.c','candidate.h','build.py','regression/run.py','native_guards.c','run_native.py','test_candidate.py']}
if (A/'MANIFEST.json').exists():
 m=json.loads((A/'MANIFEST.json').read_text());report['author_manifest_sha256']=h(A/'MANIFEST.json');report['author_manifest_entries']=len(m['files']);report['author_manifest_bad']=[p for p,v in m['files'].items() if h(A/p)!=v]
sets={}
for gate in ['off','on']:
 p=O/f'regression/{gate}_results.json'
 if not p.exists():continue
 rows=json.loads(p.read_text());old=json.loads((A/f'regression/{gate}_results.json').read_text());sets[gate]=rows
 report[gate]={'cases':len(rows),'counts':dict(collections.Counter(r['classification'] for r in rows)),'semantic_mismatches':[i for i,(a,b) in enumerate(zip(rows,old)) if {k:v for k,v in a.items() if k!='host_seconds'}!={k:v for k,v in b.items() if k!='host_seconds'}],'explicit_must_reject':sum(r['must_reject'] for r in rows),'explicit_must_reject_accepts':sum(r['must_reject'] and r['status']==0 for r in rows),'historical_reject_accepts':sum(r['dataset']!='probe' and r['archived_v3_status']!=0 and r['status']==0 for r in rows)}
 if gate=='on':
  target=['control_000.pgm','control_001.pgm','control_006.pgm','control_007.pgm','control_012.pgm','control_013.pgm','049.pgm','050.pgm'];boundary=['000.pgm','015.pgm','030.pgm'];report['target8_all_correct']=all(r['classification']=='correct_accept' for r in rows if r['dataset']=='probe' and r['key'] in target);report['boundary3_all_reject']=all(r['classification']=='reject' for r in rows if r['dataset']=='probe' and r['key'] in boundary)
if len(sets)==2:
 report['transitions']=dict(collections.Counter(a['classification']+' -> '+b['classification'] for a,b in zip(sets['off'],sets['on'])))
(O/'verification/results_check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
