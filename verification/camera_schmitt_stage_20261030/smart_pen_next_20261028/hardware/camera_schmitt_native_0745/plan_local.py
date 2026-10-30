from pathlib import Path
import os,json,sys,uuid
os.environ['XDG_CONFIG_HOME']='/tmp/schmitt0745'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1]
sys.path.insert(0,str(R/'hardware/camera_isolation_control_native_0628'));import geometry_native as g
b=g.b
removed=['25d6ed42-2d9c-4f3b-81eb-bcbe1f0c0974','ceade1d2-e098-4e3c-88a4-8761e307d2e3','580a1f8d-21e2-4634-bd4e-90d8e0e7fa13','bd4c6534-55ca-4f5c-85c0-d70111e3b924','bcaf1753-8f8d-40e3-8334-0b54250afff2','fee32339-f981-525b-8b40-7d1eccea4f23']
sys.path.insert(0,str(R/'hardware/pressure_pullup_revision_0318'));from materialize import children
source=(R/'hardware/camera_isolation_control_native_0628/native/mainboard_revD.kicad_pcb').read_text()
for a,z,block in reversed(list(children(source))):
 if (block.startswith(('(segment','(via'))and any(uid in block for uid in removed))or(block.startswith('(footprint')and '(property "Reference" "Q201"' in block):source=source[:a]+source[z:]
(D/'trimmed.kicad_pcb').write_text(source);b=p.LoadBoard(str(D/'trimmed.kicad_pcb'));g.b=b
u=p.FootprintLoad('/usr/share/kicad/footprints/Package_TO_SOT_SMD.pretty','SOT-353_SC-70-5');u.SetReference('U205');u.SetValue('SN74LVC1G14DCKR');u.SetPosition(g.V((3,69)))
b.Add(u)
net={1:'',2:'ISO_GATE',3:'GND',4:'CAM_ISO_OE_N',5:'3V3_AON'};pos={1:(1.9,68.35),2:(1.9,69),3:(1.9,69.65),4:(4.1,69.65),5:(4.1,68.35)}
for a in u.Pads():
 i=int(a.GetNumber());a.SetSize(g.V((.95,.4)));a.SetPosition(g.V(pos[i]));a.SetNetCode(b.GetNetcodeFromNetname(net[i]))
c=p.FootprintLoad('/usr/share/kicad/footprints/Capacitor_SMD.pretty','C_0402_1005Metric');c.SetReference('C209');c.SetPosition(g.V((5.55,68.85)));c.SetOrientationDegrees(270);b.Add(c)
for a in c.Pads():a.SetNetCode(b.GetNetcodeFromNetname('3V3_AON'if a.GetNumber()=='1'else'GND'))
g.old=list(b.GetTracks());g.pads=[a for f in b.GetFootprints()for a in f.Pads()];g.cache={}
items=[]
def seg(net,layer,points,w=.15):
 for a,z in zip(points,points[1:]):items.append(g.track(net,layer,a,z,w))
def via(net,xy,w=.45,drill=.2):
 t=g.via(net,xy);t.SetWidth(p.F_Cu,round(w*1e6));t.SetDrill(round(drill*1e6));items.append(t)
seg('ISO_GATE',p.F_Cu,[(1.9,69),(1.2,69),(1.2,70.8),(1.3,70.9)])
via('ISO_GATE',(1.3,70.9))
seg('ISO_GATE',p.In3_Cu,[(1.3,70.9),(1.3,67.6),(1.55,67.35)])
seg('GND',p.F_Cu,[(1.9,69.65),(1.9,70.35)],.3);via('GND',(1.9,70.35),.6,.3)
seg('CAM_ISO_OE_N',p.F_Cu,[(4.1,69.65),(4.6,70.15)])
seg('3V3_AON',p.F_Cu,[(2.2,66.8),(3.15,67.4),(4.1,68.35),(5.55,68.37)],.3);via('3V3_AON',(2.2,66.8),.6,.3)
seg('GND',p.F_Cu,[(5.55,69.33),(4.9,69.0)],.3);via('GND',(4.9,69.0),.6,.3)
errors=g.errors(items)
# Also check every new real pad vs all other copper with actual polygon + .15 guard (incl NC).
paderrors=[]
for f in [u,c]:
 for a in f.Pads():
  for other in g.old+g.pads+items:
   if other==a or(other.GetNetname()==a.GetNetname()and a.GetNetname()):continue
   for l in g.L:
    if a.IsOnLayer(l)and other.IsOnLayer(l):
     z=p.SHAPE_POLY_SET();z.BooleanIntersection(g.shape(a,l,150000),g.shape(other,l))
     if z.Area()>1:paderrors.append([f.GetReference()+'.'+a.GetNumber(),g.desc(other),other.GetNetname(),b.GetLayerName(l),z.Area()/1e12])
flat=[]
for i,t in enumerate(items):
 b.Add(t)
 flat.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'type':'via'if isinstance(t,p.PCB_VIA)else'track','layer':b.GetLayerName(t.GetLayer()),'a':list(g.xy(t))if isinstance(t,p.PCB_VIA)else[t.GetStart().x/1e6,t.GetStart().y/1e6],'b':[t.GetEnd().x/1e6,t.GetEnd().y/1e6],'width':(t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth())/1e6,'drill':t.GetDrillValue()/1e6 if isinstance(t,p.PCB_VIA)else None})
p.SaveBoard(str(D/'trial.kicad_pcb'),b)
result={'removed':removed,'new':flat,'new_pad_specs':{f.GetReference():[{'pin':a.GetNumber(),'xy':g.xy(a),'size':[a.GetSize().x/1e6,a.GetSize().y/1e6]}for a in f.Pads()]for f in[u,c]},'geometry_errors':errors,'pad_errors':paderrors,'note':'provisional footprint geometry only; not source/parity or courtyard approval'}
(D/'plan.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'geometry':errors,'pad':paderrors},indent=2))
