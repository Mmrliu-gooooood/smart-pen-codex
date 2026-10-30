#!/usr/bin/env python3
"""2026-10-28 rebuild, not restoration of lost 2026-10-27 files."""
import pathlib,uuid,json
P=pathlib.Path(__file__).resolve().parents[1]
def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'pickup-rebuild-20261028:'+s))
def q(s):return json.dumps(str(s))
root=uid('root'); comps=[]
def add(ref,val,pins,xy,fp='',names=None,types=None):
 comps.append(dict(ref=ref,value=val,pins={str(k):v for k,v in pins.items()},xy=xy,footprint=fp,names=names or {},types=types or {}))
V='3V3_AON';G='GND';SCL='AON_I2C_SCL';SDA='AON_I2C_SDA';I='PICKUP_INT_N';N='NIB_CONTACT_N'
add('U1','LIS2DW12TR',{1:SCL,2:V,3:V,4:SDA,5:G,6:G,7:G,8:G,9:V,10:V,11:None,12:I},(110,75),'Package_LGA:LGA-12_2x2mm_P0.5mm',{1:'SCL',2:'CS',3:'SA0',4:'SDA',5:'NC',6:'GND',7:'RES',8:'GND',9:'VDD',10:'VDDIO',11:'INT2',12:'INT1'},{1:'input',2:'input',3:'input',4:'bidirectional',5:'passive',6:'power_in',7:'passive',8:'power_in',9:'power_in',10:'power_in',11:'output',12:'output'})
for ref,val,a,b,xy in [('R1','10k 1%',V,SCL,(65,100)),('R2','10k 1%',V,SDA,(185,100)),('R3','100k 1%',V,N,(65,125)),('R4','1k 1%',N,'CONTACT',(185,125))]:add(ref,val,{1:a,2:b},xy,'Resistor_SMD:R_0603_1608Metric')
for ref,val,a,b,xy in [('C1','100n X7R',V,G,(65,150)),('C2','100n X7R',V,G,(185,140)),('C3','1u X7R',V,G,(65,175)),('C4','1n C0G',N,G,(185,160))]:add(ref,val,{1:a,2:b},xy,'Capacitor_SMD:C_0603_1608Metric')
add('J1','HOST INTERNAL PADS',{1:V,2:G,3:SCL,4:SDA,5:I,6:N},(45,65),'Pen:Host_6')
add('J2','DRY CONTACT PADS',{1:'CONTACT',2:G},(220,65),'Pen:Contact_2')
# Explicit external source flags, not dummy nets.
add('#FLG01','PWR_FLAG',{1:V},(175,65),'',types={1:'power_out'})
add('#FLG02','PWR_FLAG',{1:G},(175,85),'',types={1:'power_out'})
lib=[];instances=[];conn=[]
for c in comps:
 ref=c['ref'];x,y=[round(v/1.27)*1.27 for v in c['xy']]; ps=list(c['pins']); n=len(ps);half=(n+1)//2
 # Left half and right half, horizontal pins. Flag has no body.
 positions={p:((-12.7, ((half-1)/2-i)*2.54,0) if i<half else (12.7,((n-half-1)/2-(i-half))*2.54,180)) for i,p in enumerate(ps)}
 name='S_'+ref.replace('#','');body=''
 for p,(px,py,ang) in positions.items():
  typ=c['types'].get(int(p),'passive'); pn=c['names'].get(int(p),p)
  body+=f'(pin {typ} line (at {px} {py} {ang})(length 5.08)(name {q(pn)} (effects(font(size 1 1))))(number {q(p)} (effects(font(size 1 1)))))'
 h=max(3.81,half*1.27+1.27)
 lib.append(f'(symbol {q("Pen:"+name)} (pin_names(offset 0.5))(in_bom yes)(on_board yes)(property "Reference" {q(ref)} (at 0 {h+3} 0)(effects(font(size 1.27 1.27))))(property "Value" {q(c["value"])} (at 0 {h+1} 0)(effects(font(size 1.27 1.27))))(symbol {q(name+"_0_1")}(rectangle(start -7.62 {h})(end 7.62 {-h})(stroke(width 0.254)(type default))(fill(type background))))(symbol {q(name+"_1_1")}{body}))')
 inst=f'(symbol(lib_id {q("Pen:"+name)})(at {x} {y} 0)(unit 1)(in_bom {"no" if ref.startswith("#") else "yes"})(on_board {"no" if ref.startswith("#") else "yes"})(dnp no)(uuid {uid(ref)})'
 for prop,val,py in [('Reference',ref,y-h-4),('Value',c['value'],y-h-1.7),('Footprint',c['footprint'],y)]:
  inst+=f'(property {q(prop)} {q(val)} (at {x} {py} 0)(effects(font(size 1.27 1.27)){"(hide yes)" if prop=="Footprint" else ""}))'
 for p in ps:inst+=f'(pin {q(p)}(uuid {uid(ref+"pin"+p)}))'
 inst+=f'(instances(project "pickup_contact"(path "/{root}"(reference {q(ref)})(unit 1)))))';instances.append(inst)
 for p,(px,py,ang) in positions.items():
  ax=x+px;ay=y-py;net=c['pins'][p]
  if net is None:conn.append(f'(no_connect(at {ax} {ay})(uuid {uid(ref+p+"nc")}))');continue
  bx=ax+(-5.08 if px<0 else 5.08)
  conn.append(f'(wire(pts(xy {ax} {ay})(xy {bx} {ay}))(stroke(width 0)(type default))(uuid {uid(ref+p+"wire")}))')
  conn.append(f'(global_label {q(net)} (shape bidirectional) (at {bx} {ay} 0)(effects(font(size 1 1))(justify {"right" if px<0 else "left"} bottom))(uuid {uid(ref+p+"label")}))')
text='(kicad_sch(version 20250114)(generator "eeschema")(uuid '+root+')(paper "A4")(title_block(title "Pickup/contact - REBUILD 2026-10-28 NOFAB")(rev "R28"))(lib_symbols'+''.join(lib)+')'+''.join(conn+instances)+'(embedded_fonts no))'
(P/'pickup_contact.kicad_sch').write_text(text)
# Local symbol library names are unqualified outside schematic cache.
(P/'Pen.kicad_sym').write_text('(kicad_symbol_lib(version 20241209)(generator "kicad_symbol_editor")'+''.join(lib).replace('"Pen:S_','"S_')+')')
(P/'sym-lib-table').write_text('(sym_lib_table(lib(name "Pen")(type "KiCad")(uri "${KIPRJMOD}/Pen.kicad_sym")(options "")(descr "Rebuilt local symbols")))')
(P/'pickup_contact.kicad_pro').write_text(json.dumps({'meta':{'filename':'pickup_contact.kicad_pro','version':1},'net_settings':{'classes':[{'name':'Default','clearance':0.15,'track_width':0.2,'via_diameter':0.6,'via_drill':0.3}],'meta':{'version':3}}},indent=2))
(P/'design.json').write_text(json.dumps({'rebuild_date':'2026-10-28','components':comps},indent=2))
print('Built',len(comps),'symbols')

(P/'Pen.pretty').mkdir(exist_ok=True)
for name,n in [('Host_6',6),('Contact_2',2)]:
 pads=''.join(f'(pad "{i+1}" smd roundrect(at {i*1.5} 0)(size 1 2)(layers "F.Cu" "F.Mask")(roundrect_rratio 0.2))' for i in range(n))
 (P/'Pen.pretty'/f'{name}.kicad_mod').write_text(f'(footprint "{name}"(version 20241229)(generator "pcbnew")(layer "F.Cu")(attr smd)(fp_text reference "REF**"(at 0 -2)(layer "F.SilkS")(effects(font(size 0.8 0.8)(thickness 0.12))))(fp_text value "{name}"(at 0 2)(layer "F.Fab")(effects(font(size 0.8 0.8)(thickness 0.12)))){pads})')
(P/'fp-lib-table').write_text('(fp_lib_table(lib(name "Pen")(type "KiCad")(uri "${KIPRJMOD}/Pen.pretty")(options "")(descr "Internal solder pads")))')
