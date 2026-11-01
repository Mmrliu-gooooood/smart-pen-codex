from pathlib import Path
import json,hashlib,collections,sys,math,random
O=Path(__file__).resolve().parent;A=O.parent/'optics_paper_screen_20261031_1752';sys.path.insert(0,str(O));from model import project,jacobian
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={};counts=collections.Counter(); mismatch=[];images=[]
for filename in ['results.json','controls_results.json']:
 actual=json.loads((O/filename).read_text());old=json.loads((A/'decoder_probe'/filename).read_text())
 for a,b in zip(actual,old):
  counts[a['classification']]+=1
  if {k:v for k,v in a.items() if k!='host_decode_seconds'}!={k:v for k,v in b.items() if k!='host_decode_seconds'}:mismatch.append(a['pgm'])
  if h(O/a['pgm'])!=h(A/'decoder_probe'/a['pgm']):images.append(a['pgm'])
 r[filename+'_lengths']=[len(actual),len(old)]
r.update(counts=dict(counts),semantic_case_mismatches=mismatch,image_mismatches=images)
# independent central-difference derivative oracle across the actual parameter range
rng=random.Random(983);worst=0
for i in range(1000):
 D=rng.choice([5,10,20,40]); f=rng.choice([250,500,1000]);t=rng.choice([0,15,30,45,60]);x=rng.uniform(-1,1);y=rng.uniform(-1,1);e=1e-5
 J=jacobian(x,y,D,f,t)
 up,vp=project(x+e,y,D,f,t);um,vm=project(x-e,y,D,f,t);uq,vq=project(x,y+e,D,f,t);ur,vr=project(x,y-e,D,f,t)
 num=[(up-um)/(2*e),(uq-ur)/(2*e),(vp-vm)/(2*e),(vq-vr)/(2*e)]
 worst=max(worst,max(abs(a-b)/max(1,abs(a)) for a,b in zip(J,num)))
r['central_difference_1000_max_scaled_error']=worst
m=json.loads((A/'MANIFEST.json').read_text());r['author_manifest_still_unchanged']=all(h(A/p)==v for p,v in m['files'].items())
(O/'final_results.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
