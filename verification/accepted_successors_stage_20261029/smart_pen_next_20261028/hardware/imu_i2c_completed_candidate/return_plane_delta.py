exec(compile(open(__file__.replace('return_plane_delta.py','measure.py')).read().split('rows=[]')[0],__file__,'exec'))
newloss={};rows=[]
oldids={t.m_Uuid.AsString():t for t in a.GetTracks()}
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA)or t.m_Uuid.AsString()not in oldids or t.GetLayer()not in[p.F_Cu,p.In3_Cu,p.B_Cu]:continue
 ref=p.In1_Cu if t.GetLayer()==p.F_Cu else p.In4_Cu;q=shape(t,t.GetLayer());old=p.SHAPE_POLY_SET();old.BooleanIntersection(q,planes['before',ref]);now=p.SHAPE_POLY_SET();now.BooleanIntersection(q,planes['after',ref]);lost=p.SHAPE_POLY_SET();lost.BooleanSubtract(old,now)
 if lost.Area()>1e4:
  row={'net':t.GetNetname(),'uuid':t.m_Uuid.AsString(),'layer':b.GetLayerName(t.GetLayer()),'a':xy(t.GetStart()),'z':xy(t.GetEnd()),'new_lost_reference_area_mm2':lost.Area()/1e12};rows.append(row);newloss[t.GetNetname()]=newloss.get(t.GetNetname(),0)+lost.Area()/1e12
r={'note':'Existing track copper newly lacking projected GND; not electromagnetic qualification. Area threshold 1e-8 mm2.','by_net':newloss,'items':rows};(D/'return_plane_delta.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
