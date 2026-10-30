from pathlib import Path
import os,json,math
os.environ['XDG_CONFIG_HOME']='/tmp/pen-layout-config'
import pcbnew as p
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D.parent/'j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb'))
xy=lambda q:(q.x/1e6,q.y/1e6)
def pd(q,a,z):
 dx=z[0]-a[0];dy=z[1]-a[1];t=max(0,min(1,((q[0]-a[0])*dx+(q[1]-a[1])*dy)/(dx*dx+dy*dy))) if dx or dy else 0
 return math.dist(q,(a[0]+t*dx,a[1]+t*dy))
def orient(a,z,q):return(z[0]-a[0])*(q[1]-a[1])-(z[1]-a[1])*(q[0]-a[0])
def sd(a,z,c,d):
 if max(min(a[0],z[0]),min(c[0],d[0]))<=min(max(a[0],z[0]),max(c[0],d[0])) and max(min(a[1],z[1]),min(c[1],d[1]))<=min(max(a[1],z[1]),max(c[1],d[1])) and orient(a,z,c)*orient(a,z,d)<=0 and orient(c,d,a)*orient(c,d,z)<=0:return 0
 return min(pd(a,c,d),pd(z,c,d),pd(c,a,z),pd(d,a,z))
edges=[]
for e in b.GetDrawings():
 if e.GetLayer()==p.Edge_Cuts:
  if e.GetShapeStr()!='Line':raise RuntimeError('unsupported edge')
  edges.append((xy(e.GetStart()),xy(e.GetEnd())))
if len(edges)!=6:raise RuntimeError('unexpected outline')
def inside(q):
 x,y=q;v=False
 for a,z in edges:
  if (a[1]>y)!=(z[1]>y) and x<(z[0]-a[0])*(y-a[1])/(z[1]-a[1])+a[0]:v=not v
 return v
holes=[]
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):holes.append((xy(t.GetPosition()),t.GetDrillValue()/2e6,t.m_Uuid.AsString()))
for f in b.GetFootprints():
 for q in f.Pads():
  s=q.GetDrillSize()
  if s.x or s.y:raise RuntimeError('pad hole requires explicit oval model')
rows=[]
for x in [12.6,12.9,13.2,13.5]:
 a,z=(x,32),(x,89);ed=min(sd(a,z,c,d)for c,d in edges)-.075
 hd,hid=min((pd(q,a,z)-r-.075,u)for q,r,u in holes)
 if not inside(a) or not inside(z) or ed<.25:raise RuntimeError('EDGE_FAIL')
 rows.append({'x':x,'y':[32,89],'actual_outline_copper_gap_mm':ed,'minimum_existing_drill_projection_copper_gap_mm':hd,'nearest_drill_uuid':hid})
# Deliberate .1mm move past .25mm edge floor must fail the independent arithmetic.
if min(sd((13.8,32),(13.8,89),c,d)for c,d in edges)-.075>=.25:raise RuntimeError('NEGATIVE_FAILED')
(D/'edge_and_drill.json').write_text(json.dumps({'outline_edges':edges,'track_width_mm':.15,'required_edge_gap_mm':.25,'lanes':rows,'negative_x13p8_rejected':True,'not_a_new_via_hole_spacing_check':True},indent=2)+'\n')
print(json.dumps(rows,indent=2))
