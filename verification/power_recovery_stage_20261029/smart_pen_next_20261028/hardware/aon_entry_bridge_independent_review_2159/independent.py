from pathlib import Path
import os,json,hashlib,shutil,subprocess,sys
os.environ['XDG_CONFIG_HOME']='/tmp/aon-independent2159';os.environ['XDG_CACHE_HOME']='/tmp/aon-independent2159-cache'
import pcbnew as p
from finite_copper import build,components,L
D=Path(__file__).resolve().parent;R=D.parents[1]
paths=[R/'hardware/head_power_joint_native_candidate_2141/native',R/'hardware/power_zone_freshfill_candidate_2150/native',R/'hardware/aon_entry_bridge_candidate_2156/native']
H=['7e639fa62f08ba04dd5507f383e38ce1134877c5108e2527b855eb9b00b39115','d64594c0ddfcddc7b8c3a40043fe56e144f25d4c59d2fa33e30a9595054c3de5','fd989bf844a8bc224f315dd3d2559d7a55ae1ba8f9384b0c06b6e301b6668454']
def req(v,m):
 if not v:raise RuntimeError(m)
def sha(x):return hashlib.sha256(x.read_bytes()).hexdigest()
for q,h in zip(paths,H):req(sha(q/'mainboard_revD.kicad_pcb')==h,'INPUT HASH')
boards=[p.LoadBoard(str(q/'mainboard_revD.kicad_pcb'))for q in paths];uid=lambda x:x.m_Uuid.AsString()
def sig(x):return(x.GetClass(),x.GetNetname(),x.GetLayerSet().FmtHex(),x.GetStart().x,x.GetStart().y,x.GetEnd().x,x.GetEnd().y,x.GetWidth(p.F_Cu)if isinstance(x,p.PCB_VIA)else x.GetWidth(),x.GetDrillValue()if isinstance(x,p.PCB_VIA)else 0)
ts=[{uid(x):sig(x)for x in b.GetTracks()}for b in boards];req(ts[0]==ts[1]and len(ts[0])==533,'533 COPPER');added=set(ts[2])-set(ts[1]);req(added=={'4011118b-7e7a-587d-9f01-ce37302f8576'},'ONE ADD');u=next(iter(added));req({k:v for k,v in ts[2].items()if k!=u}==ts[1],'533 KEPT');t=next(x for x in boards[2].GetTracks()if uid(x)==u);req(t.GetWidth()==500000 and t.GetLayer()==p.In2_Cu and t.GetNetname()=='3V3_AON'and (t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y)==(11900000,83900000,11000000,83900000),'BRIDGE')
def fp(b):return sorted((uid(f),f.GetReference(),f.GetValue(),f.GetLayer(),f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees(),sorted((uid(q),q.GetNumber(),q.GetNetname(),q.GetPosition().x,q.GetPosition().y,q.GetLayerSet().FmtHex())for q in f.Pads()))for f in b.GetFootprints())
req(fp(boards[0])==fp(boards[1])==fp(boards[2]),'FP SOURCE')
# Fill in entirely separate projects and demand exact serialized bytes.
for index in (0,2):
 nd=D/('refill_'+str(index)+('_O'if sys.flags.optimize else ''));shutil.copytree(paths[index],nd);f=nd/'mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f))
 if index==0:
  for z in b.Zones():
   if not z.GetIsRuleArea():z.UnFill()
 p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);expect=H[1]if index==0 else H[2];req(sha(f)==expect,'REFILL HASH')
 b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);req(sha(f)==expect,'REFILL RELOAD')
# actual finite-copper reach, include physical exposed pad UUIDs and all zone fragments.
def reach(nodes,start,omit=None):
 nodes=[x for x in nodes if x[0]!=omit];lookup={x[0]:x for x in nodes};seen={start};todo=[start]
 while todo:
  x=lookup[todo.pop()]
  for name,isp,shapes in nodes:
   if name in seen:continue
   for l in x[2].keys()&shapes.keys():
    if not x[2][l].BBox().Intersects(shapes[l].BBox()):continue
    q=p.SHAPE_POLY_SET();q.BooleanIntersection(x[2][l],shapes[l])
    if q.Area()>1:seen.add(name);todo.append(name);break
 return seen
out=[];allnodes=[build(boards[i])for i in (1,2)]
for i,nets in zip((1,2),allnodes):
 states={}
 for n,core in [('3V3_AON','J106.2'),('GND','J106.3')]:
  reached=reach(nets[n],core);pads=[x[0]for x in nets[n]if x[1]];states[n]=dict(total=len(pads),core_pads=sorted(set(pads)&reached),zone_fragments=sorted(x for x in reached if '/'in x))
 req(states['3V3_AON']['total']==39 and len(states['3V3_AON']['core_pads'])==1,'AON PADS');req(states['GND']['total']==102 and len(states['GND']['core_pads'])==2,'GND PADS');req(len(states['GND']['zone_fragments'])==4,'GND REGIONS');req(len(states['3V3_AON']['zone_fragments'])==(0 if i==1 else 1),'AON REGION')
 out.append(states)
nets=allnodes[1];req(not any('/'in x for x in reach(nets['3V3_AON'],'J106.2',u)),'BRIDGE COUNTERFACTUAL');gndvia='70f2443f-1a5f-5292-8401-7d0f5fea8c0a';rg=reach(nets['GND'],'J106.3',gndvia);req('J301.2'in rg and not any('/'in x for x in rg),'GND COUNTERFACTUAL')
# Plane geometry exact, not just equal area; erosion is a screen, no ampacity inference.
regions=[]
for z,z2 in zip(boards[1].Zones(),boards[2].Zones()):
 req(uid(z)==uid(z2),'ZONE ID')
 if z.GetIsRuleArea():continue
 for l in z.GetLayerSet().Seq():
  q=z.GetFilledPolysList(l);req(q.Format()==z2.GetFilledPolysList(l).Format(),'PLANE GEOMETRY');e=p.SHAPE_POLY_SET(q);e.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000);regions.append(dict(net=z.GetNetname(),layer=boards[1].GetLayerName(l),outlines=q.OutlineCount(),eroded_outlines=e.OutlineCount()))
# Delete sole bridge, refill, native CLI: exact base recreation.
nd=D/('bridge_deleted'+('_O'if sys.flags.optimize else ''));shutil.copytree(paths[2],nd);f=nd/'mainboard_revD.kicad_pcb';lines=f.read_text().splitlines(keepends=True);new=[];i=0;count=0
while i<len(lines):
 if lines[i]=='\t(segment\n':
  j=i+1
  while lines[j]!='\t)\n':j+=1
  block=''.join(lines[i:j+1]);count+=u in block
  if u not in block:new.append(block)
  i=j+1
 else:new.append(lines[i]);i+=1
req(count==1,'DELETE ONCE');f.write_text(''.join(new));b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);req(sha(f)==H[1],'NEGATIVE EXACT BASE')
cmd=['kicad-cli','pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','-o',str(D/'independent_negative_drc.json'),str(f)];r=subprocess.run(cmd,capture_output=True,text=True);(D/'independent_negative_drc.log').write_text(r.stdout+r.stderr);dr=json.loads((D/'independent_negative_drc.json').read_text());counts=[len(dr[k])for k in ['violations','unconnected_items','schematic_parity']];req(counts==[2,232,0]and r.returncode==5,'NEGATIVE CLI')
for q,h in zip(paths,H):req(sha(q/'mainboard_revD.kicad_pcb')==h,'MUTATED')
res=dict(status='TWO_BOUNDED_RESEARCH_STAGES_ONLY_NOFAB',old533exact=True,bridge_width_mm=.5,bridge_length_mm=.9,plane_geometries_identical=True,source_pads_unchanged=True,actual_core_states=out,bridge_removal_disconnects_plane=True,gnd_via_removal_disconnects_planes_preserving_local_chain=True,erosion_screen=regions,refill_hashes_verified=[H[1],H[2]],negative_recreates_exact_base=H[1],negative_counts=counts,negative_exit=r.returncode,originals_unchanged=True)
(D/'independent_results.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
