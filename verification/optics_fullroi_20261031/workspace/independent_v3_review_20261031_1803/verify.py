from pathlib import Path
import json,hashlib,subprocess
O=Path(__file__).resolve().parent;W=O.parent;A=W/'optics_v3_comparison_20261031_1759';R=W/'publication_20261031/target_repo';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((A/'MANIFEST.json').read_text());fs=m['files'];report={'manifest_sha256':h(A/'MANIFEST.json'),'manifest_entries':len(fs),'manifest_bad':[p for p,v in fs.items() if h(A/p)!=v]}
s=json.loads((O/'replay/summary.json').read_text());bad=[]
for p,v in s['source_sha256'].items():
 rel=(W/p).relative_to(R);b=subprocess.check_output(['git','-C',str(R),'show','f92911bc:'+str(rel)])
 if hashlib.sha256(b).hexdigest()!=v:bad.append(p)
report['historical_source_mismatch']=bad
for sub in ['replay','legacy408']:
 if not (O/sub/'summary.json').exists():continue
 x=json.loads((O/sub/'results.json').read_text());y=json.loads((A/sub/'results.json').read_text());report[sub+'_lengths']=[len(x),len(y)];report[sub+'_semantic_mismatches']=[i for i,(a,b) in enumerate(zip(x,y)) if {k:v for k,v in a.items() if k not in ['host_decode_seconds','seconds']}!={k:v for k,v in b.items() if k not in ['host_decode_seconds','seconds']}]
(O/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
