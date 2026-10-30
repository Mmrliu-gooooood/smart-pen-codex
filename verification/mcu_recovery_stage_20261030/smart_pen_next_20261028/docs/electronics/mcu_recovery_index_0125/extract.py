from pathlib import Path
import json,re,hashlib,sys
import os
os.environ['XDG_CONFIG_HOME']='/tmp/pen-recovery-index-0125'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[2];S=R/'hardware/mcu_power_ground_clearance_0109';N=S/'native'
def parse(t):
 toks=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',t); stack=[];out=None
 for x in toks:
  if x=='(':
   a=[]
   if stack:stack[-1].append(a)
   stack.append(a)
  elif x==')':out=stack.pop()
  else:stack[-1].append(json.loads(x)if x.startswith('"')else x)
 return out
def children(t,k):return [x for x in t if isinstance(x,list)and x and x[0]==k]
def first(t,k):return next(iter(children(t,k)),None)
libs={};instances={};sources={}
for f in sorted((N/'schematic').glob('*.kicad_sch')):
 tree=parse(f.read_text()); ls=first(tree,'lib_symbols')
 if ls:
  for sy in children(ls,'symbol'):
   pins={}
   for unit in children(sy,'symbol'):
    for pin in children(unit,'pin'):pins[first(pin,'number')[1]]=first(pin,'name')[1]
   
   if sy[1] in libs and libs[sy[1]]!=pins:raise ValueError('conflicting embedded library '+sy[1])
   libs[sy[1]]=pins
 for sy in children(tree,'symbol'):
  li=first(sy,'lib_id')
  if li:
   props={x[1]:x[2]for x in children(sy,'property')};ref=props.get('Reference');instances[ref]=li[1];sources[ref]=str(f.relative_to(R))
b=p.LoadBoard(str(N/'mainboard_revD.kicad_pcb'));core=json.loads((S/'core_diagnostic.json').read_text());rows=[];allpads=[]
for f in b.GetFootprints():
 for q in f.Pads():
  net=q.GetNetname();name=f.GetReference()+'.'+q.GetNumber();li=instances.get(f.GetReference(),''); row={'pad':name,'uuid':q.m_Uuid.AsString(),'net':net,'value':f.GetValue(),'lib_id':li,'pin_name':libs.get(li,{}).get(q.GetNumber()),'schematic':sources.get(f.GetReference()),'x_mm':q.GetPosition().x/1e6,'y_mm':q.GetPosition().y/1e6}
  allpads.append(row)
  if net in core and name not in core[net]['after'] and not any(x.startswith(name+'#'+row['uuid'])for x in core[net]['after']):rows.append(row)
# Supply-domain classification uses actual opposite capacitor pad net, not historical A/B assumptions.
byref={}
for x in allpads:byref.setdefault(x['pad'].split('.')[0],[]).append(x)
for x in rows:
 ref=x['pad'].split('.')[0];other=[y['net']for y in byref[ref]if y['uuid']!=x['uuid']];x['other_pad_nets']=other
 if ref.startswith('U')and any(t in x['value']for t in ['AXC','TCA9517']):x['category']='translator '+str(x['pin_name'])
 elif ref.startswith('C')and '3V3_AON'in other:x['category']='GND return of AON capacitor'
 elif ref.startswith('C')and 'SENS_VIO_1V8'in other:x['category']='GND return of SENS_VIO capacitor (separate domain)'
 elif x['net']=='3V3_AON'and ref.startswith('C'):x['category']='AON capacitor supply'
 else:x['category']='other '+x['net']
sens=[x for x in allpads if x['net']=='SENS_VIO_1V8'];tx=[x for x in allpads if any(t in x['value']for t in ['AXC','TCA9517'])and x['pin_name']in ['VCCA','VCCB','GND']]
counts={n:sum(x['net']==n for x in rows)for n in core}
if counts!={'3V3_AON':25,'GND':63}:raise ValueError(counts)
if any(x['pin_name']is None for x in tx):raise ValueError('missing pin names')
obj={'pcb_sha256':hashlib.sha256((N/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'method':'actual PCB physical pads minus frozen verified core set; pin names from embedded current schematic lib_symbols, not old annotations','remaining_counts':counts,'remaining':rows,'translator_supply_ground_pin_map':tx,'separate_SENS_VIO_net_pads_not_in_25_AON_or_63_GND_count':sens}
(D/'remaining_pads.json').write_text(json.dumps(obj,indent=2))
print(json.dumps({'counts':counts,'translator':tx},indent=2))
