from pathlib import Path
import os,json,hashlib,math
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache'
import pcbnew as p
D=Path(__file__).resolve().parent;oldfile=D.parent/'gate_cam_on_path_maintenance/native/mainboard_revD.kicad_pcb';newfile=D/'native/mainboard_revD.kicad_pcb';old=p.LoadBoard(str(oldfile));new=p.LoadBoard(str(newfile));pt=lambda a:p.VECTOR2I(*(round(v*1e6)for v in a))
window=p.SHAPE_POLY_SET();window.NewOutline()
for x,y in [(0,78),(14,78),(14,88),(0,88)]:window.Append(p.FromMM(x),p.FromMM(y))
def plane(board,net,l):
 q=p.SHAPE_POLY_SET()
 for z in board.Zones():
  if not z.GetIsRuleArea()and z.GetNetname()==net and z.IsOnLayer(l):q.BooleanAdd(z.GetFilledPolysList(l))
 q.Fracture();q.BooleanIntersection(window);return q
cases=[('AON_input_to_bulk','3V3_AON',p.In2_Cu,[9.45,83.9],[4.35,85.6]),('AON_input_to_HF_feed','3V3_AON',p.In2_Cu,[9.45,83.9],[5.72,82.8]),('AON_input_to_left_plane_probe','3V3_AON',p.In2_Cu,[9.45,83.9],[8.6,83.9])]
for l in [p.In1_Cu,p.In4_Cu]:
 cases.extend([('GND_input_to_bulk_return_'+old.GetLayerName(l),'GND',l,[9.45,86.3],[5.7,83.6]),('GND_input_to_HF_return_'+old.GetLayerName(l),'GND',l,[9.45,86.3],[6.55,81.35])])
radii=[0,.025,.05,.075,.1,.125,.15,.2,.25,.3,.4,.5];result=[]
for name,net,l,a,z in cases:
 data={}
 for tag,board in [('before',old),('after',new)]:
  base=plane(board,net,l);vals=[]
  for r in radii:
   q=p.SHAPE_POLY_SET(base)
   if r:q.Inflate(-round(r*1e6),p.CORNER_STRATEGY_ROUND_ALL_CORNERS,250,True)
   shared=[i for i in range(q.OutlineCount())if q.UnitSet(i).Contains(pt(a))and q.UnitSet(i).Contains(pt(z))]
   vals.append({'erosion_radius_mm':r,'same_remaining_plane_island':bool(shared)})
  data[tag]=vals
 regress=[radii[i]for i in range(len(radii))if data['before'][i]['same_remaining_plane_island']and not data['after'][i]['same_remaining_plane_island']]
 result.append({'name':name,'net':net,'layer':old.GetLayerName(l),'from_actual_via_mm':a,'to_mm':z,'target_kind':'non-terminal local plane probe'if'probe'in name else'actual existing capacitor feed/return via','tests':data,'lost_previously_passing_radii_mm':regress})
# Positive comparison only; if baseline has no corridor, do not count it as passing power proof.
print(json.dumps({'before_sha256':hashlib.sha256(oldfile.read_bytes()).hexdigest(),'after_sha256':hashlib.sha256(newfile.read_bytes()).hexdigest(),'window_mm':[0,14,78,88],'method':'Actual filled polygon inward offset with round corners,250nm polygon error. Both fixed anchors must remain in one island. Radius is a comparative geometric clearance screen, NOT trace width/ampacity certification. This is plane-only: it excludes via-drill/barrel/spoke electrical qualification and current density.','cases':result,'any_geometric_corridor_regression':any(c['lost_previously_passing_radii_mm']for c in result),'limits':'A true passing baseline is required to interpret a non-regression. This does not establish global minimum neck, thermal rise, inductance, or safety.'},indent=2))
