from pathlib import Path
import re,json,hashlib,copy,xml.etree.ElementTree as E,csv,collections
D=Path(__file__).resolve().parent;R=D.parents[1];S=R/'hardware/pressure_pullup_revision_0318';B=R/'hardware/mcu_supply_access_candidate_0300/native'
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
changed=['mainboard_revD.kicad_pcb','schematic/pickup_on_main.kicad_sch'];out={}
for f in B.rglob('*'):
 if not f.is_file():continue
 rel=str(f.relative_to(B));g=S/'native'/rel
 if rel not in changed:req(f.read_bytes()==g.read_bytes(),'other native '+rel);continue
 a=parse(f.read_text());b=parse(g.read_text());kind='footprint'if rel.endswith('.kicad_pcb')else'symbol'
 def target(root):
  ns=[n for n in root if isinstance(n,list)and n and n[0]==kind and prop(n,'Reference')and prop(n,'Reference')[2]=='R503'];req(len(ns)==1,'unique R503');return ns[0]
 x,y=target(a),target(b);req(prop(x,'Value')[2]=='100k 1%'and prop(x,'MPN')is None,'old fields');req(prop(y,'Value')[2]=='47k 1%'and prop(y,'MPN')[2]=='RC0603FR-0747KL','new fields')
 mpn=prop(y,'MPN');req(['hide','yes']in mpn or ['hide','yes']in child(mpn,'effects'),'hidden MPN')
 y.remove(mpn);prop(y,'Value')[2]='100k 1%';req(a==b,'only declared source fields '+rel);out[rel]='only instance value+hidden MPN; all geometry/source nodes unchanged'
root=E.parse(D/'checks/candidate/netlist.xml').getroot();parts={x.get('ref'):x for x in root.find('components')};nets=root.find('nets');req(len(parts)==102 and len(nets)==90,'parts/nets')
netnodes={n.get('name'):[dict(x.attrib)for x in n.findall('node')]for n in nets};nib=netnodes['NIB_CONTACT_N'];req(any(x.get('ref')=='U101'and x.get('pin')=='7'and x.get('pinfunction')=='GPIO2'for x in nib),'GPIO2 package7 metadata')
req(parts['R503'].findtext('value')=='47k 1%','netlistvalue');rows=list(csv.DictReader((D/'checks/candidate/bom.csv').open()));rr=next(x for x in rows if x['Reference']=='R503');req(rr['MPN']=='RC0603FR-0747KL','BOM MPN')
old=3.3/(100000+1000);mn=3/(47000*1.01+1000*1.01+1);mx=3.6/(47000*.99+1000*.99);req(mn>50e-6 and 3.6/(101000*.99)<50e-6,'load')
a=json.loads((D/'checks/base/drc.json').read_text());b=json.loads((D/'checks/candidate/drc.json').read_text())
def signature(v):return json.dumps(v,sort_keys=True)
ra=collections.Counter(map(signature,a['unconnected_items']));rb=collections.Counter(map(signature,b['unconnected_items']));delta={'removed':[json.loads(x)for x in(ra-rb).elements()],'added':[json.loads(x)for x in(rb-ra).elements()]};(D/'fresh_raw_airwire_difference.json').write_text(json.dumps(delta,indent=2)+'\n')
print(json.dumps({'source_delta':out,'parts':102,'nets':90,'NIB_CONTACT_N':nib,'R503_BOM':rr,'old_nominal_3v3_uA':old*1e6,'new_min_uA':mn*1e6,'new_max_uA':mx*1e6,'fresh_raw_airwire_changes':len(delta['removed']),'status':'NOFAB_NOPOWER_CONDITIONAL_SOURCE_ONLY'},indent=2))
