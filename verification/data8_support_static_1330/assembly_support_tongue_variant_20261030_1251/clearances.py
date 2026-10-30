import sys,json
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A
ROOT=Path(__file__).resolve().parents[1];C=ROOT/'assembly_support_tongue_variant_20261030_1251/corrected_connected';R=Path(__file__).resolve().parent;rows=[]
for ctx in ['RevD_BENCH','ACCESS19','ACCESS20']:
 d=A.openDocument(str(C/(ctx+'_support_proposal_NOFAB.FCStd')));O={o.Label:o.Shape for o in d.Objects if hasattr(o,'Shape')};keys=['Common_base']if ctx=='RevD_BENCH'else['Lower_common_datum_STUDY','Upper_nonlocating_cover_STUDY','COMPLIANT_FRAME_KINEMATIC_NOT_MATERIAL_QUALIFIED']
 for k in keys:
  ds=[]
  for n,s in O.items():
   if n.startswith('INSTALL_'):ds.append(dict(envelope=n,distance_mm=O[k].distToShape(s)[0]))
  ds.sort(key=lambda x:x['distance_mm']);rows.append(dict(context=ctx,changed_part=k,envelopes_checked=len(ds),touching=[x for x in ds if x['distance_mm']<1e-7],nearest_ten=ds[:10],all_distances=ds));print(ctx,k,ds[:3],flush=True)
  (R/'clearances.json').write_text(json.dumps(rows,indent=2)+'\n')
 A.closeDocument(d.Name)
