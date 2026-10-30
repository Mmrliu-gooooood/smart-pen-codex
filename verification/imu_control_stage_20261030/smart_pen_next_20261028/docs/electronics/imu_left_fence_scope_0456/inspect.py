from pathlib import Path
import sys,json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2];sys.path.insert(0,str(R/'docs/electronics/imu_control_joint_plan_0444'));import geometry as g
p=g.p;rows=[];pads=[]
for t in g.old:
 a=[t.GetStart().x/1e6,t.GetStart().y/1e6];z=[t.GetEnd().x/1e6,t.GetEnd().y/1e6]
 if max(a[1],z[1])<78 or min(a[1],z[1])>87 or min(a[0],z[0])>7:continue
 rows.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'type':'via'if isinstance(t,p.PCB_VIA)else'track','layer':'through'if isinstance(t,p.PCB_VIA)else g.b.GetLayerName(t.GetLayer()),'a':a,'b':z,'width':(t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth())/1e6})
for f in g.b.GetFootprints():
 if f.GetReference()not in['U501','C501','C502','C503','J107','R501','R502']:continue
 for q in f.Pads():pads.append({'ref':f.GetReference()+'.'+q.GetNumber(),'value':f.GetValue(),'net':q.GetNetname(),'xy':g.xy(q),'size':[q.GetSize().x/1e6,q.GetSize().y/1e6],'layers':[g.b.GetLayerName(l)for l in g.L if q.IsOnLayer(l)]})
print(json.dumps({'status':'NEXT_SCOPE_ONLY_NO_ROUTE_OR_NATIVE','parent_sha':hashlib.sha256(g.S.read_bytes()).hexdigest(),'pads':pads,'nearby_copper':rows,'constraints':['Do not delete the CS/SA0 tie or C503 power feed','C502.1=(5.72,82) and C503.1=(4.35,84.5) are actual AON pads; no implicit via at4.35,85.6','A left-side escape must clear both F AON vertical rails x2.65 and x1.8, plus inner SENS x3.5 and actual B J107 pads','C501/C502 GND pads and U501 NC/RES/GND source ties remain required','No relocation/reroute/full-length search executed']},indent=2))
