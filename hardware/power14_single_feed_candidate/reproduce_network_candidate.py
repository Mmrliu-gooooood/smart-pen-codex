"""Independent read-only lumped DC resistor reconstruction, not field/ampacity signoff."""
from pathlib import Path
import json, hashlib, math
import numpy as np
import pcbnew as k
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
PCB=ROOT/'hardware/power14_single_feed_candidate/power_integrated_study.kicad_pcb'
CORE=ROOT/'hardware/power_core_layout_candidate/power_core_NOFAB.kicad_pcb'
b=k.LoadBoard(str(PCB));c=k.LoadBoard(str(CORE))
if not PCB.is_file():raise RuntimeError('Missing candidate')
if hashlib.sha256(CORE.read_bytes()).hexdigest()!='7a7013b4371401595b2ffcc8569bbe2b2bf0ce828f567d530ec3ab6a0b755b1f':raise RuntimeError('Wrong core baseline')
old={t.m_Uuid.AsString() for t in c.GetTracks()}
tracks=[t for t in b.GetTracks() if t.GetNetname()=='VBUS_5V' and not isinstance(t,k.PCB_VIA)]
vias=[t for t in b.GetTracks() if t.GetNetname()=='VBUS_5V' and isinstance(t,k.PCB_VIA)]
pads={f.GetReference()+'.'+p.GetNumber():p for f in b.GetFootprints() for p in f.Pads() if p.GetNetname()=='VBUS_5V'}
if any(z.GetNetname()=='VBUS_5V' for z in b.Zones()):raise RuntimeError('Plane model not supported')
points=set()
for t in tracks:
 for q in [t.GetStart(),t.GetEnd()]:points.add((t.GetLayer(),q.x,q.y))
for v in vias:
 for l in [k.F_Cu,k.In1_Cu,k.In2_Cu,k.B_Cu]:points.add((l,v.GetPosition().x,v.GetPosition().y))
for p in pads.values():
 for l in [k.F_Cu,k.In1_Cu,k.In2_Cu,k.B_Cu]:
  if p.IsOnLayer(l):points.add((l,p.GetPosition().x,p.GetPosition().y))
points=sorted(points);parent={p:p for p in points}
def root(p):
 while p!=parent[p]:parent[p]=parent[parent[p]];p=parent[p]
 return p
def union(ps):
 ps=list(ps)
 if not ps:return
 for p in ps[1:]:parent[root(p)]=root(ps[0])
for p in pads.values():union(q for q in points if p.IsOnLayer(q[0]) and p.HitTest(k.VECTOR2I(q[1],q[2])))
for v in vias:union(q for q in points if q[1:]==(v.GetPosition().x,v.GetPosition().y))
segments=[]
for t in tracks:
 a=t.GetStart();z=t.GetEnd();dx=z.x-a.x;dy=z.y-a.y;ll=dx*dx+dy*dy
 if ll==0:continue
 selected=[]
 for q in points:
  if q[0]!=t.GetLayer():continue
  u=((q[1]-a.x)*dx+(q[2]-a.y)*dy)/ll
  if u < -2/math.sqrt(ll) or u>1+2/math.sqrt(ll):continue
  u=max(0,min(1,u))
  if math.hypot(q[1]-a.x-u*dx,q[2]-a.y-u*dy)<=2:selected.append((u,q))
 selected.sort()
 for (s,p),(e,q) in zip(selected,selected[1:]):
  if (e-s)*math.sqrt(ll)<1e-6:union([p,q]);continue
  segments.append(dict(a=p,b=q,length_mm=(e-s)*math.sqrt(ll)/1e6,width_mm=k.ToMM(t.GetWidth()),layer=b.GetLayerName(t.GetLayer()),uuid=t.m_Uuid.AsString(),added=t.m_Uuid.AsString() not in old))
nodes=sorted({root(p) for p in points});idx={n:i for i,n in enumerate(nodes)}
def padnode(label):
 p=pads[label];q=next(q for q in points if q[1:]==(p.GetPosition().x,p.GetPosition().y) and p.IsOnLayer(q[0]));return idx[root(q)]
rho=1.724e-8*(1+.00393*65)
mat=np.zeros((len(nodes),len(nodes)));edges=[]
for s in segments:
 i=idx[root(s['a'])];j=idx[root(s['b'])]
 if i==j:continue
 r=rho*s['length_mm']/(s['width_mm']*(18 if s['layer'].startswith('In') else 31.5)*1e-6)
 mat[i,i]+=1/r;mat[j,j]+=1/r;mat[i,j]-=1/r;mat[j,i]-=1/r
 edges.append((i,j,r,s))
source=padnode('J2.1');keep=[i for i in range(len(nodes)) if i!=source]
result={'pcb_sha256':hashlib.sha256(PCB.read_bytes()).hexdigest(),'assumptions':'85C; outer31.5um inner18um copper; ideal zero-ohm pads/vias; centerline splitting within2nm; no source/return/pad spreading R, L, heating, or device models. Independent implementation; lumped geometric approximation only.','tracks':len(tracks),'vias':len(vias),'nodes_after_ideal_junction_collapse':len(nodes),'scenarios':[]}
for label,current in [('U1.13',1),('U102.4',.025)]:
 sink=padnode(label);rhs=np.zeros(len(nodes));rhs[sink]=-current;volts=np.zeros(len(nodes));volts[keep]=np.linalg.solve(mat[np.ix_(keep,keep)],rhs[keep]);flows=[]
 for i,j,r,s in edges:
  flows.append({**{f:s[f] for f in ['uuid','length_mm','width_mm','layer','added']},'current_A':abs((volts[i]-volts[j])/r)})
 flows.sort(key=lambda x:x['current_A'],reverse=True)
 residual=mat@volts-rhs;non_src=max(abs(residual[i]) for i in keep)
 if non_src>1e-9:raise RuntimeError('KCL residual')
 loss=sum((volts[i]-volts[j])**2/r for i,j,r,s in edges)
 if abs(loss-current*(-volts[sink]))>1e-10:raise RuntimeError('Power conservation')
 result['scenarios'].append({'sink':label,'current_A':current,'drop_mV':-1000*volts[sink],'max_added_current_A':max(x['current_A'] for x in flows if x['added']),'max_KCL_residual_A':non_src,'total_trace_loss_W':loss,'added_top': [x for x in flows if x['added']][:8]})
(OUT/'network_result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
