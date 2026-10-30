from pathlib import Path
import os,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/path1000';import pcbnew as p
import sys,math
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
def capsule(a,b,r):
 dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);nx,ny=-dy*r/length,dx*r/length
 pts=[A.Vector(a[0]+nx,a[1]+ny,0),A.Vector(b[0]+nx,b[1]+ny,0),A.Vector(b[0]-nx,b[1]-ny,0),A.Vector(a[0]-nx,a[1]-ny,0)];pts.append(pts[0]);shape=Part.Face(Part.makePolygon(pts)).extrude(A.Vector(0,0,.01))
 for x,y in [a,b]:shape=shape.fuse(Part.makeCylinder(r,.01,A.Vector(x,y,0)))
 return shape
def box(x0,y0,x1,y1):return Part.makeBox(x1-x0,y1-y0,.01,A.Vector(x0,y0,0))
O=Path(__file__).resolve().parent;W=O.parent;parent=W/'smart_pen_next_20261028/hardware/tail100_routing_native_0927/native/mainboard_revD.kicad_pcb';candidate=W/'smart_pen_next_20261028/hardware/tail_courtyard_native_0949/native/mainboard_revD.kicad_pcb';old=p.LoadBoard(str(parent));b=p.LoadBoard(str(candidate))
def ident(t):return(t.GetLayerName(),t.GetNetname(),t.GetWidth(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y)
oldtracks={ident(t)for t in old.GetTracks()if not isinstance(t,p.PCB_VIA)};L=json.load(open(W/'assembly_context_audit_0818_20261030/all103_sync.json'))['rows'];out=[]
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA)or ident(t)in oldtracks or t.GetLayerName()not in ['F.Cu','B.Cu']:continue
 start=[t.GetStart().x/1e6,t.GetStart().y/1e6];end=[t.GetEnd().x/1e6,t.GetEnd().y/1e6];s=capsule(start,end,t.GetWidth()/2e6);hits=[]
 for r in L:
  if r['current_pose'][3]!=t.GetLayerName()or r['ref']=='J108':continue # mixed pad-side J108 has no fitted body; tested separately
  for e in r['contexts'][0]['entities']:
   bb=list(e['projected_current_bounds_not_final_assembly']);x0,x1=bb[0]+7,bb[3]+7;y0,y1=127-bb[5],127-bb[2]
   if r['ref']=='J202':y0-=1.7;y1-=1.7
   area=s.common(box(x0,y0,x1,y1)).Volume/.01
   if area>1e-8:hits.append({'ref':r['ref'],'entity':e['label'],'projection_area_mm2':area})
 out.append({'net':t.GetNetname(),'layer':t.GetLayerName(),'start':start,'end':end,'width':t.GetWidth()/1e6,'same_face_full_budget_projections':hits})
res={'sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'parent_sha256':hashlib.sha256(parent.read_bytes()).hexdigest(),'changed_outer_tracks':out,'scope':'Finite copper projections only; same-face installation budget overlap does not prove protruding-body collision or accept solder/mask process. Inner routing has no exterior tool volume.'};(O/'path_projection.json').write_text(json.dumps(res,indent=2)+'\n');print('tracks',len(out),'overlaps',[(r['net'],r['layer'],[(h['ref'],h['projection_area_mm2'])for h in r['same_face_full_budget_projections']])for r in out if r['same_face_full_budget_projections']])
