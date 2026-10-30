from pathlib import Path
import shutil,json,uuid,copy,hashlib,sys
from sexpr import *
D=Path(__file__).resolve().parents[1];ROOT=D.parents[1];OLD=D.parent/'camera_isolation_control_native_0628'/'native';N=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else D/'native'
def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'smartpen-schmitt0744/'+s))
if N.exists():raise RuntimeError('no overwrite')
shutil.copytree(OLD,N,ignore=shutil.ignore_patterns('*.kicad_pcb','*.kicad_prl'))
f=N/'schematic/controls_sccb.kicad_sch';s=parse(f.read_text());lib=child(s,'lib_symbols')
refset=[]
for sf in [N/'mainboard_revD.kicad_sch',*(N/'schematic').glob('*.kicad_sch')]:
 for c in children(parse(sf.read_text()),'symbol'):refset.append(val(prop(c,'Reference')[2]))
assert 'U205' not in refset and 'C209' not in refset
oldq=next(c for c in children(s,'symbol') if val(prop(c,'Reference')[2])=='Q201');s.remove(oldq)
# Three existing wires remain: old G -> A pin2; old S -> GND pin3; old D -> Y pin4.
name='SN74LVC1G14DCKR';fp='SmartPenIO:TI_DCK0005A_Schmitt_OfficialLand'
ls=parse(f'''(symbol "ISO:{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)
(property "Reference" "U" (at 0 11 0) (effects(font(size 1 1))))
(property "Value" "{name}" (at 0 9 0) (effects(font(size 1 1))))
(symbol "{name}_0_1" (rectangle(start -7.62 3.81)(end 7.62 -3.81)(stroke(width .254)(type default))(fill(type background)))
(text "Schmitt INV" (at 0 0 0)(effects(font(size .8 .8)))))
(symbol "{name}_1_1"
(pin no_connect line(at 0 7.62 270)(length 3.81)(name "NC"(effects(font(size .9 .9))))(number "1"(effects(font(size .9 .9)))))
(pin input line(at -10.16 1.27 0)(length 2.54)(name "A"(effects(font(size .9 .9))))(number "2"(effects(font(size .9 .9)))))
(pin power_in line(at -10.16 -1.27 0)(length 2.54)(name "GND"(effects(font(size .9 .9))))(number "3"(effects(font(size .9 .9)))))
(pin output inverted(at 10.16 1.27 180)(length 2.54)(name "Y"(effects(font(size .9 .9))))(number "4"(effects(font(size .9 .9)))))
(pin power_in line(at 10.16 -1.27 180)(length 2.54)(name "VCC"(effects(font(size .9 .9))))(number "5"(effects(font(size .9 .9)))))))''')
lib.append(ls)
library=parse((N/'schematic/ISO.kicad_sym').read_text());lsc=copy.deepcopy(ls);lsc[1]=q(name);library.append(lsc);(N/'schematic/ISO.kicad_sym').write_text(dump(library)+'\n')
hierarchy=val(child(child(child(oldq,'instances'),'project'),'path')[1]);uu=uid('U205');cu=uid('C209')
def instance(ref,value,foot,x,y,libid,ids):
 props=''.join(f'(property "{k}" {q(v)} (at {x} {y+dy} 0)(effects(font(size 1 1))'+(' hide' if k not in ['Reference','Value'] else '')+'))' for k,v,dy in [('Reference',ref,-10),('Value',value,-8),('Footprint',foot,0)])
 pins=''.join(f'(pin "{pn}"(uuid {uid(ref+".pin"+str(pn))}))' for pn in ids)
 return parse(f'(symbol(lib_id "{libid}")(at {x} {y} 0)(unit 1)(in_bom yes)(on_board yes)(dnp no)(uuid {uid(ref)}){props}{pins}(instances(project "mainboard_revD"(path "{hierarchy}"(reference "{ref}")(unit 1)))))')
s.append(instance('U205',name,fp,279.4,115.57,'ISO:'+name,range(1,6)))
s.append(instance('C209','100nF 16V X7R +/-10%','Capacitor_SMD:C_0402_1005Metric',350.52,115.57,'ISO:C',[1,2]))
def connection(name,x,y,dx):
 end=x+dx
 s.append(parse(f'(wire(pts(xy {x} {y})(xy {end} {y}))(stroke(width 0)(type default))(uuid {uid(name+str(x)+str(y)+"wire")}))'))
 angle=0 if dx>0 else 180;justify='left' if dx>0 else 'right'
 s.append(parse(f'(global_label "{name}"(shape bidirectional)(at {end} {y} {angle})(effects(font(size .9 .9))(justify {justify}))(uuid {uid(name+str(x)+str(y)+"label")})(property "Intersheetrefs" "${{INTERSHEET_REFS}}"(at {end} {y} 0)(effects(font(size 1 1)) hide)))'))
connection('3V3_AON',289.56,116.84,5.08)
s.append(parse(f'(no_connect(at 279.4 107.95)(uuid {uid("U205.NC")}))'))
connection('3V3_AON',340.36,115.57,-5.08);connection('GND',360.68,115.57,5.08)
for c in children(s,'symbol'):
 ref=val(prop(c,'Reference')[2]);mpn=None
 if ref=='R202':prop(c,'Value')[2]=q('10k 1%');mpn='RC0603FR-0710KL'
 if ref=='U205':
  mpn=name
  child(prop(c,'Reference'),'at')[2]='101.57'
  child(prop(c,'Value'),'at')[2]='103.57'
 if ref=='C209':mpn='C0402C104K4RACTU'
 if mpn:c.append(parse(f'(property "MPN_candidate" "{mpn}"(at 0 0 0)(effects(font(size 1 1)) hide))'))
for t in children(s,'text'):
 if 'Hardware-default disable' in t[1]:t[1]=q('EXPERIMENT ONLY: active Schmitt OE; stable AON, USB-JTAG only. JP201/JP202 OPEN. NOFAB/NOPOWER.')
f.write_text(dump(s)+'\n')
# Manufacturer example land, not generic KiCad SC70 footprint. Explicit NC pin1, no connected copper inference.
ft='''(footprint "TI_DCK0005A_Schmitt_OfficialLand" (version 20240108)(generator "source0744") (layer "F.Cu")
(descr "TI DCK0005A official example land .95x.4 row 2.2 pitch .65; experimental NOFAB") (attr smd)
(property "Reference" "U205"(at 0 -1.8 0)(layer "F.SilkS")(effects(font(size .7 .7)(thickness .1))))
(property "Value" "SN74LVC1G14DCKR"(at 0 1.8 0)(layer "F.Fab")(effects(font(size .7 .7)(thickness .1))))
(fp_rect(start -.7 -1.075)(end .7 1.075)(stroke(width .1)(type default))(layer "F.Fab"))
(fp_rect(start -1.85 -1.35)(end 1.85 1.35)(stroke(width .05)(type default))(layer "F.CrtYd"))
(fp_circle(center -.4 -.75)(end -.3 -.75)(stroke(width .1)(type default))(fill none)(layer "F.Fab"))
'''
for pin,x,y in [(1,-1.1,-.65),(2,-1.1,0),(3,-1.1,.65),(4,1.1,.65),(5,1.1,-.65)]:ft+=f'(pad "{pin}" smd rect(at {x} {y})(size .95 .4)(layers "F.Cu" "F.Paste" "F.Mask"))\n'
ft+=')\n';(N/'SmartPenIO.pretty/TI_DCK0005A_Schmitt_OfficialLand.kicad_mod').write_text(ft)
(N.parent/'handoff.json').write_text(json.dumps({'U205':{'uuid':uu,'path':hierarchy+'/'+uu,'reference':'U205','value':name,'footprint':fp,'pins':{'1':'NC','2':'ISO_GATE','3':'GND','4':'CAM_ISO_OE_N','5':'3V3_AON'}},'C209':{'uuid':cu,'path':hierarchy+'/'+cu,'reference':'C209','value':'100nF 16V X7R +/-10%','footprint':'Capacitor_SMD:C_0402_1005Metric','MPN_candidate':'C0402C104K4RACTU','pads':{'1':{'net':'3V3_AON','xy':[-.48,0],'size':[.56,.62]},'2':{'net':'GND','xy':[.48,0],'size':[.56,.62]}}},'R202':{'old':'100k 1%','new':'10k 1%','footprint':'Resistor_SMD:R_0603_1608Metric','MPN_candidate':'RC0603FR-0710KL'},'Q201':'removed; other instances unchanged'},indent=2)+'\n')
