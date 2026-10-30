"""2026-10-28 new semantic illumination circuit, NO FAB."""
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
def add(ref,val,library,name,x,y,nets,rot=0,manual=(),dnp=False,footprint=""):
 x,y=snap(x),snap(y)
 s=extract(Path('/usr/share/kicad/symbols/'+library+'.kicad_sym').read_text(),name);new=library+'_'+name;s=s.replace(q(name),q(new)).replace('"'+name+'_','"'+new+'_');name=new
 lib[name]=s;rx,ry,vx,vy=x+5,y-2,x+5,y+2
 if ref.startswith('U'):rx,ry,vx,vy=x-10,y-23,x-10,y+23
 if ref.startswith('Q'):rx,ry,vx,vy=x+13,y-3,x+13,y+3
 if rot in [90,270]:rx,ry,vx,vy=x,y-6,x,y+6
 if ref.startswith('J'):rx,ry,vx,vy=x+5,y-7,x+5,y+8
 a=90 if rot in [90,270] else 0
 symbols.append(f'(symbol (lib_id "Illumination:{name}") (at {x} {y} {rot}) (unit 1) (in_bom {"no" if ref.startswith("#") else "yes"}) (on_board {"no" if ref.startswith("#") else "yes"}) (dnp {"yes" if dnp else "no"}) (uuid {uid()}) (property "Reference" {q(ref)} (at {rx} {ry} {a}) (effects (font (size 1.3 1.3)))) (property "Value" {q(val)} (at {vx} {vy} {a}) (effects (font (size 1.1 1.1)))) (property "Footprint" {q(footprint)} (at {x} {y} 0) (effects (font (size 1 1)) hide)) (instances (project "illumination_NOFAB" (path "/{root}" (reference {q(ref)}) (unit 1)))))')
 parts.append(dict(ref=ref,value=val,footprint_candidate=footprint,dnp=dnp))
 for pp in walk(parse(s),'pin'):
  n=un(fld(pp,'number')[1]);dx,dy,ang=map(float,fld(pp,'at')[1:]);r=math.radians(rot);pt=(round(x+dx*math.cos(r)-dy*math.sin(r),4),round(y-dx*math.sin(r)-dy*math.cos(r),4));pos[(ref,n)]=pt;ang=(ang+rot)%360;net=nets[n]
  if net is None:graphics.append(f'(no_connect (at {pt[0]} {pt[1]}) (uuid {uid()}))')
  elif n not in manual:
   end=(round(pt[0]-5.08*math.cos(math.radians(ang)),4),round(pt[1]+5.08*math.sin(math.radians(ang)),4));line(pt,end);label(net,end,'right' if ang==0 else 'left')
add('J1','HOST INTERNAL / MPN TBD','Connector_Generic','Conn_01x03',45,65,{'1':'3V3_AON','2':'GND','3':'ILLUM_STROBE'})
add('JP1','OPEN DNP / COMMISSION ONLY','Jumper','Jumper_2_Open',100,55,{'1':'3V3_AON','2':'LED_COMMISSIONED'},rot=90,dnp=True)
add('R1','330R 1% >=0.1W','Device','R',150,55,{'1':'LED_COMMISSIONED','2':'LED_A'},rot=90,footprint='Resistor_SMD:R_0603_1608Metric')
add('J2','LED A/K ONLY / MPN TBD','Connector_Generic','Conn_01x02',235,55,{'1':'LED_A','2':'LED_K'})
add('Q1','PMV30UN2','Transistor_FET','Q_NMOS_GSD',200,105,{'1':'LED_GATE','2':'GND','3':'LED_K'},footprint='Package_TO_SOT_SMD:SOT-23')
add('R2','1k 1%','Device','R',100,105,{'1':'ILLUM_STROBE','2':'LED_GATE'},rot=90,footprint='Resistor_SMD:R_0603_1608Metric')
add('R3','100k 1%','Device','R',145,130,{'1':'LED_GATE','2':'GND'},footprint='Resistor_SMD:R_0603_1608Metric')
text('2026-10-28 新增照明限流 / NO FAB',15,14,2.8)
text('独立LED端口，不是未知相机30pin连接器。JP1开路/DNP；先选光源并审查，再人工commission。',15,24,1.4)
text('3.0-3.6V regulated only. NO direct battery / VBUS. GPIO48 only; no extra GPIO.',15,32,1.3)
text('R1硬限流候选：3.6V、Rmin326.7R、LED短路时 <=11.02mA / <=39.67mW。',15,160,1.5)
text('不是恒流源，也不是光安全批准。光谱/辐射功率/视场/眼安全/LED额定尚未确定。',15,168,1.4)
text('复位/控制断开靠R3关断；瞬态栅耦合、上电和PWM脉宽仍需示波器测试。',15,176,1.4)
text('LEDSTROBE芯片1.8V与MCU GPIO48不得直接并联；本页只接受MCU侧语义输入。',15,184,1.4)
content=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {root}) (paper "A4") (title_block (title "独立照明驱动 / NO FAB") (date "2026-10-28") (rev "N0")) (lib_symbols '+''.join(s.replace('(symbol '+q(n),'(symbol '+q('Illumination:'+n),1) for n,s in lib.items())+') '+''.join(graphics+symbols)+' (sheet_instances (path "/" (page "1"))))'
(P/'illumination_NOFAB.kicad_sch').write_text(content)
(P/'Illumination.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") '+''.join(lib.values())+')')
(P/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Illumination")(type "KiCad")(uri "${KIPRJMOD}/Illumination.kicad_sym")(options "")(descr "New semantic LED driver; NO FAB")))')
(P/'illumination_NOFAB.kicad_pro').write_text('{}')
(P/'parts_unreleased.json').write_text(json.dumps(parts,indent=2)+'\n')
print('New semantic driver generated; not checked until verify.py runs')
