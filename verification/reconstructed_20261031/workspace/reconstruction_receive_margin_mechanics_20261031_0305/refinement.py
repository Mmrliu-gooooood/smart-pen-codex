from pathlib import Path
import os,json,hashlib
os.makedirs('/tmp/recv0305',exist_ok=True);os.environ['XDG_CONFIG_HOME']='/tmp/recv0305';import pcbnew as p
O=Path(__file__).resolve().parent;W=O.parent;old=W/'reconstruction_receive_pair_mechanics_20261031_0302/selected_native.kicad_pcb';new=O/'selected_native.kicad_pcb';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def need(v,m):
 if not v:raise RuntimeError(m)
need(sha(old)=='a7713a113d76041201bf9cd3a9e76d6b32b8f026ad2cd383f5a37de70821749e','old exact');need(sha(new)=='d8550195b14521806a14654c4bdeba0a6d533b0aa536b473919481da2b9d6e5b','new exact')
a=p.LoadBoard(str(old));b=p.LoadBoard(str(new))
def spec(t):return {'kind':t.GetClass(),'net':t.GetNetname(),'layer':t.GetLayerName(),'width':t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),'a':[t.GetStart().x,t.GetStart().y],'b':[t.GetEnd().x,t.GetEnd().y],'drill':t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None}
x={t.m_Uuid.AsString():spec(t)for t in a.GetTracks()};y={t.m_Uuid.AsString():spec(t)for t in b.GetTracks()};need(set(x)==set(y),'no added removed UUIDs');changed={u:{'old':x[u],'new':y[u]}for u in x if x[u]!=y[u]};need(len(changed)==6,'only six changed')
for u,row in changed.items():
 before,after=row['old'],row['new'];need(all(before[k]==after[k]for k in ['kind','net','layer','width','drill']),'identity unchanged');need(before['net']in['CAM_PCLK','CAM_HREF'],'receive only')
 for endpoint in ['a','b']:
  if before[endpoint]!=after[endpoint]:need(before[endpoint][0]==after[endpoint][0]and before[endpoint][1]==14250000 and after[endpoint][1]==14300000,'only exact 50um upward coordinate change')
(O/'refinement_results.json').write_text(json.dumps({'old_sha256':sha(old),'new_sha256':sha(new),'exact_six_changed':changed,'scope':'source via and two incident endpoints per net; not copper-union equivalence'},indent=2)+'\n')
