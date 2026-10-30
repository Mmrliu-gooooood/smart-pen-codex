from pathlib import Path
import sys,os,json,math,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/indecontrol1104';sys.path.append('/usr/lib/freecad-python3/lib');import pcbnew as p,FreeCAD as A,Part
O=Path(__file__).resolve().parent;W=O.parent;H=W/'smart_pen_next_20261028/hardware';q=H/'control_envelope_native_1051/native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(q));old=p.LoadBoard(str(H/'unused_bias_native_1017/native/mainboard_revD.kicad_pcb'))
def req(x,msg):
 if not x:raise RuntimeError(msg)
req(hashlib.sha256(q.read_bytes()).hexdigest()=='8312b1d5ec56f0ab4c396cba2b78449e191f06225bf9aa64ea6522fd1c3c68bb','SHA')
def ident(t):return(t.GetClass(),t.GetNetname(),t.GetLayerName(),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None)
oldset={ident(t)for t in old.GetTracks()};new=[t for t in b.GetTracks()if ident(t)not in oldset];req(sum(isinstance(t,p.PCB_VIA)for t in new)==2 and len(new)==20,'18track2via')
def extra(f):return sorted([(z.GetNumber(),int(z.GetAttribute()),z.GetDrillSize().x,z.GetDrillSize().y,int(z.GetDrillShape()),z.GetOffset().x,z.GetOffset().y,z.GetRoundRectRadiusRatio())for z in f.Pads()])
req({f.GetReference():extra(f)for f in b.GetFootprints()}=={f.GetReference():extra(f)for f in old.GetFootprints()},'extra pad changed');req(len(list(b.GetFootprints()))==103,'103')
es=[e for e in b.GetDrawings()if e.GetLayer()==p.Edge_Cuts];req(len(es)==6 and all(e.GetShapeStr()=='Line'for e in es),'6lines');ends={}
for e in es:
 for v in [e.GetStart(),e.GetEnd()]:ends[(v.x,v.y)]=ends.get((v.x,v.y),0)+1
req(all(n==2 for n in ends.values()),'closed outline');bounds=[min(x for x,y in ends)/1e6,min(y for x,y in ends)/1e6,max(x for x,y in ends)/1e6,max(y for x,y in ends)/1e6];req(bounds==[0,-6.5,14,93.3],'bounds')
f=next(f for f in b.GetFootprints()if f.GetReference()=='J104');f.BuildCourtyardCaches();c=f.GetCourtyard(p.B_Cu);pts=[c.Outline(i).CPoint(k)for i in range(c.OutlineCount())for k in range(c.Outline(i).PointCount())];jb=[min(v.x for v in pts)/1e6,min(v.y for v in pts)/1e6,max(v.x for v in pts)/1e6,max(v.y for v in pts)/1e6];req(jb==[9.005,51.805,10.995,57.795],'J104 native rect')
L=json.load(open(W/'assembly_context_audit_0818_20261030/all103_sync.json'))['rows'];r=next(r for r in L if r['ref']=='C206');v=r['contexts'][0]['entities'][0]['projected_current_bounds_not_final_assembly'];cb=[v[0]+7,127-v[5],v[3]+7,127-v[2]]
def rect(v):return Part.makeBox(v[2]-v[0],v[3]-v[1],.01,A.Vector(v[0],v[1],0))
def cap(t):
 a=[t.GetStart().x/1e6,t.GetStart().y/1e6];b=[t.GetEnd().x/1e6,t.GetEnd().y/1e6];r=(t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth())/2e6;s=Part.makeCylinder(r,.01,A.Vector(*a,0));dx,dy=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dy)
 if l:
  nx,ny=-dy*r/l,dx*r/l;v=[A.Vector(a[0]+nx,a[1]+ny,0),A.Vector(b[0]+nx,b[1]+ny,0),A.Vector(b[0]-nx,b[1]-ny,0),A.Vector(a[0]-nx,a[1]-ny,0)];v.append(v[0]);s=s.fuse(Part.Face(Part.makePolygon(v)).extrude(A.Vector(0,0,.01))).fuse(Part.makeCylinder(r,.01,A.Vector(*b,0)))
 return s
out=[]
for name,side,bb in [('J104_review_expanded_rectangle',p.B_Cu,[8.955,51.755,11.045,57.845]),('C206',p.F_Cu,cb),('J104_actual_native_cached',p.B_Cu,jb)]:
 ob=rect(bb);rows=[]
 for t in new:
  if not isinstance(t,p.PCB_VIA)and t.GetLayer()!=side:continue
  s=cap(t);rows.append({'type':'via'if isinstance(t,p.PCB_VIA)else'track','net':t.GetNetname(),'gap_mm':s.distToShape(ob)[0]})
 rows.sort(key=lambda x:x['gap_mm']);out.append({'ref':name,'bounds':bb,'minimum':rows[0],'closest_track':min((x for x in rows if x['type']=='track'),key=lambda x:x['gap_mm'])})
req(abs(out[0]['minimum']['gap_mm']-.205)<1e-8 and abs(out[0]['closest_track']['gap_mm']-.20958922617)<1e-8,'J104 distances');req(abs(out[1]['minimum']['gap_mm']-.60913503104)<1e-8,'C206 distance')
res={'board_sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'outline':bounds,'additional_pad_attributes_equal':True,'new_tracks':18,'new_vias':2,'independent_OCC_full_width_margins':out};(O/'independent_results.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
