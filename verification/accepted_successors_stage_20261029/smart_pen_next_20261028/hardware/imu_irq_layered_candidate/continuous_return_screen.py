from pathlib import Path
import os,json,math
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache'
import pcbnew as p
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));rr=json.loads((D/'irq_simplified_routes.json').read_text());chains=[];cur=[]
for r in rr:
 if r['type']!='track':continue
 if cur and(cur[-1]['layer']!=r['layer']or math.dist(cur[-1]['z'],r['a'])>1e-6):chains.append(cur);cur=[]
 cur.append(r)
if cur:chains.append(cur)
source=[t for t in b.GetTracks()if t.GetNetname()=='PICKUP_INT_N'and not isinstance(t,p.PCB_VIA)and t.GetLayer()==p.F_Cu and t.GetStart().y<20e6];source.sort(key=lambda t:-t.GetStart().x);xy=lambda v:[v.x/1e6,v.y/1e6];chains.insert(0,[{'a':xy(t.GetStart()),'z':xy(t.GetEnd()),'layer':'F.Cu','uuid':t.m_Uuid.AsString()}for t in source]);planes={}
for layer in[p.In1_Cu,p.In4_Cu]:
 q=p.SHAPE_POLY_SET()
 for z in b.Zones():
  if not z.GetIsRuleArea()and z.GetNetname()=='GND'and z.IsOnLayer(layer):q.BooleanAdd(z.GetFilledPolysList(layer))
 planes[layer]=q
out=[]
for i,chain in enumerate(chains):
 ref=p.In1_Cu if chain[0]['layer']=='F.Cu'else p.In4_Cu;q=planes[ref];runs=[];gap=0;arclen=0;start=None
 for r in chain:
  a,z=r['a'],r['z'];length=math.dist(a,z);n=max(1,math.ceil(length/.005));step=length/n
  for j in range(n):
   u=(j+.5)/n;v=p.VECTOR2I(round((a[0]+u*(z[0]-a[0]))*1e6),round((a[1]+u*(z[1]-a[1]))*1e6));inside=q.Contains(v)
   if not inside:
    if start is None:start=arclen
    gap+=step
   elif start is not None:runs.append({'start_arc_mm':start,'end_arc_mm':arclen,'length_mm':gap});gap=0;start=None
   arclen+=step
 if start is not None:runs.append({'start_arc_mm':start,'end_arc_mm':arclen,'length_mm':gap})
 out.append({'chain':i,'layer':chain[0]['layer'],'reference':b.GetLayerName(ref),'tracks':len(chain),'length_mm':arclen,'a':chain[0]['a'],'z':chain[-1]['z'],'uncovered_centerline_runs':runs,'max_gap_mm':max((r['length_mm']for r in runs),default=0)})
r={'status':'CHAIN_CENTERLINE_PROJECTION_SCREEN_NOT_RETURN_CURRENT_SIMULATION','sampling_max_step_mm':.005,'gap_boundary_sampling_uncertainty_mm':.010,'changed_layer_chains_not_merged':True,'max_same_layer_chain_gap_mm':max(x['max_gap_mm']for x in out),'chains':out};(D/'continuous_return_screen.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
