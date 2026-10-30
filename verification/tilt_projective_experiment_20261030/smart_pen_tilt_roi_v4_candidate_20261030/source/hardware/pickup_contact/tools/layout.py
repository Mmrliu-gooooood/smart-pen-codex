#!/usr/bin/env python3
"""Fresh review layout. No production export."""
import pcbnew as b,json,pathlib,uuid
P=pathlib.Path(__file__).resolve().parents[1];data=json.loads((P/'design.json').read_text());bd=b.BOARD();bd.SetCopperLayerCount(2);bd.GetDesignSettings().SetBoardThickness(b.FromMM(.8));bd.GetDesignSettings().m_NetSettings.GetDefaultNetclass().SetClearance(b.FromMM(.15))
bd.GetDesignSettings().m_MinClearance=b.FromMM(.15);bd.GetDesignSettings().m_TrackMinWidth=b.FromMM(.15)
def pt(x,y):return b.VECTOR2I(b.FromMM(x),b.FromMM(y))
nets={}
for n in sorted({v for c in data['components'] for v in c['pins'].values() if v}):
 no=b.NETINFO_ITEM(bd,n);bd.Add(no);nets[n]=no
nc=b.NETINFO_ITEM(bd,'unconnected-(U1-INT2-Pad11)');bd.Add(nc)
loc={'U1':(6,8,0),'J1':(2.25,2.2,0),'J2':(5.25,18,0),'R1':(2.5,5,90),'R2':(9.5,5,90),'R3':(9.5,11,90),'R4':(9.5,14,90),'C1':(2.5,8,90),'C2':(6,5,0),'C3':(2.5,11,90),'C4':(6,14,0)}
for c in data['components']:
 if c['ref'].startswith('#'):continue
 lib,fp=c['footprint'].split(':');folder=P/'Pen.pretty' if lib=='Pen' else pathlib.Path('/usr/share/kicad/footprints')/(lib+'.pretty')
 f=b.FootprintLoad(str(folder),fp);f.SetReference(c['ref']);f.SetValue(c['value']);f.SetFPID(b.LIB_ID(lib,fp))
 path=b.KIID_PATH();path.push_back(b.KIID(str(uuid.uuid5(uuid.NAMESPACE_URL,'pickup-rebuild-20261028:root'))));path.push_back(b.KIID(str(uuid.uuid5(uuid.NAMESPACE_URL,'pickup-rebuild-20261028:'+c['ref']))));f.SetPath(path)
 x,y,a=loc[c['ref']];f.SetPosition(pt(x,y));f.SetOrientationDegrees(a);bd.Add(f)
 f.Reference().SetVisible(False);f.Value().SetVisible(False)
 for p in f.Pads():
  n=c['pins'].get(p.GetNumber());p.SetNet(nets[n] if n else nc)
 # assembly reference on fabrication
 t=b.PCB_TEXT(bd);t.SetText(c['ref']);t.SetPosition(pt(x,y-1.8));t.SetLayer(b.F_Fab);t.SetTextSize(pt(.8,.8));t.SetTextThickness(b.FromMM(.12));bd.Add(t)
for a,z in [((0,0),(12,0)),((12,0),(12,20)),((12,20),(0,20)),((0,20),(0,0))]:
 s=b.PCB_SHAPE();s.SetShape(b.SHAPE_T_SEGMENT);s.SetStart(pt(*a));s.SetEnd(pt(*z));s.SetLayer(b.Edge_Cuts);s.SetWidth(b.FromMM(.05));bd.Add(s)
for i in range(6):
 t=b.PCB_TEXT(bd);t.SetText(str(i+1));t.SetPosition(pt(2.25+1.5*i,.6));t.SetLayer(b.F_SilkS);t.SetTextSize(pt(.8,.8));t.SetTextThickness(b.FromMM(.12));bd.Add(t)
for txt,x in [('CT',5.25),('G',6.75)]:
 t=b.PCB_TEXT(bd);t.SetText(txt);t.SetPosition(pt(x,16.5));t.SetLayer(b.F_SilkS);t.SetTextSize(pt(.8,.8));t.SetTextThickness(b.FromMM(.1));bd.Add(t)
# Reserve no pours/vias under MEMS body. Pin escape traces still allowed.
for layer in (b.F_Cu,b.B_Cu):
 z=b.ZONE(bd);z.SetIsRuleArea(True);z.SetLayer(layer);z.SetDoNotAllowCopperPour(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowTracks(False);z.SetDoNotAllowPads(False);o=z.Outline();o.NewOutline()
 for x,y in [(5,7),(7,7),(7,9),(5,9)]:o.Append(b.FromMM(x),b.FromMM(y))
 bd.Add(z)
b.SaveBoard(str(P/'pickup_contact.kicad_pcb'),bd)
print('Saved placement; routing is separate')
