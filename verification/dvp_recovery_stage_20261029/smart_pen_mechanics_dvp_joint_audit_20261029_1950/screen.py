import os,sys,json,hashlib,math
from pathlib import Path
os.environ['XDG_CONFIG_HOME']='/tmp/mech-dvp-audit';os.environ['XDG_DATA_HOME']='/tmp/mech-dvp-audit'
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part,pcbnew as p
R=Path(__file__).resolve().parent;W=R.parent;M=W/'smart_pen_mechanics_next_20261028/mechanical';H=W/'smart_pen_next_20261028';B=2.264793176328504;F=B+.93;V=A.Vector
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def req(x,msg):
 if not x:raise ValueError(msg)
base=H/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb';src=H/'hardware/dvp_joint_native_candidate_1950/native/mainboard_revD.kicad_pcb';req(sha(base)=='9a0335443167a4395431cb78abfab959893060d82a7b4da9e5fcd861bc40c038','base');req(sha(src)=='184dce12e82219e5d4bb3e1f20f84cf2bc6e06c1494f5b23862f5e1978024f81','candidate')
a=p.LoadBoard(str(base));b=p.LoadBoard(str(src));fa={f.GetReference():f for f in a.GetFootprints()};fb={f.GetReference():f for f in b.GetFootprints()}
def pose(f):return [f.GetPosition().x/1e6,f.GetPosition().y/1e6,f.GetOrientationDegrees(),f.GetLayerName()]
changed=[r for r in fa if pose(fa[r])!=pose(fb[r])];req(len(changed)==29,'count');req(all(pose(fa[r])==pose(fb[r])for r in ['J103','J106']),'fixed')
inputs=[('RevC',M/'gate508e_joint_screen_0247/RevC_gate508e.FCStd','CTX_'),('RevD_BENCH',M/'gate508e_joint_screen_0247/RevD_gate508e.FCStd','REF_CTX_')]+[(f'ACCESS{od}',M/f'compliant_retainer_longarc_0415/access_revision/ACCESS_retainer_OD{od}_t0p93_NOFAB.FCStd','REF_CTX_')for od in [19,20]]
def relevant(a,b):
 x,y=a.BoundBox,b.BoundBox
 return all(min(getattr(x,t+'Max'),getattr(y,t+'Max'))-max(getattr(x,t+'Min'),getattr(y,t+'Min'))>1e-8 for t in 'XYZ')
def hits(s,others):
 out=[]
 for k,t in others.items():
  if relevant(s,t):
   v=s.common(t).Volume
   if v>1e-7:out.append({'other':k,'volume_mm3':v})
 return out
rows=[]
for name,path,pre in inputs:
 d=A.openDocument(str(path));S={o.Label:o.Shape.copy()for o in d.Objects if hasattr(o,'Shape') and o.TypeId!='App::DocumentObjectGroup'};A.closeDocument(d.Name);modified={};contracts={}
 for r in changed:
  keys=[k for k in S if k==pre+r or k.startswith(pre+r+'.') or k.startswith(pre+r+'_')];req(bool(keys),'missing '+name+' '+r)
  old,new=pose(fa[r]),pose(fb[r]);side=new[3];newx,newz=new[0]-7,127-new[1]
  for k in keys:
   bb=S[k].BoundBox;h=bb.YLength
   if r in ['J105','J107']:
    num=k[-1];pad=next(q for q in fb[r].Pads()if q.GetNumber()==num);cx=pad.GetPosition().x/1e6-7;cz=127-pad.GetPosition().y/1e6;lx,lz=1.8,2.2;h=2.0
   else:
    cx,cz=newx,newz;lx,lz=bb.XLength,bb.ZLength
    if abs((new[2]-old[2])%180-90)<1e-6:lx,lz=lz,lx
   y0=B-h if side=='B.Cu'else F
   ss=Part.makeBox(lx,h,lz,V(cx-lx/2,y0,cz-lz/2));modified[k]=ss;contracts[k]={'ref':r,'old_pose':old,'new_pose':new,'retained_budget_XYZ':[lx,h,lz],'height_qualified':False,'height_basis':'inherited frozen context envelope, NOT newly verified manufacturer maximum or solder assembly height','bounds':[cx-lx/2,y0,cz-lz/2,cx+lx/2,y0+h,cz+lz/2]}
 S.update(modified)
 results={}
 for k,s in modified.items():
  others={z:t for z,t in S.items()if z!=k and z not in ['Context_ONLY','REF_Context_ONLY']}
  hh=hits(s,others);bb=s.BoundBox;side=contracts[k]['new_pose'][3];probe=Part.makeBox(bb.XLength,20,bb.ZLength,V(bb.XMin,B-20 if side=='B.Cu'else F,bb.ZMin));ob=[]
  for z,t in others.items():
   if not relevant(probe,t):continue
   c=probe.common(t)
   if c.Volume>1e-7:
    available=B-c.BoundBox.YMax if side=='B.Cu'else c.BoundBox.YMin-F
    ob.append({'other':z,'first_obstacle_height_mm':max(0,available)})
  ob.sort(key=lambda x:x['first_obstacle_height_mm']);results[k]={'budget_hits':hh,'first_height_obstacles':ob[:4]}
 rows.append({'context':name,'source_sha256':sha(path),'contracts':contracts,'results':results})
out={'status':'CONDITIONAL_EXISTING_ENVELOPE_SCREEN_NOFAB','native_candidate_sha256':sha(src),'accepted_sha256':sha(base),'changed_refs':changed,'new_or_moved_B_refs':[r for r in changed if pose(fb[r])[3]=='B.Cu'],'contexts':rows,'warning':'Budget intersections are model conflicts, not a claim about unknown actual component maximum heights. Zero intersections do not qualify unmodeled battery, optics, wire bends, solder tools, assembly, strength or thermal clearance.'}
(R/'screen_results.json').write_text(json.dumps(out,indent=2)+'\n')
for r in rows:
 print(r['context'],[(k,x['budget_hits'])for k,x in r['results'].items()if x['budget_hits']],flush=True)
