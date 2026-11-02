import os,sys,json,math
from pathlib import Path
os.environ.update(XDG_CONFIG_HOME='/tmp/pcb_interface_clean_617a/config',XDG_CACHE_HOME='/tmp/pcb_interface_clean_617a/cache',XDG_DATA_HOME='/tmp/pcb_interface_clean_617a/data')
import pcbnew as p
D=Path(__file__).parent;sys.path.insert(0,str(D/'review_dependencies'));from native_polygon import native_fractured_once
b=p.LoadBoard(str(D/'candidate/mainboard_revD.kicad_pcb'));vias={tuple((t.GetPosition().x/1e6,t.GetPosition().y/1e6)):t for t in b.GetTracks()if t.GetClass()=='PCB_VIA'and t.GetNetname()=='GND'};out=[]
for layer in[p.In1_Cu,p.In4_Cu]:
 plane=p.SHAPE_POLY_SET()
 for z in b.Zones():
  if not z.GetIsRuleArea()and z.GetLayer()==layer and z.GetNetname()=='GND':plane.BooleanAdd(native_fractured_once(z.GetFilledPolysList(layer)))
 contacts=[]
 for xy in[(11.1,32.325),(1.5,33.725)]:
  v=vias[xy];q=p.SHAPE_POLY_SET();v.TransformShapeToPolygon(q,layer,0,25,p.ERROR_OUTSIDE);drill=p.SHAPE_POLY_SET();drill.NewOutline();rad=v.GetDrillValue()/2
  # Conservative circumscribed drill removes slightly MORE hole area, never creates a false annular contact.
  for i in range(256):
   ang=2*math.pi*i/256;drill.Append(p.VECTOR2I(v.GetPosition().x+round(rad/math.cos(math.pi/256)*math.cos(ang)),v.GetPosition().y+round(rad/math.cos(math.pi/256)*math.sin(ang))))
  q.BooleanSubtract(drill);q.BooleanIntersection(plane);contacts.append({'via_xy':xy,'uuid':v.m_Uuid.AsString(),'annular_plane_contact_mm2':q.Area()/1e12})
 if plane.OutlineCount()!=1 or not all(x['annular_plane_contact_mm2']>0 for x in contacts):raise RuntimeError('actual common plane conductor not proven')
 out.append({'layer':b.GetLayerName(layer),'same_filled_GND_component_count':plane.OutlineCount(),'contacts':contacts})
(D/'ground_conductor.json').write_text(json.dumps({'scope':'Actual finite annular contact to same filled GND polygon, not merely matching net labels; no ampacity/IR/PDN qualification','planes':out},indent=2));print(out)
