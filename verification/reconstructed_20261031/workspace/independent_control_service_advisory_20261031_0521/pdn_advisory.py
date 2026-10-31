import reference_final as z
import json,math
p=z.p;V=lambda a:p.VECTOR2I(round(a[0]*1e6),round(a[1]*1e6));xy=lambda v:[v.x/1e6,v.y/1e6];out={}
rows=[]
for row in json.loads((z.D/'reference_checkpoint.json').read_text())['retained_reference_losses']:
 t=z.aa[row['uuid']];key=(z.b.GetLayerID(row['reference_layer']),row['reference_net']);q=p.SHAPE_POLY_SET();q.BooleanIntersection(z.shape(t),z.pa[key]);q.BooleanSubtract(z.pb[key]);holes=[]
 for i in range(z.pb[key].OutlineCount()):
  for j in range(z.pb[key].HoleCount(i)):
   h=p.SHAPE_POLY_SET();h.AddOutline(z.pb[key].Hole(i,j));r=p.SHAPE_POLY_SET();r.BooleanIntersection(q,h)
   if r.Area()>0:holes.append({'area_mm2':r.Area()/1e12,'vias':[{'uuid':u,'net':v.GetNetname(),'xy':xy(v.GetPosition()),'new':u not in z.aa}for u,v in z.bb.items()if isinstance(v,p.PCB_VIA)and h.Contains(v.GetPosition())]})
 rows.append(dict(row,holes=holes))
out['retained_losses']=rows
for name,b in [('baseline',z.a),('candidate',z.b)]:
 ps=z.planes(b);rows=[];start=(7.85,15.2)
 for l,net,a,ends in [(p.In1_Cu,'GND',start,[(4.5,11.5),(6,11.5),(7.5,11.5)]),(p.In4_Cu,'GND',start,[(4.5,11.5),(6,11.5),(7.5,11.5)]),(p.In2_Cu,'3V3_AON',(5.4,14.75),[(5.175,18.9),(6.45,17),(7.4,4.8),(1.8,8),(3.6,5.8)])]:
  plane=ps[l,net]
  for e in ends:
   areas=[]
   for w in [.15,.3,.5]:
    t=p.PCB_TRACK(b);t.SetLayer(p.F_Cu);t.SetStart(V(a));t.SetEnd(V(e));t.SetWidth(round(w*1e6));q=z.shape(t);q.BooleanSubtract(plane);areas.append({'width_mm':w,'outside_plane_mm2':q.Area()/1e12})
   rows.append({'net':net,'layer':b.GetLayerName(l),'start':a,'end':e,'span_mm':math.dist(a,e),'same_islands':[i for i in range(plane.OutlineCount())if plane.UnitSet(i).Contains(V(a))and plane.UnitSet(i).Contains(V(e))],'corridors':areas})
 out[name+'_corridors']=rows
out['candidate_new_vias']=[{'uuid':u,'net':t.GetNetname(),'xy':xy(t.GetPosition())}for u,t in z.bb.items()if u not in z.aa and isinstance(t,p.PCB_VIA)]
(z.D/'pdn_advisory.json').write_text(json.dumps(out,indent=2));print(json.dumps(rows,indent=2))
