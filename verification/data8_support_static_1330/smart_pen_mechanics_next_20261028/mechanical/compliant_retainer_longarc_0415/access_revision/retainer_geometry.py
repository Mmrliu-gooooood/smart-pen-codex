import sys
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
V=A.Vector;B=2.264793176328504

def box(a,b,c,d,e,f):return Part.makeBox(b-a,d-c,f-e,V(a,c,e))
def beam(p0,p3,thick_axis,width_axis,thickness,width):
 # Geometric cubic cantilever-like family, not an elastic solution of this frame/material.
 # primary direction is p3-p0 projected independently by caller; control p1/p2 passed as tuple.
 p0,p1,p2,p3=p0
 def edge(sign):
  c=Part.BezierCurve();c.setPoles([p+thick_axis*(sign*thickness/2)for p in [p0,p1,p2,p3]]);return c.toShape()
 up=edge(1);lo=edge(-1);lo.reverse()
 wire=Part.Wire([up,Part.makeLine(p3+thick_axis*thickness/2,p3-thick_axis*thickness/2),lo,Part.makeLine(p0-thick_axis*thickness/2,p0+thick_axis*thickness/2)])
 return Part.Face(wire).extrude(width_axis*width)
def retainer(thickness=.93,free=False,stop=False):
 s=box(-7.8,-7.3,3.5,4.4,29.1,137.6).fuse(box(7.3,7.8,3.5,4.4,29.1,137.6))
 for z,endz in [(29.1,31.9),(133.6,137.6)]:s=s.fuse(box(-7.8,7.8,3.35,3.75,z,endz))
 delta=0 if free else(.3 if stop else thickness-.75)
 for side,z in [(-1,45),(1,45),(-1,131)]:
  x=-7.35 if side<0 else 6.75;end=B+.75+delta+.4;root=3.85;start=z-8
  pts=[V(x,root,start),V(x,root,start+8/3),V(x,(root+end)/2,start+16/3),V(x,end,z)]
  q=beam(pts,None,V(0,1,0),V(1,0,0),.7,.6);toe=Part.makeCylinder(.4,.6,V(x,end,z),V(1,0,0))
  xa,xb=(-7.8,-6.75)if side<0 else(6.75,7.8)
  s=s.fuse(box(xa,xb,3.5,4.2,start-.4,start+.4)).fuse(q).fuse(toe)
  ceiling=B+.75+.3+.8;s=s.fuse(box(xa,xb,ceiling,ceiling+.45,z-.6,z+.6))
 # Two separate lateral compliant features. Do NOT reuse Y-finger force constants.
 yc=B+.465;dx=0 if free else(.15 if stop else .05)
 for z in [45,131]:
  root=7.6;end=7.25+dx;start=z-6;y=yc-.2
  pts=[V(root,y,start),V(root,y,start+2),V((root+end)/2,y,start+4),V(end,y,z)]
  q=beam(pts,None,V(1,0,0),V(0,1,0),.25,.4);toe=Part.makeCylinder(.3,.4,V(end,y,z),V(0,1,0))
  s=s.fuse(box(7.4,7.8,y,4.2,start-.3,start+.3)).fuse(q).fuse(toe)
  s=s.fuse(box(7.7,7.95,y,4.4,z-.6,z+.6))
 # Tail Z spring acts at left tail, near the headstop load line; its own travel model is independent.
 dz=0 if free else(.4 if stop else .1);root=134.8;end=133.7+dz;y=yc-.2
 pts=[V(2.5,y,root),V(2.5-8/3,y,root),V(2.5-16/3,y,(root+end)/2),V(-5.5,y,end)]
 q=beam(pts,None,V(0,0,1),V(0,1,0),.25,.4);toe=Part.makeCylinder(.3,.4,V(-5.5,y,end),V(0,1,0))
 s=s.fuse(box(2.2,2.8,y,3.75,134.5,135.4)).fuse(q).fuse(toe).fuse(box(-5.8,-5.2,y,3.75,134.4,134.65))
 for x,z in [(-3.8,30.5),(-3.8,136.2)]:s=s.cut(Part.makeCylinder(.9,1,V(x,3,z),V(0,1,0)))
 return s
if __name__=='__main__':
 import json
 from pathlib import Path
 R=Path(__file__).resolve().parent;rows=[];d=A.newDocument('RetainerStates')
 for name,t,free,stop in [('FREE',.75,True,False),('INSTALLED_0p83',.83,False,False),('INSTALLED_0p93',.93,False,False),('STOP_LIMIT',1.05,False,True)]:
  s=retainer(t,free,stop);o=d.addObject('Part::Feature',name);o.Label=name;o.Shape=s;rows.append(dict(name=name,valid=s.isValid(),solids=len(s.Solids),volumes=[x.Volume for x in s.Solids],volume=s.Volume))
 d.recompute();d.saveAs(str(R/'retainer_kinematic_states_ONLY.FCStd'));A.closeDocument(d.Name);(R/'retainer_geometry_results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
