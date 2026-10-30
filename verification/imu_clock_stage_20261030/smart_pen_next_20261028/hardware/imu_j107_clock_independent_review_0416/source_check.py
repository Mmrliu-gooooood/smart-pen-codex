from pathlib import Path
import re,json,hashlib,copy,xml.etree.ElementTree as E,csv,collections
D=Path(__file__).resolve().parent;R=D.parents[1];S=R/'hardware/imu_j107_clock_native_0405';B=R/'hardware/pressure_pullup_revision_0318/native'
def req(x,m):
 if not x:raise RuntimeError(m)
def parse(s):
 stack=[];root=[]
 for t in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s):
  if t=='(':
   n=[];(stack[-1]if stack else root).append(n);stack.append(n)
  elif t==')':stack.pop()
  else:stack[-1].append(json.loads(t)if t.startswith('"')else t)
 req(not stack and len(root)==1,'parse');return root[0]
def prop(n,key):return next((x for x in n if isinstance(x,list)and x[:2]==['property',key]),None)
def child(n,key):return next((x for x in n if isinstance(x,list)and x and x[0]==key),None)

def norm(tree,old):
 out=[]
 for n in tree:
  if not isinstance(n,list):out.append(n);continue
  if n and n[0]in ['segment','via','arc']:continue
  if n and n[0]=='zone':n=[x for x in n if not isinstance(x,list)or not x or x[0]!='filled_polygon']
  if n and n[0]=='footprint':
   ref=prop(n,'Reference')[2]
   if ref=='J107':
    at=child(n,'at');req(at[1:]==(['3.2','84','180']if old else['5.2','84','180']),'J107 exact');at[1]='5.2'
   if ref=='R503':
    req(prop(n,'Value')[2]=='47k 1%'and prop(n,'MPN')[2]=='RC0603FR-0747KL','R503 retained');mp=prop(n,'MPN');n=[x for x in n if x is not mp]+[mp]
  out.append(n)
 return out
req(norm(parse((B/'mainboard_revD.kicad_pcb').read_text()),True)==norm(parse((S/'native/mainboard_revD.kicad_pcb').read_text()),False),'no hidden PCB noncopper change')
for f in B.rglob('*'):
 if f.is_file()and f.name!='mainboard_revD.kicad_pcb':req(f.read_bytes()==(S/'native'/f.relative_to(B)).read_bytes(),'other source file')
r=E.parse(D/'checks/candidate/netlist.xml').getroot();old=E.parse(D/'checks/base/netlist.xml').getroot()
for tag in ['nets','libparts','components']:req(E.tostring(r.find(tag))==E.tostring(old.find(tag)),'source netlist '+tag)
rows=[]
for n in r.find('nets'):
 for x in n.findall('node'):
  if x.get('ref')=='U501':rows.append({'net':n.get('name'),**x.attrib})
contract={'2':('CS','3V3_AON'),'3':('SA0','3V3_AON'),'5':('NC','GND'),'6':('GND','GND'),'7':('RES','GND'),'8':('GND','GND'),'9':('VDD','3V3_AON'),'10':('VDDIO','3V3_AON')}
for pin,(func,net)in contract.items():req(any(x['pin']==pin and x['pinfunction']==func and x['net']==net for x in rows),'embedded IMU contract')
print(json.dumps({'source_unchanged_except_J107_pose_and_R503_serialization':True,'netlist_exact':True,'U501_actual_source':rows},indent=2))
