import sys,json
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
R=Path(__file__).resolve().parent;d=A.openDocument(str(R/'common_datum_bench.FCStd'));items=[]
for o in d.Objects:
 if not hasattr(o,'Shape'):continue
 s=o.Shape
 if o.Name=='REF_D1_nominal':s=s.common(Part.makeBox(20,20,85,A.Vector(-10,-10,20)))
 v,f=s.tessellate(.08);items.append(dict(name=o.Label,v=[[p.x,p.y,p.z]for p in v],f=f))
(R/'preview_meshes.json').write_text(json.dumps(items))
