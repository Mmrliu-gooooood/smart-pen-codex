import sys,json,hashlib
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A,Part
from patch_supports import apply,ROOT,B
R=Path(__file__).resolve().parent/'corrected_connected'
R.mkdir(exist_ok=True)
S=ROOT/'assembly_outline_sync_20261030_1239'
rows=[]
for context in ['RevD_BENCH','ACCESS19','ACCESS20']:
 p=S/(context+'_exact_outline_NOFAB.FCStd')
 if not p.exists():raise RuntimeError('missing synchronized baseline '+str(p))
 print('OPEN',context,flush=True);d=A.openDocument(str(p));O={o.Label:o for o in d.Objects if hasattr(o,'Shape')};old={k:o.Shape.copy()for k,o in O.items()}
 changes=apply(d,context);print('PATCHED',context,flush=True);hits=[];pair=[]
 for k in changes:
  s=O[k].Shape
  for n,o in O.items():
   if n==k or not s.BoundBox.intersect(o.Shape.BoundBox):continue
   v=s.common(o.Shape).Volume
   if v>1e-7:
    ov=old[k].common(old[n]).Volume
    row=dict(changed=k,other=n,volume=v,old_volume=ov,delta=v-ov)
    (hits if n.startswith(('INSTALL_','Native_outline','WIRE_','CONTACT_','GND_'))else pair).append(row)
 out=R/(context+'_support_proposal_NOFAB.FCStd');d.recompute();d.saveAs(str(out))
 # STEP includes full retained contracts and original unmodified assembly items.
 Part.export([o for o in d.Objects if hasattr(o,'Shape')],str(R/(context+'_support_proposal_NOFAB.step')))
 rows.append(dict(context=context,baseline_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),candidate_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),installation_count=sum(k.startswith('INSTALL_')for k in O),changed=changes,valid={k:O[k].Shape.isValid()for k in changes},solids={k:len(O[k].Shape.Solids)for k in changes},full_envelope_hits=hits,part_intersections=pair))
 A.closeDocument(d.Name)
 (R/'exact_context_tests.json').write_text(json.dumps(rows,indent=2)+'\n')
 print(context,rows[-1],flush=True)
