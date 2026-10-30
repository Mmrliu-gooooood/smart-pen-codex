import os,json,hashlib
from pathlib import Path
os.environ['XDG_CONFIG_HOME']='/tmp/contact_carrier'
import pcbnew as p
R=Path(__file__).resolve().parent;b=p.BOARD();b.GetDesignSettings().SetBoardThickness(p.FromMM(.8))
def layers(ids):
 s=p.LSET()
 for x in ids:s.AddLayer(x)
 return s
nets={}
for name in ['CONTACT','GND']:
 n=p.NETINFO_ITEM(b,name);b.Add(n);nets[name]=n
f=p.FOOTPRINT(b);f.SetReference('SW1');f.SetValue('SPVE110100_CONDITIONAL');f.SetPosition(p.VECTOR2I(p.FromMM(3.75),p.FromMM(3.4)));b.Add(f)
# Vendor recommended 1.2x.7 lands,3.05inner gap,1.5pairedpitch; view A.
for no,x,y,n in [('1',2.125,.75,'GND'),('2',2.125,-.75,'GND'),('3',-2.125,0,'CONTACT')]:
 q=p.PAD(f);q.SetNumber(no);q.SetAttribute(p.PAD_ATTRIB_SMD);q.SetShape(p.PAD_SHAPE_RECT);q.SetSize(p.VECTOR2I(p.FromMM(1.2),p.FromMM(.7)));q.SetLayerSet(layers([p.F_Cu,p.F_Paste,p.F_Mask]));q.SetPosition(p.VECTOR2I(p.FromMM(3.75+x),p.FromMM(3.4+y)));q.SetNet(nets[n]);f.Add(q)
fab=p.PCB_SHAPE(f);fab.SetShape(p.SHAPE_T_RECT);fab.SetStart(p.VECTOR2I(p.FromMM(2.25),p.FromMM(1.7)));fab.SetEnd(p.VECTOR2I(p.FromMM(5.25),p.FromMM(5.1)));fab.SetLayer(p.F_Fab);fab.SetWidth(p.FromMM(.05));f.Add(fab)
j=p.FOOTPRINT(b);j.SetReference('J1');j.SetValue('CONTACT_GND_FRONT_OBLIQUE_STUDY');b.Add(j)
for no,x,n in [('1',1.45,'CONTACT'),('2',6.05,'GND')]:
 q=p.PAD(j);q.SetNumber(no);q.SetAttribute(p.PAD_ATTRIB_SMD);q.SetShape(p.PAD_SHAPE_RECT);q.SetSize(p.VECTOR2I(p.FromMM(1.4),p.FromMM(1.2)));q.SetLayerSet(layers([p.F_Cu,p.F_Mask]));q.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(1.2)));q.SetNet(nets[n]);j.Add(q)
pts=[(0,0),(7.25,0),(7.25,.6),(7.5,.6),(7.5,6),(0,6)]
for a,c in zip(pts,pts[1:]+pts[:1]):
 s=p.PCB_SHAPE(b);s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(p.VECTOR2I(*(p.FromMM(v)for v in a)));s.SetEnd(p.VECTOR2I(*(p.FromMM(v)for v in c)));s.SetWidth(p.FromMM(.05));s.SetLayer(p.Edge_Cuts);b.Add(s)
for a,c,n in [((1.625,3.4),(1.45,1.2),'CONTACT'),((5.875,2.65),(6.05,1.2),'GND'),((5.875,4.15),(6.7,4.15),'GND'),((6.7,4.15),(6.7,2.65),'GND'),((6.7,2.65),(5.875,2.65),'GND')]:
 t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(*(p.FromMM(v)for v in a)));t.SetEnd(p.VECTOR2I(*(p.FromMM(v)for v in c)));t.SetWidth(p.FromMM(.25));t.SetLayer(p.F_Cu);t.SetNet(nets[n]);b.Add(t)
for fp in b.GetFootprints():
 fp.Reference().SetLayer(p.F_Fab);fp.Reference().SetVisible(True);fp.Value().SetLayer(p.F_Fab);fp.Value().SetVisible(False)
p.SaveBoard(str(R/'contact_carrier_NOFAB.kicad_pcb'),b)
# Reopen actual file and extract the actual pads, not copied design intent.
b=p.LoadBoard(str(R/'contact_carrier_NOFAB.kicad_pcb'));rows=[]
for f in b.GetFootprints():
 for q in f.Pads():
  x=q.GetPosition().x/1e6;y=q.GetPosition().y/1e6
  rows.append(dict(ref=f.GetReference(),pin=q.GetNumber(),net=q.GetNetname(),PCB_xy=[x,y],pen_front_XYZ=[x-3.75,-y-.4,78.4],pen_rear_XYZ=[x-3.75,-y-.4,79.2]))
(R/'carrier_contract.json').write_text(json.dumps(dict(status='MECHANICAL_CARRIER_PROPOSAL_NOFAB_NO_SYSTEM_SOURCE_INTEGRATION',native_sha256=hashlib.sha256((R/'contact_carrier_NOFAB.kicad_pcb').read_bytes()).hexdigest(),pads=rows,vendor_lands='ALPS2510 drawingNo1:1.2x.7,innergap3.05,pairpitch1.5',own_wire_pads='F-only1.4x1.2SMD hand-solderland,ownstudy notmanufacturer requirement',transform='penX=PCB_x-3.75;penY=-PCB_y-.4;FfrontZ78.4/Brear79.2 nominal',no_system_circuit_changed=True),indent=2)+'\n')
