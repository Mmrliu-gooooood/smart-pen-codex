from pathlib import Path
import os,sys,json,math,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/ground0807'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[2];BASE=R/'hardware/camera_schmitt_native_0745/native/mainboard_revD.kicad_pcb'
sys.path.insert(0,str(R/'hardware/camera_schmitt_native_0745'));import geometry_native as g
b=g.b;req=lambda c,m:None if c else (_ for _ in ()).throw(RuntimeError(m));req(hashlib.sha256(BASE.read_bytes()).hexdigest()=='3276f04433c8ee3759f963fdc133200aee0b398ec6009e31a82fd595ab2f4328','exact0745')
sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));from finite_copper import build,components
nodes=build(b)['GND'];core=next(c for c in components(nodes)if'J106.3'in c);isol=[c[0]for c in components(nodes)if len(c)==1];req(len(core)==71 and len(isol)==32,'actual0745ground')
lookup={name:sh for name,_,sh in nodes};seen={'J106.3'};todo=['J106.3']
while todo:
 sh=lookup[todo.pop()]
 for name,z in lookup.items():
  if name in seen:continue
  for l in sh.keys()&z.keys():
   if not sh[l].BBox().Intersects(z[l].BBox()):continue
   q=p.SHAPE_POLY_SET();q.BooleanIntersection(sh[l],z[l])
   if q.Area()>1:seen.add(name);todo.append(name);break
pm={}
for f in b.GetFootprints():
 for a in f.Pads():
  name=f.GetReference()+'.'+a.GetNumber();pm[name]=a;pm[name+'#'+a.m_Uuid.AsString()]=a
anchors=[]
for name in core:
 a=pm[name]
 for l in [p.F_Cu,p.B_Cu]:
  if a.IsOnLayer(l):anchors.append((name,g.xy(a),l))
for t in b.GetTracks():
 if t.GetNetname()!='GND'or t.m_Uuid.AsString()not in seen:continue
 if isinstance(t,p.PCB_VIA):
  for l in [p.F_Cu,p.B_Cu]:anchors.append((t.m_Uuid.AsString(),g.xy(t),l))
 else:
  for xy in [(t.GetStart().x/1e6,t.GetStart().y/1e6),(t.GetEnd().x/1e6,t.GetEnd().y/1e6)]:
   if t.GetLayer()in[p.F_Cu,p.B_Cu]:anchors.append((t.m_Uuid.AsString(),xy,t.GetLayer()))
# New GND through hole removes AON In2 copper: screen against retained In3 signal strips.
old_in3=[t for t in b.GetTracks()if not isinstance(t,p.PCB_VIA)and t.GetLayer()==p.In3_Cu and t.GetNetname()not in ['GND','3V3_AON','SENS_VIO_1V8']]
def ref_risk(v):
 h=g.shape(v,p.In2_Cu,150000)
 return[t.m_Uuid.AsString()for t in old_in3 if h.BBox().Intersects(g.shape(t,p.In3_Cu).BBox()) and area(h,g.shape(t,p.In3_Cu))>1]
def area(x,y):
 q=p.SHAPE_POLY_SET();q.BooleanIntersection(x,y);return q.Area()
def routes(a,z):
 yield[a,z]
 dx=z[0]-a[0];dy=z[1]-a[1];d=min(abs(dx),abs(dy));sx=1 if dx>=0 else-1;sy=1 if dy>=0 else-1
 for mid in [(a[0]+sx*d,a[1]+sy*d),(z[0]-sx*d,z[1]-sy*d)]:
  if math.dist(a,mid)>.001 and math.dist(mid,z)>.001:yield[a,mid,z]
def tracks(l,pts):return[g.track('GND',l,a,z,.3)for a,z in zip(pts,pts[1:])if math.dist(a,z)>.001]
def makevia(xy):
 v=g.via('GND',xy);v.SetWidth(p.F_Cu,450000);v.SetDrill(200000);return v
rows=[];new=[];candidates=[];order=sorted([x for x in isol if not x.startswith('J202.')],key=lambda x:(x!='R104.2',g.xy(pm[x])[1],g.xy(pm[x])[0]))
for name in order:
 a=pm[name];xy=g.xy(a);l=p.B_Cu if a.IsOnLayer(p.B_Cu)else p.F_Cu;choices=[];rejections=[]
 near=sorted([(an,z,ll)for an,z,ll in anchors if ll==l and .001<math.dist(xy,z)<=3],key=lambda k:math.dist(xy,k[1]))[:10]
 for an,z,ll in near:
  for pts in routes(xy,z):choices.append((sum(math.dist(a,z)for a,z in zip(pts,pts[1:])),False,an,pts,tracks(l,pts)))
 for radius in [.85,1.1,1.4,1.7]:
  for dx,dy in[(1,0),(-1,0),(0,1),(0,-1),(.70710678,.70710678),(-.70710678,.70710678),(.70710678,-.70710678),(-.70710678,-.70710678)]:
   z=(round(xy[0]+radius*dx,3),round(xy[1]+radius*dy,3));v=makevia(z)
   if ref_risk(v):continue
   choices.append((math.dist(xy,z)+1.2,True,'new_plane_via',[xy,z],tracks(l,[xy,z])+[v]))
 chosen=None
 for score,isvia,target,pts,items in sorted(choices,key=lambda c:c[0]):
  errs=g.errors(items)
  if errs:
   rejections.append({'target':target,'via':isvia,'xy':pts[-1],'first_errors':errs[:2]});continue
  chosen=(score,isvia,target,pts,items);break
 if chosen:
  score,isvia,target,pts,items=chosen
  g.objs.extend(items);new.extend(items)
  for i in items:
   candidates.append({'target_pad':name,'type':'via'if isinstance(i,p.PCB_VIA)else'track','net':'GND','layer':b.GetLayerName(i.GetLayer()),'a':list(g.xy(i))if isinstance(i,p.PCB_VIA)else[i.GetStart().x/1e6,i.GetStart().y/1e6],'b':[i.GetEnd().x/1e6,i.GetEnd().y/1e6],'width':(i.GetWidth(p.F_Cu)if isinstance(i,p.PCB_VIA)else i.GetWidth())/1e6,'drill':i.GetDrillValue()/1e6 if isinstance(i,p.PCB_VIA)else None})
  anchors.append((name,xy,l))
  if isvia:
   for ll in[p.F_Cu,p.B_Cu]:anchors.append(('proposed_via_for_'+name,pts[-1],ll))
  rows.append({'pad':name,'xy':xy,'layer':b.GetLayerName(l),'accepted_finite_geometry':True,'anchor':target,'new_via':isvia,'path':pts,'rejected_before_success':len(rejections)})
 else:rows.append({'pad':name,'xy':xy,'layer':b.GetLayerName(l),'accepted_finite_geometry':False,'tested_candidates':len(choices),'rejections':rejections})
 print(name,'clear'if chosen else'BLOCKED',flush=True)
(D/'model.json').write_text(json.dumps({'status':'LOCAL_GND_GROUP_PLANNING_ONLY_NO_SUCCESSOR_FREEZE','source_pcb_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'actual_base_core_pads':core,'actual_base_isolated_pads':isol,'scope':'26 non-J202 singleton pads, nearest <=3mm anchors and <=1.7mm radial via choices; no old edits','rows':rows,'new':candidates,'pending':'J202 six targets separately planned; true refilled physical/DRC/courtyard evidence required before considering connections proven'},indent=2)+'\n')
print('accepted',sum(x['accepted_finite_geometry']for x in rows),'objects',len(new),'vias',sum(isinstance(t,p.PCB_VIA)for t in new))
