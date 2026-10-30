import os,sys,json,hashlib
from pathlib import Path
os.environ['XDG_CONFIG_HOME']='/tmp/mech-dvp-audit'
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
R=Path(__file__).resolve().parent;M=R.parent/'smart_pen_mechanics_next_20261028/mechanical';B=2.264793176328504;V=A.Vector
p=M/'compliant_retainer_longarc_0415/access_revision/ACCESS_retainer_OD19_t0p93_NOFAB.FCStd';d=A.openDocument(str(p));S={o.Label:o.Shape.copy()for o in d.Objects if hasattr(o,'Shape')};A.closeDocument(d.Name);out=[]
for ref,cx,cz,shape,target in [('R206',2,80,(2.45,.95),'REF_HousingRight'),('J107.2',-5.5,43.1,(1.8,2.2),'Lower_common_datum_STUDY')]:
 rows=[]
 for h in [.1,.3,.414,.415,.464,.465,.55,.7,1.45,2]:
  s=Part.makeBox(shape[0],h,shape[1],V(cx-shape[0]/2,B-h,cz-shape[1]/2));c=s.common(S[target]);rows.append({'height':h,'volume':c.Volume})
 out.append({'ref':ref,'XY_budget':shape,'target':target,'height_sensitivity_NOT_part_choice':rows})
# Smaller dimensions below are sensitivity only, not chosen substitute or body qualification.
for ref,cx,cz,shape,target,h in [('R206_body_sensitivity',2,80,(1.6,.8),'REF_HousingRight',.55),('J107_copper_XY_with_2mm_termination_sensitivity',-5.5,43.1,(1.4,1.8),'Lower_common_datum_STUDY',2)]:
 s=Part.makeBox(shape[0],h,shape[1],V(cx-shape[0]/2,B-h,cz-shape[1]/2));out.append({'ref':ref,'XY_sensitivity':shape,'height':h,'volume':s.common(S[target]).Volume,'NOT_selected':True})
# Independent negative control: elevate the obstacle-targeted column out of B component region.
ctrl=Part.makeBox(2.45,1.45,.95,V(2-2.45/2,B+2,80-.95/2));v=ctrl.common(S['REF_HousingRight']).Volume
if abs(v)>1e-7:raise ValueError('separated control failed')
if out[0]['height_sensitivity_NOT_part_choice'][-2]['volume']<.18:raise ValueError('original collision missed')
if out[1]['height_sensitivity_NOT_part_choice'][-1]['volume']<.019:raise ValueError('wire collision missed')
(R/'conflict_sensitivity.json').write_text(json.dumps({'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'cases':out,'separated_control_volume':v},indent=2)+'\n');print(json.dumps(out,indent=2))
