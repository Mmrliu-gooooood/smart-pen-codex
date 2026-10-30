exec(compile(open(__file__.replace('via_plane_screen.py','measure.py')).read().split('rows=[]')[0],__file__,'exec'))
def distpoint(v,a,z):
 dx=z[0]-a[0];dy=z[1]-a[1];den=dx*dx+dy*dy;u=max(0,min(1,((v[0]-a[0])*dx+(v[1]-a[1])*dy)/den))if den else 0;return math.hypot(v[0]-a[0]-u*dx,v[1]-a[1]-u*dy)
def boundarydist(q,v):
 best=1e9
 for i in range(q.OutlineCount()):
  for c in [q.COutline(i)]+[q.CHole(i,j)for j in range(q.HoleCount(i))]:
   pts=[xy(c.CPoint(j))for j in range(c.PointCount())]
   for aa,zz in zip(pts,pts[1:]+pts[:1]):best=min(best,distpoint(v,aa,zz))
 return best
oldids={t.m_Uuid.AsString()for t in a.GetTracks()};via=[]
for t in b.GetTracks():
 if not isinstance(t,p.PCB_VIA)or t.m_Uuid.AsString()in oldids:continue
 vv=xy(t.GetPosition());rr=[]
 for l in [p.In1_Cu,p.In2_Cu,p.In4_Cu]:
  old=planes['before',l];dd=boundarydist(old,vv);inside=old.Contains(t.GetPosition());rr.append({'layer':b.GetLayerName(l),'center_inside_old_plane':inside,'old_boundary_distance_mm':dd,'radius0p375_clearance_disc_to_old_boundary_mm':dd-.375 if inside else None})
 via.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'xy':vv,'layers':rr})
rf=p.SHAPE_POLY_SET();clock=p.SHAPE_POLY_SET()
for t in b.GetTracks():
 if t.GetLayer()!=p.F_Cu:continue
 q=shape(t,p.F_Cu)
 if t.GetNetname().startswith('RF_'):rf.BooleanAdd(q)
 if 'CLK'in t.GetNetname():clock.BooleanAdd(q)
for f in b.GetFootprints():
 for pad in f.Pads():
  if not pad.IsOnLayer(p.F_Cu):continue
  if pad.GetNetname().startswith('RF_'):rf.BooleanAdd(shape(pad,p.F_Cu))
  if 'CLK'in pad.GetNetname():clock.BooleanAdd(shape(pad,p.F_Cu))
def distpoly(q,z):
 lo=0;hi=20000000
 if q.Collide(z,0):return 0
 for _ in range(26):
  mid=(lo+hi)//2
  if q.Collide(z,mid):hi=mid
  else:lo=mid+1
 return hi/1e6
lost=p.SHAPE_POLY_SET();lost.BooleanSubtract(planes['before',p.In1_Cu],planes['after',p.In1_Cu]);critical={}
for name,q in [('RF_F_copper_and_pads',rf),('clock_F_copper_and_pads',clock)]:
 ix=p.SHAPE_POLY_SET();ix.BooleanIntersection(lost,q);critical[name]={'new_void_projected_overlap_mm2':ix.Area()/1e12,'nearest_new_In1_void_to_copper_mm':distpoly(lost,q)}
# Rules identical by full verifier. Screen new objects against actual six-layer RF region.
rules=[z for z in b.Zones()if z.GetIsRuleArea()and z.GetZoneName().startswith('RF_')];intr=[]
for t in b.GetTracks():
 if t.m_Uuid.AsString()in oldids:continue
 for z in rules:
  for l in L if isinstance(t,p.PCB_VIA)else[t.GetLayer()]:
   ix=p.SHAPE_POLY_SET();ix.BooleanIntersection(shape(t,l),z.Outline())
   if ix.Area()>1:intr.append({'uuid':t.m_Uuid.AsString(),'rule':z.GetZoneName(),'layer':b.GetLayerName(l),'area_mm2':ix.Area()/1e12})
r={'status':'LOCAL_PLANE_DISC_SCREEN_NOT_FULL_PLANE_CURRENT_OR_NECK_QUALIFICATION','clearance_disc_radius_mm':.375,'note':'Copper radius .225 + plane clearance .15. Signed separation is distance from disc to previous boundary, not a whole-board minimum neck. Negative/merged clearances need local interpretation; full finite island graph separately checked.','vias':via,'critical_projection':critical,'new_RF_region_intrusions':intr};(D/'via_plane_screen.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
