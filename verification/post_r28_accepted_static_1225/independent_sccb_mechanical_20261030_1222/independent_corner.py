from pathlib import Path
import os,sys,json,math,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/indesccb1222';sys.path.append('/usr/lib/freecad-python3/lib');import pcbnew as p,FreeCAD as A,Part
O=Path(__file__).resolve().parent;W=O.parent;H=W/'smart_pen_next_20261028/hardware';q=H/'sccb_local_reference_1216/native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(q));old=p.LoadBoard(str(H/'control_envelope_native_1051/native/mainboard_revD.kicad_pcb'))
def req(x,msg):
 if not x:raise RuntimeError(msg)
req(hashlib.sha256(q.read_bytes()).hexdigest()=='dcbd2e6501c8294ece5ecf7b41ffcc86ccc7f58f7cb54ececfdf24962a50f697','SHA')
def cap(t):
 a=[t.GetStart().x/1e6,t.GetStart().y/1e6];b=[t.GetEnd().x/1e6,t.GetEnd().y/1e6];r=(t.GetWidth(p.B_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth())/2e6;s=Part.makeCylinder(r,.01,A.Vector(*a,0));dx,dy=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dy)
 if l:
  nx,ny=-dy*r/l,dx*r/l;v=[A.Vector(a[0]+nx,a[1]+ny,0),A.Vector(b[0]+nx,b[1]+ny,0),A.Vector(b[0]-nx,b[1]-ny,0),A.Vector(a[0]-nx,a[1]-ny,0)];v.append(v[0]);s=s.fuse(Part.Face(Part.makePolygon(v)).extrude(A.Vector(0,0,.01))).fuse(Part.makeCylinder(r,.01,A.Vector(*b,0)))
 return s
keys={frozenset([(10.9,64.875),(11.125,65.025)]),frozenset([(11.125,65.025),(12.05,64.875)])};ts=[t for t in b.GetTracks()if not isinstance(t,p.PCB_VIA)and t.GetNetname()=='3V3_AON'and t.GetLayer()==p.B_Cu and frozenset([(t.GetStart().x/1e6,t.GetStart().y/1e6),(t.GetEnd().x/1e6,t.GetEnd().y/1e6)])in keys];req(len(ts)==2 and all(t.GetWidth()==500000 for t in ts),'corner exact');branch=cap(ts[0]).fuse(cap(ts[1]));L=json.load(open(W/'assembly_context_audit_0818_20261030/all103_sync.json'))['rows'];out=[]
for ref in ['C301','U301']:
 r=next(r for r in L if r['ref']==ref);bb=r['contexts'][0]['entities'][0]['projected_current_bounds_not_final_assembly'];xy=[bb[0]+7,127-bb[5],bb[3]+7,127-bb[2]];rect=Part.makeBox(xy[2]-xy[0],xy[3]-xy[1],.01,A.Vector(xy[0],xy[1],0));inter=branch.common(rect);remain=inter.copy();n=0
 for t in old.GetTracks():
  if t.GetNetname()!='3V3_AON'or (not isinstance(t,p.PCB_VIA)and t.GetLayer()!=p.B_Cu):continue
  s=cap(t)
  if s.BoundBox.intersect(inter.BoundBox):remain=remain.cut(s);n+=1
 residual=remain.Volume/.01;req(abs(residual)<1e-10,'new OCC underbody projection');out.append({'ref':ref,'branch_projection_area_mm2':inter.Volume/.01,'additional_projection_mm2_OCC':residual,'old_overlapping_capsules_tested':n})
(O/'independent_corner.json').write_text(json.dumps({'exact_parent':'8312b1d5ec56f0ab4c396cba2b78449e191f06225bf9aa64ea6522fd1c3c68bb','method':'OCC analytic finite-width round-cap copper, no expansion of source; residual failure threshold1e-10mm2','rows':out},indent=2)+'\n');print(out)
