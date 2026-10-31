import reference_final as z
import json
p=z.p;out={}
for n,b in [('baseline',z.a),('candidate',z.b)]:
 plane=z.planes(b)[p.In2_Cu,'3V3_AON'];rows=[]
 for i in range(plane.OutlineCount()):
  unit=plane.UnitSet(i);box=unit.BBox();rows.append({'island':i,'area_mm2':unit.Area()/1e12,'bbox':[box.GetX()/1e6,box.GetY()/1e6,box.GetRight()/1e6,box.GetBottom()/1e6],'AON_vias':[{'xy':[t.GetPosition().x/1e6,t.GetPosition().y/1e6],'uuid':z.uid(t)}for t in b.GetTracks()if isinstance(t,p.PCB_VIA)and t.GetNetname()=='3V3_AON'and unit.Contains(t.GetPosition())]})
 missing=[{'xy':[t.GetPosition().x/1e6,t.GetPosition().y/1e6],'uuid':z.uid(t)}for t in b.GetTracks()if isinstance(t,p.PCB_VIA)and t.GetNetname()=='3V3_AON'and not plane.Contains(t.GetPosition())]
 out[n]={'islands':rows,'AON_vias_not_in_plane':missing}
(z.D/'plane_islands_final.json').write_text(json.dumps(out,indent=2))
