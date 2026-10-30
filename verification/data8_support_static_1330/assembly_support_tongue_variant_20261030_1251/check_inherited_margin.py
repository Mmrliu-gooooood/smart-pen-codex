import sys,json
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A
R=Path(__file__).resolve().parent;ROOT=R.parent;rows=[]
for ctx in ['ACCESS19','ACCESS20']:
 values=[]
 for p in [ROOT/'assembly_outline_sync_20261030_1239'/(ctx+'_exact_outline_NOFAB.FCStd'),R/'corrected_connected'/(ctx+'_support_proposal_NOFAB.FCStd')]:
  d=A.openDocument(str(p));O={o.Label:o.Shape for o in d.Objects if hasattr(o,'Shape')};values.append(O['Upper_nonlocating_cover_STUDY'].distToShape(O['INSTALL_C103_12'])[0]);A.closeDocument(d.Name)
 if abs(values[0]-values[1])>1e-9:raise RuntimeError('C103 clearance changed')
 rows.append(dict(context=ctx,C103_upper_cover_distance_old_new_mm=values))
(R/'inherited_margin.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
