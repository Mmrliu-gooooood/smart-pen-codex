import sys,json,math
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
R=Path(__file__).resolve().parent;d=A.openDocument(str(R/'contact_oblique_harness.FCStd'));S={o.Name:o.Shape for o in d.Objects if hasattr(o,'Shape')}
physical=['HousingLeft','HousingRight','SwitchCarrierPCB','FrontCalibrationShim','RearCalibrationShim','SPVE_body_conservative','M1p6x8_at_66','M1p6x8_at_78','Slider']
hits=[]
for i,k in enumerate(physical):
 for j in physical[i+1:]:
  v=S[k].common(S[j]).Volume
  if v>1e-7:hits.append([k,j,v])
print('physical',hits)
for k in S:
 if not(k.startswith('Solder_') or k.startswith('StrainBushing')):continue
 h=[]
 for j in S:
  if j.startswith(('Harness_','Solder_','StrainBushing')) or 'J103' in j:continue
  v=S[k].common(S[j]).Volume
  if v>1e-7:h.append([j,v])
 print(k,h)
