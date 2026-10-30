import sys,json
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A
from patch_supports import ROOT
R=Path(__file__).resolve().parent/'corrected_connected';rows=[]
for ctx in ['RevD_BENCH','ACCESS19','ACCESS20']:
 docs=[A.openDocument(str(p))for p in [ROOT/'assembly_outline_sync_20261030_1239'/(ctx+'_exact_outline_NOFAB.FCStd'),R/(ctx+'_support_proposal_NOFAB.FCStd')]]
 O=[{o.Label:o.Shape for o in d.Objects if hasattr(o,'Shape')}for d in docs]
 labels=[k for k in O[0]if k.startswith('INSTALL_')or k.startswith('Native_outline')]
 checks=[]
 for k in labels:
  a,b=O[0][k],O[1][k];v=a.common(b).Volume;delta=a.Volume+b.Volume-2*v
  checks.append(dict(label=k,volume_symmetric_difference=delta,bounds_equal=str(a.BoundBox)==str(b.BoundBox),valid=b.isValid()))
 if len(labels)!=105 or any(abs(x['volume_symmetric_difference'])>1e-7 or not x['bounds_equal']or not x['valid']for x in checks):raise RuntimeError('preservation failed '+ctx)
 rows.append(dict(context=ctx,board_plus_installations=len(labels),checks=checks))
 for d in docs:A.closeDocument(d.Name)
(R/'preservation.json').write_text(json.dumps(rows,indent=2)+'\n');print('PASS exact board and 104 full solids unchanged in all three derivatives')
