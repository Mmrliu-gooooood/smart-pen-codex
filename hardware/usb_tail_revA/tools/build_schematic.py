#!/usr/bin/env python3
"""2026-10-28 camera isolation new design, NO FAB. Editable native KiCad."""
import json,uuid
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def uid(): return str(uuid.uuid4())
def q(s): return json.dumps(str(s))
def eff(n=1): return f'(effects (font (size {n} {n})))'
lib={}; specs={}
def sym(name,pins,kind='box'):
    # pins: number,name,electrical type; split across left/right
    n=len(pins); left=(n+1)//2; rows=left; h=(rows+1)*2.54/2; w=15.24 if n>10 else 7.62
    lines=[f'(symbol {q(name)} (pin_names (offset 1.016)) (in_bom yes) (on_board yes)',f'(property "Reference" "U" (at 0 {h+3} 0) {eff()})',f'(property "Value" {q(name)} (at 0 {h+1.5} 0) {eff()})',f'(symbol {q(name+"_0_1")} (rectangle (start {-w} {h}) (end {w} {-h}) (stroke (width 0.254) (type default)) (fill (type background))))']
    # replace final close: primitive symbol closed only, parent remains
    # primitive symbol already closed
    coords={}; pp=[]
    for i,(num,pn,typ) in enumerate(pins):
        side=i<left; row=i if side else i-left; x=-w-2.54 if side else w+2.54; y=h-2.54-row*2.54; a=0 if side else 180
        coords[str(num)]=(x,y,a)
        pp.append(f'(pin {typ} line (at {x} {y} {a}) (length 2.54) (name {q(pn)} {eff(.9)}) (number {q(num)} {eff(.9)}))')
    lines.append(f'(symbol {q(name+"_1_1")} '+''.join(pp)+'))')
    lib[name]='\n'.join(lines);specs[name]=coords

root=uid(); allparts=[]
class Sheet:
 def __init__(self,name):self.name=name;self.id=uid();self.items=[];self.used=set()
 def text(self,s,x,y):self.items.append(f'(text {q(s)} (at {x} {y} 0) {eff(1.27)} (uuid {uid()}))')
 def part(self,name,ref,value,x,y,nets,foot='',dnp=False):
  x=round(x/1.27)*1.27;y=round(y/1.27)*1.27
  self.used.add(name);i=uid();z=[f'(symbol (lib_id "Pen:{name}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp {"yes" if dnp else "no"}) (uuid {i})',f'(property "Reference" {q(ref)} (at {x} {y-((len(specs[name])+2)//2)*1.27-5} 0) {eff()})',f'(property "Value" {q(value)} (at {x} {y-((len(specs[name])+2)//2)*1.27-3} 0) {eff()})',f'(property "Footprint" {q(foot)} (at {x} {y} 0) (effects (font (size 1 1)) hide))']
  for pn,(dx,dy,a) in specs[name].items():
   z.append(f'(pin {q(pn)} (uuid {uid()}))');px=x+dx;py=y-dy;net=nets.get(pn)
   if net is None:self.items.append(f'(no_connect (at {px} {py}) (uuid {uid()}))')
   else:
    ex=px-5.08 if a==0 else px+5.08
    self.items.append(f'(wire (pts (xy {px} {py}) (xy {ex} {py})) (stroke (width 0) (type default)) (uuid {uid()}))')
    self.items.append(f'(global_label {q(net)} (shape bidirectional) (at {ex} {py} {180 if a==0 else 0}) {eff(.9)[:-1]+(" (justify right))" if a==0 else " (justify left))")} (uuid {uid()}) (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {ex} {py} 0) (effects (font (size 1 1)) hide)))')
  z.append(f'(instances (project "usb_tail_revA" (path "/{root}/{self.id}" (reference {q(ref)}) (unit 1)))) )')
  self.items.append(''.join(z));allparts.append(dict(sheet=self.name,ref=ref,value=value,lib=name,nets=nets,footprint=foot,dnp=dnp))
 def save(self):
  out=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {self.id}) (paper "A3") (title_block (title "2026-10-28 REBUILD / NO FAB") (rev "R0")) (lib_symbols '+''.join(lib[k].replace('(symbol "'+k+'"','(symbol "Pen:'+k+'"',1) for k in self.used)+')'+''.join(self.items)+')'
  (P/(self.name+'.kicad_sch')).write_text(out)

usb=[('A1','GND'),('A4','VBUS'),('A5','CC1'),('A6','D+'),('A7','D-'),('A8','SBU1'),('A9','VBUS'),('A12','GND'),('B1','GND'),('B4','VBUS'),('B5','CC2'),('B6','D+'),('B7','D-'),('B8','SBU2'),('B9','VBUS'),('B12','GND'),('S1','SHIELD')]
sym('USB4105_GF_A',[(a,b,'passive') for a,b in usb])
sym('TPD4E05U06DQAR',[(str(i),n,'passive') for i,n in {1:'D1+',2:'D1-',3:'GND',4:'D2+',5:'D2-',6:'NC_ROUTE',7:'NC_ROUTE',8:'GND',9:'NC_ROUTE',10:'NC_ROUTE'}.items()])
sym('TPD1E10B06DYAR',[(1,'IO','passive'),(2,'GND','passive')])
sym('R',[(1,'1','passive'),(2,'2','passive')]);sym('WIRE_LAND',[(1,'WIRE','passive')])
a=Sheet('usb_entry')
a.text('USB TAIL RevA / NO FAB. R112/R113 remain on mainboard. No PD/current advertisement detection.',205,15)
n={pin:('GND' if signal in ['GND','SHIELD'] else 'VBUS_5V' if signal=='VBUS' else 'USB_DP' if signal=='D+' else 'USB_DM' if signal=='D-' else 'USB_'+signal if signal in ['CC1','CC2'] else None) for pin,signal in usb}
a.part('USB4105_GF_A','J101','USB4105-GF-A-120',75,65,n,'Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal')
a.part('TPD4E05U06DQAR','U102','TPD4E05U06DQAR',265,65,{str(k):v for k,v in {1:'USB_DP',2:'USB_DM',3:'GND',4:'USB_CC1',5:'USB_CC2',6:'USB_CC2',7:'USB_CC1',8:'GND',9:'USB_DM',10:'USB_DP'}.items()},'SmartPen:TI_DQA0010A_USON10_OfficialLandpattern')
a.part('TPD1E10B06DYAR','D101','TPD1E10B06DYAR',75,145,{'1':'VBUS_5V','2':'GND'},'SmartPen:TI_DYA0002A_SOD523_OfficialLandpattern')
for i,net in enumerate(['USB_CC1','USB_CC2']):a.part('R','R'+str(110+i),'5.1k 1%',200+i*100,145,{'1':net,'2':'GND'},'Resistor_SMD:R_0603_1608Metric')
for i,net in enumerate(['USB_DP','USB_DM','VBUS_5V','GND']):a.part('WIRE_LAND','TP'+str(101+i),net+'_INTERNAL_WIRE',55+i*95,205,{'1':net},'SmartPen:WireLand_1.5x2_NoPaste')
a.text('U102 NC 6/7/9/10 are optional straight-through PCB pads per TI; no internal chip connection assumed.',205,245)
a.text('Wire lands are real assembly interfaces requiring harness/strain relief qualification, NOT completed pen interconnects.',205,255)
a.text('J101 shell is grounded at all four S1 pads. Keep VBUS TVS/ESD ground paths short. USB100 default policy unchanged.',205,265)
a.save()
(P/'usb_tail_revA.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {root}) (paper "A4") (lib_symbols) (sheet (at 65 65) (size 120 45) (stroke (width 0.1524) (type default)) (fill (color 0 0 0 0)) (uuid {a.id}) (property "Sheetname" "usb_entry" (at 65 64 0) {eff()}) (property "Sheetfile" "usb_entry.kicad_sch" (at 65 112 0) {eff()}) (instances (project "usb_tail_revA" (path "/{root}" (page "2"))))))')
(P/'Pen.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor")'+''.join(lib.values())+')')
(P/'sym-lib-table').write_text('(sym_lib_table (lib (name "Pen") (type "KiCad") (uri "${KIPRJMOD}/Pen.kicad_sym") (options "") (descr "USB tail semantic interface")))')
(P/'fp-lib-table').write_text('(fp_lib_table (lib (name "SmartPen") (type "KiCad") (uri "${KIPRJMOD}/SmartPen.pretty") (options "") (descr "Qualified DYA plus real wire lands")))')
(P/'usb_tail_revA.kicad_pro').write_text('{}')
(P/'design_manifest.json').write_text(json.dumps(allparts,indent=2))
(P/'SmartPen.pretty/WireLand_1.5x2_NoPaste.kicad_mod').write_text('(footprint "WireLand_1.5x2_NoPaste" (version 20241229) (generator "pcbnew") (layer "F.Cu") (attr smd) (property "Reference" "TP?" (at 0 -1.7 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12)))) (property "Value" "WIRE" (at 0 1.7 0) (layer "F.Fab") (effects (font (size 0.7 0.7) (thickness 0.1)))) (fp_rect (start -1 -1.25) (end 1 1.25) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd")) (pad "1" smd roundrect (at 0 0) (size 1.5 2) (layers "F.Cu" "F.Mask") (roundrect_rratio 0.2)))')
print('Native USB tail source:9components, real wire interfaces, NO FAB')
