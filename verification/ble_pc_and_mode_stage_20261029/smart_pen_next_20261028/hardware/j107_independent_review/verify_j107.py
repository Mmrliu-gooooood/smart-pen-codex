from pathlib import Path
import json,hashlib,collections
D=Path(__file__).resolve().parent;s=(D/'audit_gate.py').read_text();exec(compile(s[:s.index('na,nb=build')],__file__,'exec'))
S=D.parent/'gate_cam_on_path_maintenance';base=S/'native/mainboard_revD.kicad_pcb';old=p.LoadBoard(str(base));delta=json.loads((D/'j107_delta.json').read_text());require(hashlib.sha256(base.read_bytes()).hexdigest()==delta['input_pcb_sha256'],'Wrong 1c49 baseline')
def geom(t):return(t.GetClass(),t.GetNetname(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,int(t.GetLayer()),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None)
aa={t.m_Uuid.AsString():geom(t)for t in old.GetTracks()};zz={t.m_Uuid.AsString():geom(t)for t in b.GetTracks()};removed={r['uuid']for r in delta['removed']};added={r['uuid']for r in delta['added']}
require(set(aa)-set(zz)==removed and set(zz)-set(aa)==added,'Exact J107 copper set')
require(all(aa[u]==zz[u]for u in aa.keys()&zz.keys()),'Surviving original copper changed')
require(all(aa[u][1]=='GND'for u in removed),'Removed non-ground copper')
byid={t.m_Uuid.AsString():t for t in b.GetTracks()}
for r in delta['added']:
 t=byid[r['uuid']];require(t.GetNetname()==r['net'],'Added actual net')
 if r['type']=='via':require(t.GetDrillValue()==300000 and all(t.GetWidth(l)==600000 for l in L),'Via six-layer diameter/drill')
 else:require(t.GetWidth()==round(r['width']*1e6)and b.GetLayerName(t.GetLayer())==r['layer']and[t.GetStart().x,t.GetStart().y]==[round(v*1e6)for v in r['a']]and[t.GetEnd().x,t.GetEnd().y]==[round(v*1e6)for v in r['z']],'Added width/layer/geometry')
def fg(f):return(f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees(),f.GetLayer(),f.GetAttributes(),f.GetValue(),f.GetFPIDAsString(),f.GetPath().AsString(),[(q.GetNumber(),q.GetNetname(),q.GetPosition().x,q.GetPosition().y,q.GetSize().x,q.GetSize().y,q.GetOrientationDegrees(),list(q.GetLayerSet().Seq()))for q in f.Pads()])
require({f.GetReference():fg(f)for f in old.GetFootprints()}=={f.GetReference():fg(f)for f in b.GetFootprints()},'Any physical/source footprint changed')
na,nb=build(old),build(b);ca={n:components(v)for n,v in na.items()if sum(x[1]for x in v)>1};cb={n:components(v)for n,v in nb.items()if sum(x[1]for x in v)>1}
for net,comps in ca.items():
 for group in comps:require(any(set(group)<=set(q)for q in cb[net]),'Old component split '+net)
 if net not in ['USB_EN1','USB_EN2','GND']:require(comps==cb[net],'Unexpected other-net merge '+net)
for net,pins in [('USB_EN1',{'J107.1','U101.24'}),('USB_EN2',{'J107.2','U101.27'})]:require(cb[net]==[sorted(pins)],'Mode input not closed independently '+net)
oldground=next(c for c in ca['GND']if'C104.2'in c);newground=next(c for c in cb['GND']if'C104.2'in c)
require(set(newground)==set(oldground)|{'J107.3'},'Ground merge must add only J107.3 to core')
require(len(cb['GND'])==len(ca['GND'])-1,'Unexpected ground component count')
require(all(q in newground for q in ['J106.3','J107.3','U501.5','U501.6','U501.7','U501.8','C501.2','C502.2','C503.2','U301.2','C301.2']),'Actual current return lost')
# Right legacy stitch + present input return retained, not skinny replacement of load path.
require('e95ec091-2805-4117-b87e-25db7835b752'in zz and zz['e95ec091-2805-4117-b87e-25db7835b752'][7]==500000,'Present J106 ground main trace changed')
require('3e5c1457-dfe2-4fd3-8145-4f946500f344'in zz,'Present J106 ground via lost')
right=[t for t in b.GetTracks()if isinstance(t,p.PCB_VIA)and t.GetNetname()=='GND'and t.GetPosition()==p.VECTOR2I(9400000,82400000)];require(len(right)==1,'Right legacy GND stitching via not preserved')
# Test every actual filled AON island, not just pad components.
aon=[(n,pad or '/'in n,sh)for n,pad,sh in nb['3V3_AON']];groups=components(aon);core=next(c for c in groups if'C104.1'in c);islands=[n for n,_,_ in aon if '/'in n];require(all(n in core for n in islands),'Floating AON filled island')
def filled(board):
 out={}
 for z in board.Zones():
  if z.GetIsRuleArea():continue
  for l in L:
   if z.IsOnLayer(l):out[(z.m_Uuid.AsString(),int(l))]=(z.GetNetname(),z.GetFilledPolysList(l))
 return out
fa,fb=filled(old),filled(b);areas=[]
for k,(net,q)in fa.items():
 r=fb[k][1];gone=p.SHAPE_POLY_SET(q);gone.BooleanSubtract(r);new=p.SHAPE_POLY_SET(r);new.BooleanSubtract(q)
 areas.append({'zone':k[0],'net':net,'layer':b.GetLayerName(k[1]),'before_islands':q.OutlineCount(),'after_islands':r.OutlineCount(),'before_area_mm2':q.Area()/1e12,'after_area_mm2':r.Area()/1e12,'removed_plane_mm2':gone.Area()/1e12,'added_plane_mm2':new.Area()/1e12})
# Entire two control nets checked against other nets on each actual layer.
hits=[]
for net in ['USB_EN1','USB_EN2']:
 for name,_,ss in nb[net]:
  for other,nodes in nb.items():
   if other==net:continue
   for oname,_,oo in nodes:
    for l in ss.keys()&oo.keys():
     if not ss[l].BBox().Intersects(oo[l].BBox()):continue
     q=p.SHAPE_POLY_SET();q.BooleanIntersection(ss[l],oo[l])
     if q.Area()>1:hits.append([net,name,other,oname,int(l)])
require(not hits,'Actual USB mode net short '+str(hits))
result={'pcb_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'old_pad_components_preserved':True,'mode_components':{n:cb[n]for n in ['USB_EN1','USB_EN2']},'GND_components_before':len(ca['GND']),'GND_components_after':len(cb['GND']),'only_GND_pad_added_to_existing_core':'J107.3','existing_input_IMU_MCU_gate_GND_core_preserved':True,'existing_J106_ground_trace_width_mm':.5,'new_J107_reference_ground_trace_width_mm':.5,'AON_all_pad_components_unchanged':ca['3V3_AON']==cb['3V3_AON'],'all_AON_filled_islands_in_core':islands,'plane_geometry_delta':areas,'control_cross_net_actual_copper_overlap':hits,'all_footprints_unchanged':True,'no_mode_ties_or_source_BOM_change':True,'limits':'Static finite copper only; AON/GND plane area/connection do not qualify neck ampacity, return inductance, external harness or current-loop sharing. JP301 OPEN; charging commissioning unchanged; NOFAB.'}
print(json.dumps(result,indent=2))
