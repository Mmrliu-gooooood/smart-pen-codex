from pathlib import Path
import sys,json,hashlib,copy
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A
O=Path(__file__).resolve().parent;W=O.parent;C=W/'reconstruction_saved_cad_f27_20261031_0156';E=json.load(open(W/'reconstruction_sccb_margin_mechanics_20261031_0214/proposed_full104.json'));manifest=json.load(open(C/'manifest.json'));rows=[];out=copy.deepcopy(E)
def need(x,m):
 if not x:raise RuntimeError(m)
def hit(a,b):
 x,y=a.BoundBox,b.BoundBox
 if any(min(getattr(x,k+'Max'),getattr(y,k+'Max'))-max(getattr(x,k+'Min'),getattr(y,k+'Min'))<1e-8 for k in 'XYZ'):return 0.
 return a.common(b).Volume
poses={'R230':(11.1,34.25,90),'R219':(6.2,39.5,0)}
for e in out['all_static_rectangles']:
 if e['ref'] not in poses:continue
 x,y,a=poses[e['ref']];dx,dy=(.95,2.45)if a==90 else(2.45,.95);e['xy_bounds']=[x-dx/2,y-dy/2,x+dx/2,y+dy/2];e['native_pose']=[x,y,a];old=e['cad_bounds_XYZ'];e['cad_bounds_XYZ']=[x-dx/2-7,old[1],127-y-dy/2,x+dx/2-7,old[4],127-y+dy/2]
for ctx in ['RevC','RevD_BENCH','ACCESS19','ACCESS20']:
 q=C/f'{ctx}_NEW_f27_RESEARCH_NOFAB.FCStd';sha=hashlib.sha256(q.read_bytes()).hexdigest();need(sha==manifest['files'][q.name],'saved source hash')
 d=A.openDocument(str(q));S={o.Label:o.Shape.copy()for o in d.Objects if hasattr(o,'Shape')and not o.Shape.isNull()};A.closeDocument(d.Name);changed={}
 for ref,(x,y,angle) in poses.items():
  key=next(k for k in S if k.startswith('INSTALL_'+ref+'_'));s=S[key].copy();old=s.BoundBox;center=old.Center
  if angle:s.rotate(center,A.Vector(0,1,0),angle)
  s.translate(A.Vector(x-7-center.x,0,127-y-center.z));bb=s.BoundBox;e=next(e for e in out['all_static_rectangles']if e['ref']==ref);got=[bb.XMin,bb.YMin,bb.ZMin,bb.XMax,bb.YMax,bb.ZMax];need(max(abs(a-b)for a,b in zip(got,e['cad_bounds_XYZ']))<1e-7,'exact transformed contract');need(abs(s.Volume-S[key].Volume)<1e-8,'full body volume');S[key]=s;changed[key]=s
 hits=[];near=[]
 for key,s in changed.items():
  for k,t in S.items():
   if k==key or k.startswith('Native_outline'):continue
   v=hit(s,t)
   if v>1e-7:hits.append({'moved':key,'other':k,'volume_mm3':v})
   near.append({'moved':key,'other':k,'gap_mm':s.distToShape(t)[0]})
 need(not hits,'pose collision '+str(hits))
 wrong=next(s.copy()for k,s in changed.items()if k.startswith('INSTALL_R230_'));target=next(t for k,t in S.items()if k.startswith('INSTALL_U201_'));wrong.translate(target.BoundBox.Center-wrong.BoundBox.Center);negative=hit(wrong,target);need(negative>0,'body negative missed')
 rows.append({'context':ctx,'saved_source_sha256':sha,'proposed_poses':poses,'hits':hits,'nearest':sorted(near,key=lambda e:e['gap_mm'])[:12],'full_static_entities':104,'saved_file_modified':False,'deliberate_U201_center_negative_mm3':negative})
(O/'placement_results.json').write_text(json.dumps(rows,indent=2)+'\n');(O/'proposed_full104.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS four saved-source contexts; proposed only')
