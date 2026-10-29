from pathlib import Path
import pcbnew as p,xml.etree.ElementTree as E,json,hashlib,math
D=Path(__file__).resolve().parents[1];x=E.parse(D/'illumination_NOFAB.xml');s=E.parse(D.parent/'illumination_driver/illumination_NOFAB.xml')
def nn(t):return {(n.attrib['ref'],n.attrib['pin']):a.attrib['name'] for a in t.findall('./nets/net') for n in a}
expected={('J1','1'):'/3V3_AON',('J1','2'):'/GND',('J1','3'):'/ILLUM_STROBE',('JP1','1'):'/3V3_AON',('JP1','2'):'/LED_COMMISSIONED',('R1','1'):'/LED_COMMISSIONED',('R1','2'):'/LED_A',('J2','1'):'/LED_A',('J2','2'):'/LED_K',('Q1','1'):'/LED_GATE',('Q1','2'):'/GND',('Q1','3'):'/LED_K',('R2','1'):'/ILLUM_STROBE',('R2','2'):'/LED_GATE',('R3','1'):'/LED_GATE',('R3','2'):'/GND'}
assert nn(x)==expected==nn(s)
a={c.attrib['ref']:c for c in x.findall('./components/comp')};o={c.attrib['ref']:c for c in s.findall('./components/comp')};assert len(a)==7
for r,c in a.items():assert c.findtext('value')==o[r].findtext('value');assert (c.find("property[@name='dnp']") is not None)==(o[r].find("property[@name='dnp']") is not None)
b=p.LoadBoard(str(D/'illumination_NOFAB.kicad_pcb'));assert len(b.GetFootprints())==7;pd={};fps=[]
for f in b.GetFootprints():
 r=f.GetReference();assert f.GetValue()==a[r].findtext('value');assert f.IsDNP()==(a[r].find("property[@name='dnp']") is not None)
 for z in f.Pads():pd[r,z.GetNumber()]=z.GetNetname()
 fps.append({'ref':r,'FPID':str(f.GetFPID().GetLibItemName()),'DNP':f.IsDNP(),'position_mm':[p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y)],'pad_geometry':[{'number':z.GetNumber(),'net':z.GetNetname(),'center_mm':[p.ToMM(z.GetPosition().x),p.ToMM(z.GetPosition().y)],'size_mm':[p.ToMM(z.GetSize().x),p.ToMM(z.GetSize().y)]} for z in f.Pads()]})
assert pd==expected
q=next(f for f in b.GetFootprints() if f.GetReference()=='Q1');assert {z.GetNumber():z.GetNetname() for z in q.Pads()}=={'1':'/LED_GATE','2':'/GND','3':'/LED_K'}
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):assert t.GetDrillValue()==p.FromMM(.3) and t.GetWidth(p.F_Cu)==p.FromMM(.6)
 else:assert t.GetWidth() in [p.FromMM(.2),p.FromMM(.25)]
assert b.GetCopperLayerCount()==2 and b.GetDesignSettings().GetBoardThickness()==p.FromMM(.8)
rmin=330*.99;report={'status':'PASS circuit unchanged and exact 16 pad-net/value/DNP checks','components':7,'pins':16,'footprints':fps,'board_mm':[8,15,.8],'layers':2,'I_short_max_mA_conditional':3.6/rmin*1000,'R1_max_mW_conditional':3.6**2/rmin*1000,'Q1_max_static_mW_load_line_bound_conditional':3.6**2/(4*rmin)*1000,'conditions':'Vrail<=3.6V; actual resistor>=326.7ohm; no bypass; static passive LED load with nonnegative Vf; excludes switching loss, TCR/aging, R1 short, optic safety. Not normal LED operating current.','pcb_sha256':hashlib.sha256((D/'illumination_NOFAB.kicad_pcb').read_bytes()).hexdigest()}
(D/'verification.json').write_text(json.dumps(report,indent=2));print(report['status'])
