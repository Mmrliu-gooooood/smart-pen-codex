from pathlib import Path
import json,os,math,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/mcu-plane0300'
import pcbnew as p
from native_polygon import native_fractured_once
D=Path(__file__).resolve().parent;R=D.parents[1];Q=R/'docs/electronics/mcu_supply_access_study_0242';a=p.LoadBoard(str(R/'hardware/gate_power_candidate_0228/native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));m=json.loads((D/'materialization.json').read_text());plan=json.loads((Q/'two_vias.json').read_text())[0];bt={t.m_Uuid.AsString():t for t in b.GetTracks()};stats=[]
for u,t in zip(m['added'],plan['objects']):
 x=bt[u];v=isinstance(x,p.PCB_VIA);check=dict(type='via'if v else'track',net=x.GetNetname(),layer='through'if v else b.GetLayerName(x.GetLayer()),start=[x.GetStart().x/1e6,x.GetStart().y/1e6],end=[x.GetEnd().x/1e6,x.GetEnd().y/1e6],width=(x.GetWidth(p.F_Cu)if v else x.GetWidth())/1e6,drill=x.GetDrillValue()/1e6 if v else None)
 if check!=t:raise RuntimeError('plan object mismatch '+u)
 stats.append(dict(uuid=u,**check,length_mm=math.dist(check['start'],check['end'])))
def copper(z,b):
 l=z.GetLayer();x=native_fractured_once(z.GetFilledPolysList(l))
 for t in b.GetTracks():
  if not isinstance(t,p.PCB_VIA)or not t.IsOnLayer(l):continue
  h=p.SHAPE_POLY_SET();h.NewOutline();c=t.GetPosition();r=t.GetDrillValue()/2
  for i in range(256):h.Append(round(c.x+r*math.cos(i*2*math.pi/256)),round(c.y+r*math.sin(i*2*math.pi/256)))
  x.BooleanSubtract(h)
 return x
rows=[]
for z in a.Zones():
 if z.GetIsRuleArea():continue
 zz=next(x for x in b.Zones()if x.m_Uuid==z.m_Uuid);old=copper(z,a);new=copper(zz,b);loss=p.SHAPE_POLY_SET();loss.BooleanSubtract(old,new);gain=p.SHAPE_POLY_SET();gain.BooleanSubtract(new,old);e=p.SHAPE_POLY_SET(new);e.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000)
 if e.OutlineCount()!=1:raise RuntimeError('eroded plane disconnected')
 rows.append(dict(net=z.GetNetname(),layer=b.GetLayerName(z.GetLayer()),lost_mm2=loss.Area()/1e12,gained_mm2=gain.Area()/1e12,eroded_025_components=e.OutlineCount()))
mechanics=json.loads((Q/'mechanics.json').read_text());(D/'mechanics_linked.json').write_bytes((Q/'mechanics.json').read_bytes())
print(json.dumps(dict(plan_exact=True,new_objects=stats,physical_planes_all_drills_subtracted=rows,mechanics_source=str(Q/'mechanics.json'),mechanics_sha256=hashlib.sha256((Q/'mechanics.json').read_bytes()).hexdigest(),mechanics_scope='Exact same two poses; original four contexts/budgets associated unchanged; not full new assembly or height qualification'),indent=2))
