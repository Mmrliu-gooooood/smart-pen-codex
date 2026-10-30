"""2026-10-28 authorized reconstruction, NOT recovery of yesterday's original files."""
from pathlib import Path
import json,re,uuid,math
P=Path(__file__).parent
uid=lambda:str(uuid.uuid4())
q=lambda x:json.dumps(str(x),ensure_ascii=False)
def extract(s,name):
 a=s.index('(symbol '+q(name));depth=0;quoted=False;escape=False
 for i in range(a,len(s)):
  c=s[i]
  if quoted:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quoted=False
  elif c=='"':quoted=True
  elif c=='(':depth+=1
  elif c==')':
   depth-=1
   if depth==0:return s[a:i+1]
def parse(s):
 stack=[];root=None
 for t in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s):
  if t=='(':
   x=[]
   if stack:stack[-1].append(x)
   else:root=x
   stack.append(x)
  elif t==')':stack.pop()
  else:stack[-1].append(t)
 return root
def fld(x,k):return next(z for z in x if isinstance(z,list) and z and z[0]==k)
def walk(x,k):
 if not isinstance(x,list):return []
 return ([x] if x and x[0]==k else [])+sum((walk(z,k) for z in x if isinstance(z,list)),[])
def un(x):return json.loads(x) if x.startswith('"') else x
def snap(x):return round(x/1.27)*1.27
root=uid();lib={};symbols=[];graphics=[];pos={};parts=[]
def line(a,b):
 if a!=b:graphics.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid {uid()}))')
def wire(*pts):
 for a,b in zip(pts,pts[1:]):line(a,b)
def label(n,pt,j='left'):graphics.append(f'(label {q(n)} (at {pt[0]} {pt[1]} 0) (effects (font (size 1 1)) (justify {j} bottom)) (uuid {uid()}))')
def text(s,x,y,size=2.0):graphics.append(f'(text {q(s)} (at {x} {y} 0) (effects (font (size {size} {size})) (justify left top)) (uuid {uid()}))')
def pin(r,n):return pos[(r,str(n))]
def tps():
 s='(symbol "TPS63802" (pin_names (offset 0.8)) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 16 0) (effects (font (size 1.27 1.27)))) (property "Value" "TPS63802" (at 0 -16 0) (effects (font (size 1.27 1.27)))) (symbol "TPS63802_0_1" (rectangle (start -12.7 12.7) (end 12.7 -12.7) (stroke (width 0.254) (type default)) (fill (type background)))) (symbol "TPS63802_1_1" '
 pins=[('EN','input',-17.78,2.54,0),('MODE','input',-17.78,-2.54,0),('AGND','power_in',-17.78,-7.62,0),('FB','input',17.78,2.54,180),('PG','open_collector',17.78,-7.62,180),('VOUT','power_out',17.78,7.62,180),('L2','passive',5.08,17.78,270),('GND','power_in',0,-17.78,90),('L1','passive',-5.08,17.78,270),('VIN','power_in',-17.78,7.62,0)]
 for i,(n,t,x,y,a) in enumerate(pins,1):s+=f'(pin {t} line (at {x} {y} {a}) (length 5.08) (name {q(n)} (effects (font (size 1 1)))) (number "{i}" (effects (font (size 1 1)))))'
 return s+'))'
def add(ref,val,library,name,x,y,nets,rot=0,manual=(),dnp=False):
 x,y=snap(x),snap(y)
 if name=='TPS63802':s=tps();name='TPS63802'
 else:
  s=extract(Path('/usr/share/kicad/symbols/'+library+'.kicad_sym').read_text(),name);new=library+'_'+name;s=s.replace(q(name),q(new)).replace('"'+name+'_','"'+new+'_');name=new
 lib[name]=s;rx,ry,vx,vy=x+5,y-2,x+5,y+2
 if ref.startswith('U'):rx,ry,vx,vy=x-10,y-23,x-10,y+23
 if rot in [90,270]:rx,ry,vx,vy=x,y-6,x,y+6
 if ref=='J1':rx,ry,vx,vy=x+5,y-7,x+5,y+8
 a=90 if rot in [90,270] else 0
 symbols.append(f'(symbol (lib_id "PowerCore:{name}") (at {x} {y} {rot}) (unit 1) (in_bom {"no" if ref.startswith("#") else "yes"}) (on_board {"no" if ref.startswith("#") else "yes"}) (dnp {"yes" if dnp else "no"}) (uuid {uid()}) (property "Reference" {q(ref)} (at {rx} {ry} {a}) (effects (font (size 1.3 1.3)))) (property "Value" {q(val)} (at {vx} {vy} {a}) (effects (font (size 1.1 1.1)))) (property "Footprint" "" (at {x} {y} 0) (effects (font (size 1 1)) hide)) (instances (project "power_core_NOFAB" (path "/{root}" (reference {q(ref)}) (unit 1)))))')
 parts.append(dict(ref=ref,value=val,footprint_status='UNASSIGNED',dnp=dnp))
 for pp in walk(parse(s),'pin'):
  n=un(fld(pp,'number')[1]);dx,dy,ang=map(float,fld(pp,'at')[1:]);r=math.radians(rot);pt=(round(x+dx*math.cos(r)-dy*math.sin(r),4),round(y-dx*math.sin(r)-dy*math.cos(r),4));pos[(ref,n)]=pt;ang=(ang+rot)%360;net=nets[n]
  if net is None:graphics.append(f'(no_connect (at {pt[0]} {pt[1]}) (uuid {uid()}))')
  elif n not in manual:
   end=(round(pt[0]-5.08*math.cos(math.radians(ang)),4),round(pt[1]+5.08*math.sin(math.radians(ang)),4));line(pt,end);label(net,end,'right' if ang==0 else 'left')
add('U1','BQ24074RGTR','Battery_Management','BQ24074RGT',95,75,{'1':'PACK_NTC','2':'PACK_PLUS_PROTECTED','3':'PACK_PLUS_PROTECTED','4':'CHARGE_DISABLE','5':'USB_EN2','6':'USB_EN1','7':None,'8':'GND','9':None,'10':'SYS_RAW','11':'SYS_RAW','12':'CHG_ILIM','13':'VBUS_5V','14':'CHG_TMR','15':None,'16':'CHG_ISET','17':'GND'},manual=['13','10','11','2','3','12','14','16'])
for r,v,x,y,n in [('C1','2.2uF 16V',70,45,'VBUS_5V'),('C2','10uF 10V',175,110,'PACK_PLUS_PROTECTED'),('C3','10uF 10V',135,85,'SYS_RAW')]:add(r,v,'Device','C',x,y,{'1':n,'2':'GND'},manual=['1'])
for r,v,x,n in [('R1','8.66k 1%',60,'CHG_ISET'),('R2','3.24k 1%',45,'CHG_ILIM'),('R3','68k 1%',30,'CHG_TMR')]:add(r,v,'Device','R',x,115,{'1':n,'2':'GND'},manual=['1'])
add('U2','TPS63802DLAR',None,'TPS63802',285,85,{'1':'SYS_RAW','2':'GND','3':'GND','4':'REG_FB','5':None,'6':'3V3_AON','7':'SW_L2','8':'GND','9':'SW_L1','10':'SYS_RAW'},manual=['1','4','6','7','9','10'])
add('L1','0.47uH / MPN TBD','Device','L',285,45,{'1':'SW_L1','2':'SW_L2'},rot=90,manual=['1','2'])
for r,v,x,y,n in [('C4','10uF 10V',235,80,'SYS_RAW'),('C5','22uF 6.3V',365,80,'3V3_AON'),('C6','22uF 6.3V',390,80,'3V3_AON')]:add(r,v,'Device','C',x,y,{'1':n,'2':'GND'},manual=['1'])
add('R7','511k 1%','Device','R',340,110,{'1':'3V3_AON','2':'REG_FB'},manual=['1','2'])
add('R8','91k 1%','Device','R',340,135,{'1':'REG_FB','2':'GND'},manual=['1'])
add('J1','NTC WIRES / MPN TBD','Connector_Generic','Conn_01x02',170,130,{'1':'PACK_NTC','2':'GND'})
add('R4','100k','Device','R',35,195,{'1':'USB_EN1','2':'GND'})
add('R5','100k','Device','R',80,195,{'1':'USB_EN2','2':'GND'})
add('R6','10k 1%','Device','R',150,175,{'1':'VBUS_5V','2':'CHARGE_DISABLE'},manual=['2'])
add('JP1','OPEN / DO NOT BRIDGE','Jumper','Jumper_2_Open',150,210,{'1':'CHARGE_DISABLE','2':'GND'},rot=270,manual=['1'],dnp=True)
for r,y,n in [('#FLG01',40,'VBUS_5V'),('#FLG02',55,'GND')]:add(r,'PWR_FLAG','power','PWR_FLAG',30,y,{'1':n})
a,b=pin('U1',13),pin('C1',1);y=snap(35);wire(a,(a[0],y),(b[0],y),b);label('VBUS_5V',(b[0],y))
for net,pn,c in [('SYS_RAW',10,'C3'),('PACK_PLUS_PROTECTED',2,'C2')]:
 a,b=pin('U1',pn),pin(c,1);wire(a,(b[0],a[1]),b);label(net,(b[0],a[1]))
for pn,r,n in [(14,'R3','CHG_TMR'),(12,'R2','CHG_ILIM'),(16,'R1','CHG_ISET')]:
 a,b=pin('U1',pn),pin(r,1);wire(a,(b[0],a[1]),b);label(n,(b[0],a[1]))
for pn,lp,n in [(9,1,'SW_L1'),(7,2,'SW_L2')]:
 a,b=pin('U2',pn),pin('L1',lp);wire(a,(a[0],b[1]),b);label(n,(a[0],b[1]))
a,b,c=pin('U2',10),pin('U2',1),pin('C4',1);x=snap(250);wire(a,(x,a[1]),(x,b[1]),b);wire((x,a[1]),(c[0],a[1]),c);label('SYS_RAW',(c[0],a[1]))
pts=[pin('U2',6),pin('C5',1),pin('C6',1),pin('R7',1)];y=snap(60)
for a in pts:wire(a,(a[0],y))
xs=sorted({a[0] for a in pts});wire(*[(x,y) for x in xs]);label('3V3_AON',(xs[0],y))
a,b,c=pin('R7',2),pin('R8',1),pin('U2',4);mid=(a[0],snap(122));wire(a,mid,b);wire(c,(snap(320),c[1]),(snap(320),mid[1]),mid);label('REG_FB',mid)
a,b=pin('R6',2),pin('JP1',1);wire(a,b);label('CHARGE_DISABLE',(a[0],snap(192)))
from collections import Counter
unique=set();new=[];counts=Counter()
for g in graphics:
 m=re.match(r'\(wire \(pts \(xy ([^ ]+) ([^)]+)\) \(xy ([^ ]+) ([^)]+)\)\)',g)
 if m:
  a=(float(m[1]),float(m[2]));b=(float(m[3]),float(m[4]));k=tuple(sorted((a,b)))
  if k in unique:continue
  unique.add(k);counts[a]+=1;counts[b]+=1
 new.append(g)
graphics=new
for pt,n in counts.items():
 if n>=3:graphics.append(f'(junction (at {pt[0]} {pt[1]}) (diameter 0) (color 0 0 0 0) (uuid {uid()}))')
text('2026-10-28 重建稿 / REBUILT - NO FAB - 禁止投板与连接未批准电池',15,15,3.0)
text('不是原件恢复；本次重新生成与检查。JP1保持开路，充电默认禁用；封装、电池、NTC和热设计未放行。',15,23,1.8)
text('1  电池电源路径 / POWER PATH',12,30,1.6);text('2  常供电升降压 / BUCK-BOOST',215,30,1.6)
text('J1: 外接真实NTC两线接口，型号/温度窗口/连接器待定。',12,145)
text('GND = 保护后PACK_MINUS；禁止连接裸CELL_MINUS绕过保护。',12,151)
text('3  专用GPIO接口 / 调试充电跳线',12,162,1.6)
text('USB_EN1 -> MCU GPIO18；USB_EN2 -> GPIO21；禁止复用UART。',12,230)
text('复位默认LOW/LOW=USB100；休眠/枚举/来源授权仍需系统验证。',12,237)
text('JP1为物理开路跳线，未批准电池/NTC前禁止短接。',12,244)
text('R1=8.66k: 91.12-113.73mA；R2=3.24k: 最坏536.23mA。',12,251)
text('R2不是500mA硬上限；CE支路电流也必须计入USB总电流。',12,258)
text('511k/91k -> 3.3077V标称；纹波/偏置/负载阶跃尚未测试。',215,160)
text('COUT有效容量与电感饱和/DCR需按实际器件和布局核验。',215,167)
text('所有封装未指定；本子项目无PCB、Gerber或可制造性声明。',215,174)
text('RELEASE BLOCKERS / 未放行项目',215,191,1.6)
for i,s in enumerate(['仅验证过的5V输入；USB-C/ESD/OVP在外部。','VBUS_5V / 3V3_AON / USB_EN1 / USB_EN2为统一逻辑网名。','充电电压容差、NTC故障与温度边界、保护电池待验证。','CE内部约285k下拉：JP1开路也有VBUS偏置电流。','JP1闭合时R6约0.5mA，不受充电器输入限流覆盖。','转换器低压能力不等于正常电池放电截止；策略待定。','本次ERC仅检查连接，不批准电池充电或生产。']):text(s,215,201+i*7)
content=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {root}) (paper "A3") (title_block (title "电源核心重建稿 / NO FAB") (date "2026-10-28") (rev "REBUILD-P0") (comment 1 "非原件恢复；充电禁用；未批准生产")) (lib_symbols '+''.join(s.replace('(symbol '+q(n),'(symbol '+q('PowerCore:'+n),1) for n,s in lib.items())+') '+''.join(graphics+symbols)+' (sheet_instances (path "/" (page "1"))))'
(P/'power_core_NOFAB.kicad_sch').write_text(content)
(P/'PowerCore.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") '+''.join(lib.values())+')')
(P/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "PowerCore")(type "KiCad")(uri "${KIPRJMOD}/PowerCore.kicad_sym")(options "")(descr "2026-10-28 reconstruction; not restored original")))')
(P/'power_core_NOFAB.kicad_pro').write_text('{}')
(P/'parts_unreleased.json').write_text(json.dumps(parts,indent=2)+'\n')
print('REBUILT new files; new UUIDs; no old check results reused')
