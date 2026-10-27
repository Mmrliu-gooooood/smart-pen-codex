import sys,os,json
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A,Part
r=os.path.dirname(__file__)
for name in ['optical_bench','pen18_envelope_NOT_FOR_PRINT','pen18_compact170_NOT_FOR_PRINT']:
 d=A.openDocument(r+'/'+name+'.FCStd');out=[]
 for o in d.Objects:
  if name=='optical_bench' and (o.Name=='Nose_guide_coupon' or o.Name.startswith('Paper_wedge')):continue
  if name.startswith('pen') and o.Name in ['Controller_populated_candidate','Battery_complete_budget','Battery_expansion_reserve','Refill_service_sweep','FPC_route_placeholder','Antenna_keepout_placeholder','RF_keepout_placeholder']:continue
  s=o.Shape
  if o.Name=='Shell_d18_wall1p5':s=s.cut(Part.makeBox(30,15,220,A.Vector(-15,-15,-1)))
  v,f=s.tessellate(.15)
  out.append({'name':o.Name,'v':[[a.x,a.y,a.z] for a in v],'f':f})
 json.dump(out,open(r+'/'+name+'_render_meshes.json','w'))
