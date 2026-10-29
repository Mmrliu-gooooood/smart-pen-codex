from pathlib import Path
import pcbnew as p,xml.etree.ElementTree as E,re,json,shutil
D=Path(__file__).resolve().parents[1];mm=p.FromMM;v=lambda x,y:p.VECTOR2I(mm(x),mm(y))
for n in [2,3]:
 name=f'WireLands_{n}_P2.5_AssemblyUnqualified';f=p.FOOTPRINT(None);f.SetReference('REF**');f.SetValue(name);f.SetFPID(p.LIB_ID('SmartPenIllum',name));f.SetAttributes(p.FP_SMD)
 for i in range(n):
  a=p.PAD(f);a.SetNumber(str(i+1));a.SetAttribute(p.PAD_ATTRIB_SMD);a.SetShape(p.PAD_SHAPE_RECT);a.SetPosition(v((i-(n-1)/2)*2.5,0));a.SetSize(v(1.4,2));ls=p.LSET();ls.AddLayer(p.F_Cu);ls.AddLayer(p.F_Mask);a.SetLayerSet(ls);f.Add(a)
 f.Reference().SetVisible(False);f.Value().SetVisible(False);p.PCB_IO_MGR.PluginFind(p.PCB_IO_MGR.KICAD_SEXP).FootprintSave(str(D/'SmartPenIllum.pretty'),f)
x=E.parse(D/'illumination_NOFAB.xml');b=p.BOARD();b.SetCopperLayerCount(2);b.GetDesignSettings().SetBoardThickness(mm(.8));nets={}
for n in x.findall('./nets/net'):
 z=p.NETINFO_ITEM(b,n.attrib['name']);b.Add(z)
 for a in n:nets[a.attrib['ref'],a.attrib['pin']]=z
root=re.search(r'\(uuid ([\w-]+)\)',(D/'illumination_NOFAB.kicad_sch').read_text())[1]
positions={'J1':(4,1.5,0),'J2':(4,13.5,0),'JP1':(1.8,4.5,-90),'R1':(1.8,10,-90),'R2':(5.5,4.5,180),'R3':(4.2,11.2,0),'Q1':(5,8,0)}
for c in x.findall('./components/comp'):
 r=c.attrib['ref'];lib,name=c.findtext('footprint').split(':');path=D/'SmartPenIllum.pretty' if lib=='SmartPenIllum' else Path('/usr/share/kicad/footprints')/(lib+'.pretty');f=p.FootprintLoad(str(path),name);assert f is not None,(lib,name);f.SetReference(r);f.SetValue(c.findtext('value'));f.SetFPID(p.LIB_ID(lib,name));f.SetPath(p.KIID_PATH('/'+root+'/'+c.findtext('tstamps').split()[0]));f.SetDNP(c.find("property[@name='dnp']") is not None);f.SetExcludedFromBOM(False);f.SetPosition(v(*positions[r][:2]));f.SetOrientationDegrees(positions[r][2]);f.Reference().SetVisible(False);f.Value().SetVisible(False);b.Add(f)
 for a in f.Pads():a.SetNet(nets[r,a.GetNumber()])
for a,z in [((0,0),(8,0)),((8,0),(8,15)),((8,15),(0,15)),((0,15),(0,0))]:
 t=p.PCB_SHAPE();t.SetShape(p.SHAPE_T_SEGMENT);t.SetStart(v(*a));t.SetEnd(v(*z));t.SetLayer(p.Edge_Cuts);t.SetWidth(mm(.05));b.Add(t)
p.SaveBoard(str(D/'illumination_NOFAB.kicad_pcb'),b)
pro=json.loads((D.parent/'power_core_layout_candidate/power_core_NOFAB.kicad_pro').read_text());pro['meta']['filename']='illumination_NOFAB.kicad_pro';pro['board']['design_settings']['rules']['min_copper_edge_clearance']=.5;assert not pro['board']['design_settings'].get('drc_exclusions',[]);(D/'illumination_NOFAB.kicad_pro').write_text(json.dumps(pro,indent=2));(D/'placement.json').write_text(json.dumps(positions,indent=2))
print([(f.GetReference(),[(a.GetNumber(),a.GetNetname(),p.ToMM(a.GetPosition().x),p.ToMM(a.GetPosition().y)) for a in f.Pads()]) for f in b.GetFootprints()])
