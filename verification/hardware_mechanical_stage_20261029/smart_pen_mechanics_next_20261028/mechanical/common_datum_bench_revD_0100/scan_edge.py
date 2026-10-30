import sys,json
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
R=Path(__file__).resolve().parent;d=A.openDocument(str(R.parent/'contact_oblique_harness_revC_0038/contact_oblique_harness.FCStd'));S={o.Name:o.Shape.copy()for o in d.Objects if hasattr(o,'Shape')};V=A.Vector
out=[]
for z in range(37,123):
 h=[]
 for side,x in [('L',-7.4),('R',6.5)]:
  for face,y in [('B',1.7647931763),('F',3.1947931763)]:
   a=Part.makeBox(.9,.5,2,V(x,y,z-1));bad=[]
   for n,s in S.items():
    if n=='CTX_main_board':continue
    v=a.common(s).Volume
    if v>1e-6:bad.append(n)
   if bad:h.append([side,face,bad])
 out.append(dict(z=z,hits=h))
print(json.dumps(out,indent=2));(R/'edge_scan.json').write_text(json.dumps(out,indent=2))
