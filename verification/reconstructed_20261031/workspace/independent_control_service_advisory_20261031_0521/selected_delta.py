import reference_final as z
import native_blocks as n,re,json,hashlib
p=z.p;c=p.LoadBoard(str(z.D/'selected_candidate/mainboard_revD.kicad_pcb'));cs={z.uid(t):t for t in c.GetTracks()}
def contour(b):
 return [tuple((v.x,v.y)for v in q.CPoints())for zone in b.Zones()if not zone.GetIsRuleArea()for i in range(zone.GetFilledPolysList(zone.GetLayer()).OutlineCount())for q in [zone.GetFilledPolysList(zone.GetLayer()).Outline(i)]+[zone.GetFilledPolysList(zone.GetLayer()).Hole(i,j)for j in range(zone.GetFilledPolysList(zone.GetLayer()).HoleCount(i))]]
def blocks(path):
 return {m.group(1):v for _,_,v in n.blocks(path.read_text())if (m:=re.search(r'\(uuid "([^"\n]+)"\)',v))}
a=blocks(z.D/'candidate/mainboard_revD.kicad_pcb');b=blocks(z.D/'selected_candidate/mainboard_revD.kicad_pcb');changes=[u for u in a if a[u]!=b[u]]
if set(a)!=set(b)or len(changes)!=1:raise RuntimeError(changes)
u=changes[0];t=z.bb[u];v=cs[u]
if u in z.aa or t.GetNetname()!='CAM_PWDN_UART_RX'or t.GetLayer()!=p.F_Cu:raise RuntimeError(u)
if contour(z.b)!=contour(c):raise RuntimeError('planes changed')
q=z.shape(v);miss=p.SHAPE_POLY_SET();miss.BooleanSubtract(q,z.pb[p.In1_Cu,'GND']);oldmiss=p.SHAPE_POLY_SET();oldmiss.BooleanSubtract(z.shape(t),z.pb[p.In1_Cu,'GND']);diff=p.SHAPE_POLY_SET();diff.BooleanSubtract(q,z.shape(t));diff.BooleanSubtract(z.pb[p.In1_Cu,'GND'])
(z.D/'selected_delta.json').write_text(json.dumps({'selected_sha256':hashlib.sha256((z.D/'selected_candidate/mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'changed_uuid':u,'old_length':t.GetLength()/1e6,'new_length':v.GetLength()/1e6,'old_start':[t.GetStart().x/1e6,t.GetStart().y/1e6],'old_end':[t.GetEnd().x/1e6,t.GetEnd().y/1e6],'new_start':[v.GetStart().x/1e6,v.GetStart().y/1e6],'new_end':[v.GetEnd().x/1e6,v.GetEnd().y/1e6],'all_filled_vertices_equal':True,'old_track_missing_mm2':oldmiss.Area()/1e12,'new_track_missing_mm2':miss.Area()/1e12,'added_projection_missing_mm2':diff.Area()/1e12,'all_other_uuid_blocks_exact':True},indent=2))
