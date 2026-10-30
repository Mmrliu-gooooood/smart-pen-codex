from pathlib import Path
import sys,json,collections
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'imu_power_return_candidate_0333'))
from geometry import *
if hashlib.sha256(S.read_bytes()).hexdigest()!='6902c742f9e3995e20cffd1946a8e2c47197cdffe7b4d6357b14a2c0b3857d0c':raise RuntimeError('wrong source')
pro=json.loads(S.with_suffix('.kicad_pro').read_text())['board']['design_settings']['rules']
counts=collections.Counter((round(t.GetWidth(p.F_Cu)/1e6,4),round(t.GetDrillValue()/1e6,4))for t in old if isinstance(t,p.PCB_VIA))
locations=[('3V3_AON',(2.2,82)),('3V3_AON',(2.2,80.4)),('GND',(5.2,83.3)),('GND',(3,83.4)),('GND',(5.55,83.3)),('GND',(3.4,83.4)),('3V3_AON',(2.65,79.9)),('GND',(4.45,83.4)),('GND',(7.3,81.3)),('3V3_AON',(5.72,79.7)),('3V3_AON',(4.35,85.8)),('GND',(7.2,84.5))]
rows=[]
for n,pos in locations:
 row=dict(net=n,position=pos,variants=[])
 for diameter,drill in [(.60,.30),(.45,.20)]:
  t=via(n,pos);t.SetWidth(p.F_Cu,round(diameter*1e6));t.SetDrill(round(drill*1e6));er=errors([t]);row['variants'].append(dict(diameter=diameter,drill=drill,annulus=(diameter-drill)/2,errors=er))
 rows.append(row)
print(json.dumps(dict(source_sha256=hashlib.sha256(S.read_bytes()).hexdigest(),rules=pro,existing_vias=[dict(diameter=k[0],drill=k[1],count=v)for k,v in sorted(counts.items())],positions=rows),indent=2))
