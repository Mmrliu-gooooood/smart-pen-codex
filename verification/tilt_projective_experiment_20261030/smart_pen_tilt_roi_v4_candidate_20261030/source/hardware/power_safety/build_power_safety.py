"""New camera power isolation proposal. Shared drawing helper adapted from our rebuilt power core; new circuit/tests."""
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
def label(n,pt,j='left'):
 if n=='CAM_PWR_EN' and not any('(hierarchical_label ' in g for g in graphics):
  graphics.append(f'(hierarchical_label {q(n)} (shape input) (at {pt[0]} {pt[1]} 0) (effects (font (size 1 1)) (justify left)) (uuid {uid()}))');return
 graphics.append(f'(label {q(n)} (at {pt[0]} {pt[1]} 0) (effects (font (size 1 1)) (justify {j} bottom)) (uuid {uid()}))')
def text(s,x,y,size=2.0):graphics.append(f'(text {q(s)} (at {x} {y} 0) (effects (font (size {size} {size})) (justify left top)) (uuid {uid()}))')
def pin(r,n):return pos[(r,str(n))]
def tps():
 s='(symbol "TPS22918" (pin_names (offset 0.8)) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 16 0) (effects (font (size 1.27 1.27)))) (property "Value" "TPS22918" (at 0 -16 0) (effects (font (size 1.27 1.27)))) (symbol "TPS22918_0_1" (rectangle (start -12.7 12.7) (end 12.7 -12.7) (stroke (width 0.254) (type default)) (fill (type background)))) (symbol "TPS22918_1_1" '
 pins=[('VIN','power_in',-17.78,7.62,0),('GND','power_in',0,-17.78,90),('ON','input',-17.78,-5.08,0),('CT','passive',10.16,-17.78,90),('QOD','passive',17.78,-5.08,180),('VOUT','power_out',17.78,7.62,180)]
 for i,(n,t,x,y,a) in enumerate(pins,1):s+=f'(pin {t} line (at {x} {y} {a}) (length 5.08) (name {q(n)} (effects (font (size 1 1)))) (number "{i}" (effects (font (size 1 1)))))'
 return s+'))'
def add(ref,val,library,name,x,y,nets,rot=0,manual=(),dnp=False):
 x,y=snap(x),snap(y)
 if name=='TPS22918':s=tps();name='TPS22918'
 else:
  s=extract(Path('/usr/share/kicad/symbols/'+library+'.kicad_sym').read_text(),name);new=library+'_'+name;s=s.replace(q(name),q(new)).replace('"'+name+'_','"'+new+'_');name=new
 lib[name]=s;rx,ry,vx,vy=x+5,y-2,x+5,y+2
 if ref.startswith('U'):rx,ry,vx,vy=x-10,y-23,x-10,y+23
 if rot in [90,270]:rx,ry,vx,vy=x,y-6,x,y+6
 if ref=='J1':rx,ry,vx,vy=x+5,y-7,x+5,y+8
 a=90 if rot in [90,270] else 0
 symbols.append(f'(symbol (lib_id "PowerSafety:{name}") (at {x} {y} {rot}) (unit 1) (in_bom {"no" if ref.startswith("#") else "yes"}) (on_board {"no" if ref.startswith("#") else "yes"}) (dnp {"yes" if dnp else "no"}) (uuid {uid()}) (property "Reference" {q(ref)} (at {rx} {ry} {a}) (effects (font (size 1.3 1.3)))) (property "Value" {q(val)} (at {vx} {vy} {a}) (effects (font (size 1.1 1.1)))) (property "Footprint" "" (at {x} {y} 0) (effects (font (size 1 1)) hide)) (instances (project "power_safety_NOFAB" (path "/{root}" (reference {q(ref)}) (unit 1)))))')
 parts.append(dict(ref=ref,value=val,footprint_status='UNASSIGNED',dnp=dnp))
 for pp in walk(parse(s),'pin'):
  n=un(fld(pp,'number')[1]);dx,dy,ang=map(float,fld(pp,'at')[1:]);r=math.radians(rot);pt=(round(x+dx*math.cos(r)-dy*math.sin(r),4),round(y-dx*math.sin(r)-dy*math.cos(r),4));pos[(ref,n)]=pt;ang=(ang+rot)%360;net=nets[n]
  if net is None:graphics.append(f'(no_connect (at {pt[0]} {pt[1]}) (uuid {uid()}))')
  elif n not in manual:
   end=(round(pt[0]-5.08*math.cos(math.radians(ang)),4),round(pt[1]+5.08*math.sin(math.radians(ang)),4));line(pt,end);label(net,end,'right' if ang==0 else 'left')

add('U1','TPS22918DBVR',None,'TPS22918',120,80,{'1':'3V3_AON','2':'GND','3':'CAM_ON','4':'CAM_CT','5':'CAM_QOD','6':'CAM_3V3_PRELINK'})
add('TP1','ENABLE MEASURE','Connector','TestPoint',65,55,{'1':'CAM_PWR_EN'})
add('C1','10uF 10V X7R','Device','C',35,75,{'1':'3V3_AON','2':'GND'})
add('C2','1uF 10V X7R','Device','C',180,75,{'1':'CAM_3V3_PRELINK','2':'GND'})
add('C3','1nF 25V C0G','Device','C',145,130,{'1':'CAM_CT','2':'GND'})
add('R1','100k 1%','Device','R',65,125,{'1':'CAM_ON','2':'GND'})
add('R2','1k 1%','Device','R',35,115,{'1':'CAM_PWR_EN','2':'CAM_ON'})
add('R3','100R 1%','Device','R',190,125,{'1':'CAM_3V3_PRELINK','2':'CAM_QOD'})
add('JP1','OPEN / DO NOT BRIDGE','Jumper','Jumper_2_Open',235,65,{'1':'CAM_3V3_PRELINK','2':'CAM_3V3_SW'},dnp=True)
add('J1','APPROVED LOAD / TBD','Connector_Generic','Conn_01x02',250,110,{'1':'CAM_3V3_SW','2':'GND'})
for r,y,n in [('#FLG01',60,'3V3_AON'),('#FLG02',80,'GND')]:add(r,'PWR_FLAG','power','PWR_FLAG',15,y,{'1':n})
text('相机供电门控候选 / NO FAB / 2026-10-28',15,13,2.5)
text('新设计，不是历史原件恢复。JP1开路；未批准的摄像头禁止接电。',15,22,1.5)
text('3V3_AON 输入；CAM_PWR_EN = GPIO41 候选；高有效，复位高阻由R1拉低。',15,32,1.4)
text('JP1是实物开路调试桥，不是软件开关；J1封装和线序待实际模块确认。',15,160,1.4)
text('CAM_3V3_SW仅用于已批准3.3V模块或下游调压器，绝非裸传感器所有电源。',15,167,1.4)
text('本器件不提供限流、过压或反灌保护；其他电源或I/O不得倒灌输出。',15,174,1.4)
text('上电前隔离I/O；关电前停XCLK/置复位并隔离I/O；禁止3.3V当1.8V VIO。',15,181,1.4)
text('CT定时与放电只作候选；实际负载、电容、浪涌、关断和掉电必须测试。',15,188,1.4)
content=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {root}) (paper "A4") (title_block (title "Camera power gate / NO FAB") (date "2026-10-28") (rev "NEW-P0")) (lib_symbols '+''.join(s.replace('(symbol '+q(n),'(symbol '+q('PowerSafety:'+n),1) for n,s in lib.items())+') '+''.join(graphics+symbols)+' (sheet_instances (path "/" (page "1"))))'
(P/'power_safety_NOFAB.kicad_sch').write_text(content)
(P/'PowerSafety.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") '+''.join(lib.values())+')')
(P/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "PowerSafety")(type "KiCad")(uri "${KIPRJMOD}/PowerSafety.kicad_sym")(options "")(descr "New NO FAB camera supply gate")))')
(P/'power_safety_NOFAB.kicad_pro').write_text('{}')
(P/'parts_unreleased.json').write_text(json.dumps(parts,indent=2)+'\n')
