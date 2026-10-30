from pathlib import Path
import os,json,math,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/mcu-independent0124'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];S=R/'hardware/sens_tree_candidate_0158';B=R/'hardware/translator_domain_candidate_0130'
L=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu];uid=lambda x:x.m_Uuid.AsString()
def need(c,m):
 if not c:raise RuntimeError(m)
def disk(x,r):
 q=p.SHAPE_POLY_SET();q.NewOutline();v=x.GetPosition()
 for k in range(512):q.Append(round(v.x+r*math.cos(k*math.tau/512)),round(v.y+r*math.sin(k*math.tau/512)))
 return q
def poly(x,l):
 q=p.SHAPE_POLY_SET();x.TransformShapeToPolygon(q,l,0,100,p.ERROR_INSIDE)
 if isinstance(x,p.PCB_VIA):q.BooleanSubtract(disk(x,x.GetDrillValue()/2))
 return q
def graph(b,net):
 nodes=[]
 for f in b.GetFootprints():
  for pad in f.Pads():
   if pad.GetNetname()==net:nodes.append((uid(pad),f.GetReference()+'.'+pad.GetNumber(),{l:poly(pad,l)for l in L if pad.IsOnLayer(l)}))
 for t in b.GetTracks():
  if t.GetNetname()==net:nodes.append((uid(t),None,{l:poly(t,l)for l in L if t.IsOnLayer(l)}))
 for z in b.Zones():
  if z.GetIsRuleArea()or z.GetNetname()!=net:continue
  for l in L:
   if z.IsOnLayer(l):
    q=z.GetFilledPolysList(l)
    for k in range(q.OutlineCount()):nodes.append((uid(z)+':'+str(l)+':'+str(k),None,{l:q.UnitSet(k)}))
 adj={n[0]:set()for n in nodes}
 for i,(u,_,a)in enumerate(nodes):
  for v,_,b in nodes[:i]:
   for l in set(a)&set(b):
    if not a[l].BBox().Intersects(b[l].BBox()):continue
    q=p.SHAPE_POLY_SET();q.BooleanIntersection(a[l],b[l])
    if q.Area()>10:adj[u].add(v);adj[v].add(u);break
 return nodes,adj
def reach(adj,start,omit=set()):
 seen={start};todo=[start]
 while todo:
  for q in adj[todo.pop()]-seen-omit:seen.add(q);todo.append(q)
 return seen
b=p.LoadBoard(str(S/'native/mainboard_revD.kicad_pcb'));base=p.LoadBoard(str(B/'native/mainboard_revD.kicad_pcb'));m=json.loads((S/'materialization.json').read_text())
results={};graphs={}
for net,core,want in [('3V3_AON','J106.2',23),('GND','J106.3',57),('SENS_VIO_1V8','J202.23',12)]:
 ns,adj=graph(b,net);graphs[net]=(ns,adj);root=next(u for u,n,_ in ns if n==core);rr=reach(adj,root);pads=[{'uuid':u,'name':n}for u,n,_ in ns if n and u in rr];need(len(pads)==want,'physical core count '+net);results[net]={'connected':pads,'total':sum(n is not None for _,n,_ in ns)}
pairs=[('3V3_AON','U201.1','C201.1'),('SENS_VIO_1V8','U201.23','C202.1'),('SENS_VIO_1V8','U201.24','C202.1'),('3V3_AON','U202.1','C203.1'),('SENS_VIO_1V8','U202.16','C204.1'),('3V3_AON','U203.1','C205.1'),('SENS_VIO_1V8','U203.16','C206.1'),('3V3_AON','U204.8','C207.1'),('SENS_VIO_1V8','U204.1','C208.1')]
for net,start,end in pairs:
 ns,adj=graphs[net];u=next(u for u,n,_ in ns if n==start);v=next(u for u,n,_ in ns if n==end);need(v in reach(adj,u),'local pair '+start)
results['nine_local_bypass_pairs']=pairs
fp={f.GetReference():f for f in b.GetFootprints()};ofp={f.GetReference():f for f in base.GetFootprints()};need(set(fp)==set(ofp)and len(fp)==102,'footprints')
# PAD.GetPinFunction is blank in this manually generated board. Resolve the real embedded schematic library instead.
import re
def sexpr(text):
 toks=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',text);stack=[];root=[]
 for t in toks:
  if t=='(':
   n=[]
   if stack:stack[-1].append(n)
   else:root.append(n)
   stack.append(n)
  elif t==')':stack.pop()
  else:stack[-1].append(json.loads(t)if t.startswith('"')else t)
 need(not stack and len(root)==1,'schematic parse');return root[0]
def child(n,key):return next((x for x in n if isinstance(x,list)and x and x[0]==key),None)
def walk(n):
 if isinstance(n,list):
  yield n
  for x in n:
   if isinstance(x,list):yield from walk(x)
libfunc={};libtype={}
for sch in (S/'native/schematic').glob('*.kicad_sch'):
 tree=sexpr(sch.read_text());libs=child(tree,'lib_symbols')
 if not libs:continue
 libmap={x[1]:x for x in libs[1:]if isinstance(x,list)and x and x[0]=='symbol'}
 for node in tree:
  if not isinstance(node,list)or not node or node[0]!='symbol':continue
  lid=child(node,'lib_id');ref=next((x[2]for x in node if isinstance(x,list)and len(x)>2 and x[:2]==['property','Reference']),None)
  if ref not in ['U201','U202','U203','U204','J202','R242','R243']or not lid:continue
  for pn in walk(libmap[lid[1]]):
   if pn and pn[0]=='pin'and child(pn,'number')and child(pn,'name'):libfunc[(ref,child(pn,'number')[1])]=child(pn,'name')[1];libtype[(ref,child(pn,'number')[1])]=pn[1]
contract=[('U201','1','VCCA','3V3_AON'),('U201','23','VCCB','SENS_VIO_1V8'),('U201','24','VCCB','SENS_VIO_1V8'),('U202','1','VCCA','3V3_AON'),('U202','16','VCCB','SENS_VIO_1V8'),('U203','1','VCCA','3V3_AON'),('U203','16','VCCB','SENS_VIO_1V8'),('U204','8','VCCB','3V3_AON'),('U204','1','VCCA','SENS_VIO_1V8')];rows=[]
for ref,pin,func,net in contract:
 pad=next(q for q in fp[ref].Pads()if q.GetNumber()==pin);need(pad.GetNetname()==net,'domain net');need(libfunc[(ref,pin)]==func,'schematic pin function '+ref+pin);rows.append({'ref':ref,'pin':pin,'function':libfunc[(ref,pin)],'net':net,'source':'embedded schematic library; PCB PAD pin-function field is empty'})
results['native_pin_function_domain_contract']=rows
for ref,f in fp.items():
 old=ofp[ref];need(uid(f)==uid(old)and f.GetValue()==old.GetValue()and str(f.GetFPID().GetLibItemName())==str(old.GetFPID().GetLibItemName())and f.GetLayer()==old.GetLayer()and f.GetOrientationDegrees()==old.GetOrientationDegrees(),'FP metadata')
 need(f.GetPosition()==old.GetPosition(),'all FP pose')
 op={uid(q):q for q in old.Pads()};np={uid(q):q for q in f.Pads()};need(set(op)==set(np),'pad ids')
 for u,q in np.items():
  z=op[u];need(q.GetNetname()==z.GetNetname()and q.GetNumber()==z.GetNumber()and q.GetPinFunction()==z.GetPinFunction()and q.GetLayerSet().FmtHex()==z.GetLayerSet().FmtHex()and q.GetSize()==z.GetSize(),'pad identity')
sig=lambda t:(t.GetClass(),t.GetNetname(),t.GetLayerSet().FmtHex(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None)
t={uid(x):x for x in b.GetTracks()};bt={uid(x):x for x in base.GetTracks()};need(set(bt)-set(t)==set(m['removed'])and set(t)-set(bt)==set(m['added']),'exact set');need(all(sig(t[u])==sig(x)for u,x in bt.items()if u not in m['removed']),'retained copper');need(len(t)==773,'count');results['retained_copper']=len(bt)-len(m['removed'])
# Independent SENS versus each other supply/ground, all real copper layers.
cross=[]
for net in ['3V3_AON','GND','CAM_3V3_SW']:
 other=graphs[net][0]if net in graphs else graph(b,net)[0]
 for u,_,a in other:
  for v,_,c in graphs['SENS_VIO_1V8'][0]:
   for l in set(a)&set(c):
    if not a[l].BBox().Intersects(c[l].BBox()):continue
    q=p.SHAPE_POLY_SET();q.BooleanIntersection(a[l],c[l])
    if q.Area()>10:cross.append([net,u,v,b.GetLayerName(l),q.Area()/1e12])
need(not cross,'domain copper short');results['SENS_other_rail_overlap']=cross
via_hits=[];count=0
for u in m['added']:
 v=t[u]
 if not isinstance(v,p.PCB_VIA):continue
 count+=1
 for f in b.GetFootprints():
  for pad in f.Pads():
   for l in L:
    if not pad.IsOnLayer(l):continue
    q=poly(pad,l);a=p.SHAPE_POLY_SET();a.BooleanIntersection(q,poly(v,l));h=p.SHAPE_POLY_SET();h.BooleanIntersection(q,disk(v,v.GetDrillValue()/2))
    if a.Area()>10 or h.Area()>10:via_hits.append([u,f.GetReference(),pad.GetNumber(),pad.GetNetname(),b.GetLayerName(l),a.Area()/1e12,h.Area()/1e12])
need(count==7 and not via_hits,'via/pad collision');results['new_vias_checked']=count;results['same_and_foreign_pad_hits']=via_hits
# Controlled same-net geometry fault must be observable, regardless of native same-net DRC behavior.
v=next(t[u]for u in m['added']if isinstance(t[u],p.PCB_VIA)and t[u].GetNetname()=='SENS_VIO_1V8');oldpos=p.VECTOR2I(v.GetPosition());target=next(q for q in fp['C202'].Pads()if q.GetNumber()=='1');v.SetPosition(target.GetPosition());h=p.SHAPE_POLY_SET();h.BooleanIntersection(poly(target,p.F_Cu),disk(v,v.GetDrillValue()/2));need(h.Area()>1e6,'same net drill injected detection');results['same_net_pad_drill_fault_detected_mm2']=h.Area()/1e12;v.SetPosition(oldpos)
ns,adj=graphs['SENS_VIO_1V8'];root=next(u for u,n,_ in ns if n=='J202.23');rr=reach(adj,root,set(m['added']));names={n for u,n,_ in ns if n and u in rr};need(names=={'J202.23'},'delete37 isolates external input');results['delete37_core']=sorted(names)
expected={'J202.23','U201.23','U201.24','U202.16','U203.16','U204.1','C202.1','C204.1','C206.1','C208.1','R242.2','R243.2'}
actual={x['name']for x in results['SENS_VIO_1V8']['connected']};need(actual==expected,'exact12 physical pads');results['external_reference_only_contract']='J202.23 is passive connector, not local voltage source; capacity and sequence unqualified'
for f in ['mainboard_revD.kicad_pro','mainboard_revD.kicad_dru','mainboard_revD.kicad_sch']:need((S/'native'/f).read_bytes()==(B/'native'/f).read_bytes(),'source/rules')
pullups={}
for ref in ['R242','R243','J202']:
 pullups[ref]=[{'pin':q.GetNumber(),'net':q.GetNetname(),'embedded_name':libfunc.get((ref,q.GetNumber())),'embedded_type':libtype.get((ref,q.GetNumber()))}for q in fp[ref].Pads()if ref!='J202'or q.GetNumber()=='23']
need(libtype[('J202','23')]=='passive','external connector passive')
for ref,signal in [('R242','SENS_SCL'),('R243','SENS_SDA')]:
 nets={q.GetNumber():q.GetNetname()for q in fp[ref].Pads()};need(nets=={'1':signal,'2':'SENS_VIO_1V8'},'actual pullup pin domain')
results['actual_pullups_external_pin']=pullups
print(json.dumps(results,indent=2))
