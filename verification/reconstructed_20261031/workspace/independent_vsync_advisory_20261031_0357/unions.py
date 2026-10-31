import reference_final as z
import json
p=z.p;rows=json.loads((z.D/'reference_checkpoint.json').read_text())['retained_reference_losses'];groups={}
for r in rows:groups.setdefault((r['net'],r['reference_layer'],r['reference_net']),set()).add(r['uuid'])
def box(q):
 b=q.BBox();return[b.GetX()/1e6,b.GetY()/1e6,b.GetRight()/1e6,b.GetBottom()/1e6]
out=[]
for (net,l,n),ids in groups.items():
 proj=p.SHAPE_POLY_SET()
 for u in ids:proj.BooleanAdd(z.shape(z.aa[u]))
 k=(z.b.GetLayerID(l),n);q=p.SHAPE_POLY_SET();q.BooleanIntersection(proj,z.pa[k]);q.BooleanSubtract(z.pb[k]);out.append({'net':net,'reference_layer':l,'reference_net':n,'unique_track_UUIDs':sorted(ids),'union_loss_mm2':q.Area()/1e12,'bbox':box(q)})
loss=p.SHAPE_POLY_SET();loss.BooleanSubtract(z.pa[p.In2_Cu,'3V3_AON'],z.pb[p.In2_Cu,'3V3_AON']);components=[{'area_mm2':loss.UnitSet(i).Area()/1e12,'bbox':box(loss.UnitSet(i))}for i in range(loss.OutlineCount())]
r={'retained_loss_unions':out,'In2_total_plane_loss_components':components,'AON_via_centers_in_removed_plane':[{'uuid':u,'xy':[t.GetPosition().x/1e6,t.GetPosition().y/1e6]}for u,t in z.bb.items()if isinstance(t,p.PCB_VIA)and t.GetNetname()=='3V3_AON'and loss.Contains(t.GetPosition())],'zone_minimum_thickness_mm':[q.GetMinThickness()/1e6 for q in z.b.Zones()if not q.GetIsRuleArea()and q.GetLayer()==p.In2_Cu]};(z.D/'union_losses.json').write_text(json.dumps(r,indent=2))
