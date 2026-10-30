from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent
s=(D/'audit_gate.py').read_text();exec(compile(s[:s.index('na,nb=build')],__file__,'exec'))
n=build(b);hits=[]
for ida,_,aa in n['CAM_3V3_PRELINK']:
 for idz,_,zz in n['CAM_3V3_SW']:
  for l in aa.keys()&zz.keys():
   if not aa[l].BBox().Intersects(zz[l].BBox()):continue
   q=p.SHAPE_POLY_SET();q.BooleanIntersection(aa[l],zz[l])
   if q.Area()>1:hits.append([ida,idz,l,q.Area()])
require(not hits,'Actual pre/post commissioning copper bridge')
drc=json.loads((D/'drc_gate.json').read_text());bad=[]
for v in drc['violations']:
 if v['type']in ['shorting_items','clearance','solder_mask_bridge']and any(any('['+net+']'in i.get('description','')for net in ['CAM_3V3_PRELINK','CAM_3V3_SW'])for i in v.get('items',[])):bad.append(v)
require(not bad,'Native output copper shorts/clearance')
print(json.dumps({'pcb_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'actual_pre_post_copper_overlap_all_six_layers':False,'full_native_DRC_output_short_clearance_or_mask_bridge':False,'JP301':'OPEN/DNP; distinct physical islands','scope':'Copper separation only. TPS22918 semiconductor/body-diode and GPIO-domain leakage are not modeled. Unknown external camera remains disconnected.'},indent=2))
