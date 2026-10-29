#!/usr/bin/python3
from pathlib import Path
import pcbnew as p,xml.etree.ElementTree as E,re,json
D=Path(__file__).resolve().parents[1];xml=E.parse(D/'power_core_NOFAB.xml');b=p.BOARD();b.SetCopperLayerCount(4);b.GetDesignSettings().SetBoardThickness(p.FromMM(.8));mm=p.FromMM
v=lambda x,y:p.VECTOR2I(mm(x),mm(y))
netmap={}
for n in xml.findall('./nets/net'):
 ni=p.NETINFO_ITEM(b,n.attrib['name']);b.Add(ni)
 for a in n:netmap[a.attrib['ref'],a.attrib['pin']]=ni
root=re.search(r'\(uuid ([\w-]+)\)',(D/'power_core_NOFAB.kicad_sch').read_text())[1]
placements={'U1':(6,8,0),'C1':(8.7,4.8,0),'C2':(2,8,180),'C3':(10,8,0),'R1':(2.2,4.8,0),'R2':(10,11.2,0),'R3':(5.2,4.8,0),'R4':(6.3,11.2,0),'R5':(3.2,11.2,0),'R6':(2.2,3.2,0),'JP1':(10.4,17.7,90),'J1':(9,14,0),'J2':(8.5,1.8,0),'J4':(3,14,0),'U2':(6,23,90),'L1':(6,19.2,0),'C4':(2,22.6,180),'C5':(10,22.6,0),'C6':(10,25,0),'R7':(7.4,26,90),'R8':(4.6,26,90),'J3':(6,29.4,0),'J5':(6,33.1,0)}
checks=[]
for c in xml.findall('./components/comp'):
 ref=c.attrib['ref'];fpname=c.findtext('footprint')
 if not fpname:continue
 lib,name=fpname.split(':');path=D/'SmartPenPower.pretty' if lib=='SmartPenPower' else Path('/usr/share/kicad/footprints')/(lib+'.pretty')
 fp=p.FootprintLoad(str(path),name);assert fp is not None,(ref,fpname);fp.SetReference(ref);fp.SetValue(c.findtext('value'));fp.SetFPID(p.LIB_ID(lib,name));fp.SetDNP(c.find("property[@name='dnp']") is not None);fp.SetExcludedFromBOM(False)
 stamp=c.find('tstamps').text.split()[0];fp.SetPath(p.KIID_PATH('/'+root+'/'+stamp));x,y,a=placements[ref];fp.SetPosition(v(x,y));fp.SetOrientationDegrees(a);b.Add(fp)
 fp.Reference().SetVisible(False);fp.Value().SetVisible(False)
 for pad in fp.Pads():pad.SetNet(netmap[ref,pad.GetNumber()]);checks.append((ref,pad.GetNumber(),pad.GetNetname()))
for a,z in [((0,0),(12,0)),((12,0),(12,35)),((12,35),(0,35)),((0,35),(0,0))]:
 s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(v(*a));s.SetEnd(v(*z));s.SetLayer(p.Edge_Cuts);s.SetWidth(mm(.05));b.Add(s)
p.SaveBoard(str(D/'power_core_NOFAB.kicad_pcb'),b)
source=D/'rules_template.json';pro=json.loads(source.read_text());pro['meta']['filename']='power_core_NOFAB.kicad_pro';pro['board']['design_settings']['rules']['min_copper_edge_clearance']=.5;assert not pro['board']['design_settings'].get('drc_exclusions',[])
(D/'power_core_NOFAB.kicad_pro').write_text(json.dumps(pro,indent=2));(D/'placement_contract.json').write_text(json.dumps({'placements':placements,'actual_pad_map':checks,'board_mm':[12,35,.8],'stage':'PLACEMENT ONLY; no operational/thermal claim'},indent=2));print('Placed',len(placements),'parts;',len(checks),'pad shapes')
