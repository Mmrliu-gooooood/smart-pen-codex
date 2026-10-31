import reference_final as z
import json
p=z.p;unions={};refs={p.F_Cu:(p.In1_Cu,'GND'),p.B_Cu:(p.In4_Cu,'GND'),p.In2_Cu:(p.In1_Cu,'GND'),p.In3_Cu:(p.In4_Cu,'GND')}
for u,t in z.bb.items():
 if u not in z.aa and not isinstance(t,p.PCB_VIA):unions.setdefault((t.GetNetname(),t.GetLayer()),p.SHAPE_POLY_SET()).BooleanAdd(z.shape(t))
rows=[]
for (net,l),proj in unions.items():
 if l not in refs:continue
 plane=z.pb[refs[l]];miss=p.SHAPE_POLY_SET();miss.BooleanSubtract(proj,plane);foreign=p.SHAPE_POLY_SET();own=p.SHAPE_POLY_SET();allholes=p.SHAPE_POLY_SET();holes=[]
 for i in range(plane.OutlineCount()):
  for j in range(plane.HoleCount(i)):
   h=p.SHAPE_POLY_SET();h.AddOutline(plane.Hole(i,j));q=p.SHAPE_POLY_SET();q.BooleanIntersection(h,miss)
   if q.Area()<=0:continue
   allholes.BooleanAdd(h);vs=[{'uuid':u,'net':t.GetNetname(),'new':u not in z.aa,'xy':[t.GetPosition().x/1e6,t.GetPosition().y/1e6]}for u,t in z.bb.items()if isinstance(t,p.PCB_VIA)and h.Contains(t.GetPosition())];hasown=any(v['net']==net for v in vs)
   if hasown:own.BooleanAdd(h)
   else:foreign.BooleanAdd(q)
   holes.append({'area':q.Area()/1e12,'has_own_net_via':hasown,'vias':vs})
 rem=p.SHAPE_POLY_SET();rem.BooleanSubtract(miss,allholes);rows.append({'net':net,'layer':z.b.GetLayerName(l),'reference':z.b.GetLayerName(refs[l][0]),'uncovered_mm2':miss.Area()/1e12,'foreign_only_hole_mm2':foreign.Area()/1e12,'outside_all_holes_mm2':rem.Area()/1e12,'holes':holes})
(z.D/'newpaths_final.json').write_text(json.dumps(rows,indent=2))
