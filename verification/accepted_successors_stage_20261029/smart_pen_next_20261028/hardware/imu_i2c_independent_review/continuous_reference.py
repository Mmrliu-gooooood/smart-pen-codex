from pathlib import Path
from collections import defaultdict
import os,json,math
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache';os.environ['XDG_DATA_HOME']='/tmp/rf-independent/data'
import pcbnew as p
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));xy=lambda v:(v.x/1e6,v.y/1e6);planes={}
for l in[p.In1_Cu,p.In4_Cu]:
 q=p.SHAPE_POLY_SET()
 for z in b.Zones():
  if not z.GetIsRuleArea()and z.GetNetname()=='GND'and z.IsOnLayer(l):q.BooleanAdd(z.GetFilledPolysList(l))
 planes[l]=q
out=[]
for net in ['AON_I2C_SCL','AON_I2C_SDA']:
 for l in[p.F_Cu,p.In3_Cu,p.B_Cu]:
  ts=[t for t in b.GetTracks()if not isinstance(t,p.PCB_VIA)and t.GetNetname()==net and t.GetLayer()==l];nodes={xy(t.GetStart())for t in ts}|{xy(t.GetEnd())for t in ts};edges={};adj=defaultdict(list)
  # Split centerlines at exact interior T coordinates; no endpoint-degree claim about copper widths.
  for t in ts:
   a,z=xy(t.GetStart()),xy(t.GetEnd());dx,dy=z[0]-a[0],z[1]-a[1];den=dx*dx+dy*dy;pts=[(0,a),(1,z)]
   for v in nodes:
    u=((v[0]-a[0])*dx+(v[1]-a[1])*dy)/den
    if 1e-8<u<1-1e-8 and math.hypot(v[0]-a[0]-u*dx,v[1]-a[1]-u*dy)<1e-7:pts.append((u,v))
   pts=sorted(set(pts))
   for i,((_,aa),(_,zz))in enumerate(zip(pts,pts[1:])):
    key=t.m_Uuid.AsString()+':'+str(i);edges[key]=(aa,zz);adj[aa].append(key);adj[zz].append(key)
  stop={v for v,e in adj.items()if len(e)!=2};vias=[xy(t.GetPosition())for t in b.GetTracks()if isinstance(t,p.PCB_VIA)and t.GetNetname()==net]
  stop|={v for v in adj if any(math.dist(v,q)<.001 for q in vias)};remaining=set(edges)
  while remaining:
   key=next((u for u in sorted(remaining)if any(v in stop for v in edges[u])),min(remaining));a,z=edges[key];start=a if a in stop else z;cur=start;chain=[]
   while key in remaining:
    remaining.remove(key);a,z=edges[key];end=z if cur==a else a;chain.append((cur,end));cur=end
    if cur in stop:break
    rr=[u for u in adj[cur]if u in remaining]
    if len(rr)!=1:break
    key=rr[0]
   ref=p.In1_Cu if l==p.F_Cu else p.In4_Cu;plane=planes[ref];runs=[];gap=0;arc=0;gs=None
   for a,z in chain:
    length=math.dist(a,z);n=max(1,math.ceil(length/.005));step=length/n
    for i in range(n):
     u=(i+.5)/n;v=p.VECTOR2I(round((a[0]+u*(z[0]-a[0]))*1e6),round((a[1]+u*(z[1]-a[1]))*1e6))
     if not plane.Contains(v):
      if gs is None:gs=arc
      gap+=step
     elif gs is not None:runs.append({'start':gs,'end':arc,'gap_mm':gap});gs=None;gap=0
     arc+=step
   if gs is not None:runs.append({'start':gs,'end':arc,'gap_mm':gap})
   out.append({'net':net,'layer':b.GetLayerName(l),'ref':b.GetLayerName(ref),'chain_segments':len(chain),'start':chain[0][0],'end':chain[-1][1],'length_mm':arc,'gaps':runs,'max_gap_mm':max((g['gap_mm']for g in runs),default=0)})
r={'status':'CONTINUOUS_CENTERLINE_REFERENCE_SCREEN_NOT_RETURN_CURRENT_SIMULATION','max_sample_step_mm':.005,'boundary_uncertainty_mm':.010,'layer_changes_and_branches_split':True,'max_chain_gap_mm':max(q['max_gap_mm']for q in out),'chains':out};(D/'continuous_reference.json').write_text(json.dumps(r,indent=2));print(json.dumps({'max_chain_gap_mm':r['max_chain_gap_mm'],'chains':len(out)},indent=2))
