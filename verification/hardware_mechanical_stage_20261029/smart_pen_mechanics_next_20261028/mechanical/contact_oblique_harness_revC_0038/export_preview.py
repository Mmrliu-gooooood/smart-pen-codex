import sys,json
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
R=Path(__file__).resolve().parent;d=A.openDocument(str(R/'contact_oblique_harness.FCStd'));items=[];clip=Part.makeBox(20,20,10,A.Vector(-10,-10,72))
for o in d.Objects:
 if not hasattr(o,'Shape') or o.Name in ['HousingLeft','HousingRight','RearCalibrationShim'] or o.Name.startswith('CTX_'):continue
 s=o.Shape.common(clip)
 if not s.Volume:continue
 v,f=s.tessellate(.03);items.append(dict(name=o.Name,v=[[p.x,p.y,p.z]for p in v],f=f))
(R/'preview_meshes.json').write_text(json.dumps(items))
