import math,json
from pathlib import Path
R=Path(__file__).resolve().parent
rows=[]
for U in [.005,.01,.02,.025]:
 lo=.08+U;hi=.12-U;rows.append(dict(U=U,measured_interval=[lo,hi],width=max(0,hi-lo),robust_nonzero_window=hi-lo>1e-12))
if not rows[1]['robust_nonzero_window']or rows[2]['robust_nonzero_window']:raise ValueError('guardband logic')
projection=[dict(axial_d=d,theta_from_normal_deg=a,plane_projection_mm=d*math.sin(math.radians(a)))for d in [.25,.35]for a in[30,45,60]]
out=dict(status='INTERPRETATION_ERRATUM_NOT_NEW_MECHANICAL_RELEASE',five_micron_is_vendor_requirement=False,five_micron_purchase_required=False,original_true_ON_window=[.08,.12],guardband_rows=rows,projection=projection,replacement_stroke_approved=False,instrument_U_qualified=False)
print(json.dumps(out,indent=2))
