from pathlib import Path
import os,json
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache'
import pcbnew as p
D=Path(__file__).resolve().parent
import re
base=D.parent/'imu_compact_0402_placement/mainboard_revD.kicad_pcb'
oldids={'531b0f10-034c-4aa6-a1b3-283da8e482e2','fd731fad-49f7-4daa-8c1d-abda098559cf','97081987-0a80-4c7e-b5e9-2c4782127c11'}
raw=base.read_text()
raw=re.sub(r'\n\t\((?:segment|via)\n.*?\n\t\)',lambda m:'' if any(u in m[0] for u in oldids) else m[0],raw,flags=re.S)
(D/'mainboard_revD.kicad_pcb').write_text(raw)
b=p.LoadBoard(str(D/'mainboard_revD.kicad_pcb'));rows=[]
def pt(a):return p.VECTOR2I(*(round(v*1e6) for v in a))
def route(net,ps,w):
 for a,z in zip(ps,ps[1:]):
  t=p.PCB_TRACK(b);t.SetStart(pt(a));t.SetEnd(pt(z));t.SetWidth(p.FromMM(w));t.SetLayer(p.B_Cu);t.SetNet(b.FindNet(net));b.Add(t);rows.append(dict(uuid=t.m_Uuid.AsString(),net=net,type='track',a=a,z=z,width=w,layer='B.Cu'))
def via(net,a):
 v=p.PCB_VIA(b);v.SetPosition(pt(a));v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(b.FindNet(net));b.Add(v);rows.append(dict(uuid=v.m_Uuid.AsString(),net=net,type='via',xy=a,diameter=.6,drill=.3))
# Two explicit old signal detours; preserve their original end vertices.
oldids={'531b0f10-034c-4aa6-a1b3-283da8e482e2','fd731fad-49f7-4daa-8c1d-abda098559cf','97081987-0a80-4c7e-b5e9-2c4782127c11'}
route('3V3_AON',[(11.1,65.95),(11.3,66.05)],.5);via('3V3_AON',(11.3,66.05))
route('3V3_AON',[(11.1,64.3),(11.3,64.5),(11.3,64.8)],.5);via('3V3_AON',(11.3,64.8))
route('GND',[(9.4,63.9),(9.9,63.4),(10,63.4)],.3)
route('GND',[(11.1,67),(11.3,67)],.4);via('GND',(11.3,67))
route('USB_EN1',[(11.75,38.975),(11.75,62),(12,62.25),(12,69.5),(11.75,69.75),(11.75,75.225)],.15)
def front(net,ps):
 for a,z in zip(ps,ps[1:]):
  t=p.PCB_TRACK(b);t.SetStart(pt(a));t.SetEnd(pt(z));t.SetWidth(p.FromMM(.15));t.SetLayer(p.F_Cu);t.SetNet(b.FindNet(net));b.Add(t);rows.append(dict(uuid=t.m_Uuid.AsString(),net=net,type='track',a=a,z=z,width=.15,layer='F.Cu'))
front('CAM_IO_EN',[(11.15,62.65),(12.25,63.75),(12.25,68.25),(11.15,69.35)])
front('CAM_ISO_OE_N',[(10.75,63.5),(10.7,63.55),(10.7,66.45),(10.75,66.5)])
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(D/'mainboard_revD.kicad_pcb'),b)
(D/'new_routes.json').write_text(json.dumps(rows,indent=2))
