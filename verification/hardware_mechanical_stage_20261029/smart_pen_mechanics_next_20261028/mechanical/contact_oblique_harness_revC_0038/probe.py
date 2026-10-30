import sys,json,math
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A,Part
R=Path(__file__).resolve().parent
D=A.openDocument(str(R.parent/'compact_contact_cassette_backspacer_revB_0031/compact_contact_candidate.FCStd'))
V=A.Vector
out=[]
for name,x,tx in [('CONTACT',-2.3,-4),('GND',2.3,-1.6)]:
 a=V(x,-1.6,78.0952);b=V(tx,1.9599931763,75);u=b-a
 s=Part.makeCylinder(.3048,u.Length,a,u)
 hits=[]
 for o in D.Objects:
  if not hasattr(o,'Shape') or o.Name=='Context_ONLY' or o.Name.startswith('Wire_') or 'J103' in o.Label:continue
  v=s.common(o.Shape).Volume
  if v>1e-7:hits.append([o.Name,o.Label,v])
 out.append(dict(name=name,length=u.Length,a=list(a),b=list(b),hits=hits))
print(json.dumps(out,indent=2))
