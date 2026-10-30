from pathlib import Path
import os,json,hashlib,math,heapq
os.environ['XDG_CONFIG_HOME']='/tmp/pen-mcusupply2338'
import pcbnew as p
D=Path(__file__).resolve().parent; R=D.parents[2]
inputs={'board':R/'hardware/gnd_conservative_recovery_2305/native/mainboard_revD.kicad_pcb','old':R/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb','plan':R/'docs/electronics/aon_branch_reuse_plan_2318/evaluation.json','stack':R/'hardware/explicit_stackup_metadata_candidate/stackup_contract.json'}
def require(x,msg):
 if not x:raise RuntimeError(msg)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest(); before={k:sha(v) for k,v in inputs.items()}
b=p.LoadBoard(str(inputs['board'])); old=p.LoadBoard(str(inputs['old'])); groups=json.loads(inputs['plan'].read_text())['geometrically_screened_groups']; stack=json.loads(inputs['stack'].read_text())
import re
text=inputs['board'].read_text()
for lname,th in zip(['F.Cu','In1.Cu','In2.Cu','In3.Cu','In4.Cu','B.Cu'],stack['copper_mm']):
 match=re.search(r'\(layer \"'+re.escape(lname)+r'\"\s+\(type \"copper\"\)\s+\(thickness ([0-9.]+)\)',text)
 require(match is not None and float(match.group(1))==th,'native stack mismatch '+lname)
uid=lambda t:t.m_Uuid.AsString(); oldt={uid(t):t for t in old.GetTracks()}; pads={f.GetReference()+'.'+q.GetNumber():q for f in b.GetFootprints() for q in f.Pads() if q.GetNumber()!='57'}
# Coordinates/geometry come from byte-bound original objects; no board is saved.
for g in groups:
 for x in g['geometry']:
  t=oldt[x['uuid']]; require(t.GetNetname()=='3V3_AON','net mismatch'); require(abs((t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth())/1e6-x['width_mm'])<1e-9,'width mismatch')
  require((t.GetStart().x/1e6,t.GetStart().y/1e6)==tuple(x['start']),'start mismatch')
  require((t.GetEnd().x/1e6,t.GetEnd().y/1e6)==tuple(x['end']),'end mismatch')
paths=[]; summaries=[]
for g in groups:
 geom=g['geometry']; graph={}; vias=[]
 for x in geom:
  a=tuple(x['start']); z=tuple(x['end'])
  if x['type']=='via':vias.append(a);continue
  length=math.dist(a,z); graph.setdefault(a,[]).append((z,length,x));graph.setdefault(z,[]).append((a,length,x))
 summaries.append({'group':g['id'],'pads':g['pads'],'total_track_length_mm':sum(math.dist(x['start'],x['end'])for x in geom if x['type']=='track'),'via_count':len(vias),'layers':sorted(set(l for x in geom if x['type']=='track' for l in x['actual_layers']))})
 for name in g['pads']:
  q=pads[name]; start=(q.GetPosition().x/1e6,q.GetPosition().y/1e6);queue=[(0,start,[])];seen=set();answer=None
  while queue:
   dist,at,edges=heapq.heappop(queue)
   if at in seen:continue
   seen.add(at)
   if at in vias:answer=(dist,at,edges);break
   for nxt,dl,x in graph.get(at,[]):
    if nxt not in seen:heapq.heappush(queue,(dist+dl,nxt,edges+[x]))
  require(answer is not None,'missing path '+name)
  length,via,edges=answer
  # Copper physical constants are explicit engineering assumptions, not factory minima.
  rho=1.724e-5 # ohm mm at20C, assumed annealed copper
  r20=sum(rho*math.dist(x['start'],x['end'])/(x['width_mm']*stack['copper_mm'][0])for x in edges)
  r65=r20*(1+.00393*45)
  stress=sum(rho*math.dist(x['start'],x['end'])/((x['width_mm']-.03)*.025)for x in edges)*(1+.00393*45)
  paths.append({'pad':name,'group':g['id'],'actual_pad_layers':[b.GetLayerName(l)for l in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]if q.IsOnLayer(l)],'pad_center_mm':start,'nearest_plane_via_center_mm':via,'centerline_length_mm':length,'track_uuids':[x['uuid']for x in edges],'widths_mm':[x['width_mm']for x in edges],'track_R20_milliohm':r20*1000,'track_R65_milliohm':r65*1000,'stress_R65_milliohm_25um_widthminus30um':stress*1000,'drop65_mV_at_0p1A':r65*1000*.1,'drop65_mV_at_0p5A':r65*1000*.5})
# Screen a proposed .254 width in memory, not a selected route. Same .15 clearance.
L=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]; selected={x['uuid'] for g in groups for x in g['geometry']}; proposed=[oldt[u]for u in selected]; targets=[oldt[x['uuid']]for g in groups if g['id']in[0,5,6]for x in g['geometry']if x['type']=='track']; others=list(b.GetTracks())+[q for f in b.GetFootprints()for q in f.Pads()]+proposed
conflicts=[]
for t in targets:
 prior=t.GetWidth();t.SetWidth(254000)
 for o in others:
  if uid(o)==uid(t)or o.GetNetname()==t.GetNetname():continue
  for l in L:
   if not t.IsOnLayer(l)or not o.IsOnLayer(l):continue
   a=p.SHAPE_POLY_SET();z=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(a,l,150000,100,p.ERROR_OUTSIDE);o.TransformShapeToPolygon(z,l,0,100,p.ERROR_OUTSIDE)
   if not a.BBox().Intersects(z.BBox()):continue
   v=p.SHAPE_POLY_SET();v.BooleanIntersection(a,z)
   if v.Area()>1:conflicts.append({'track':uid(t),'other':uid(o),'other_net':o.GetNetname(),'layer':b.GetLayerName(l),'expanded_overlap_mm2':v.Area()/1e12})
 t.SetWidth(prior)
# Parameterized via term; plating remains unknown; use only sensitivity estimates.
f_to_in2=stack['copper_mm'][0]/2+stack['dielectric_mm'][0]+stack['copper_mm'][1]+stack['dielectric_mm'][1]+stack['copper_mm'][2]/2
via_sensitivity=[{'assumed_plating_um':tp,'active_length_mm':f_to_in2,'R20_milliohm':1.724e-5*f_to_in2/(math.pi*.3*(tp/1000))*1000}for tp in[15,20,25]]
require(before=={k:sha(v)for k,v in inputs.items()},'input file changed')
print(json.dumps({'status':'READ_ONLY_NOFAB_NO_POWER_APPROVAL','inputs':{k:{'path':str(v.relative_to(R)),'sha256':before[k]}for k,v in inputs.items()},'stack':stack,'paths':paths,'group_summaries':summaries,'width254_limited_screen':{'target_track_count':len(targets),'conflicts':conflicts,'not_done':['native saved candidate/full DRC','same-net topology/plane refill','temperature or transient tests','full return/core qualification']},'via_sensitivity':via_sensitivity,'current_ground_status':'All nine U101 physical ground pads not connected to J106 core in bound research state; see role_and_return_limits.json','limits':['centerline pad-to-via trace-only resistance; excludes pad spreading/via/plane/source/return/package','nominal35um outerCu,15.2um innerCu; actual stack tolerances unapproved','stress25um and width-minus30um are hypothetical sensitivity not certified minima','0.1A/0.5A are example branch currents, not known pin load','same-net components and decoupling internal to package need power-integrity validation']},indent=2))
