from pathlib import Path
import sys,json,re,hashlib,xml.etree.ElementTree as ET
R=Path('/workspace/scratch/fe148e758944/smart_pen_next_20261028');D=R/'hardware/ground_recovery_native_0818';O=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));from finite_copper import build,components
import os
os.environ["XDG_CONFIG_HOME"]="/tmp/camera-remaining-review-config"
import pcbnew as p
b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));nodes=build(b);physical={net:components(ns)for net,ns in nodes.items()};xml=ET.parse(D/'checks/candidate/netlist.xml');comps={c.get('ref'):c for c in xml.findall('.//components/comp')};lib={(l.get('lib'),l.get('part')):{q.get('num'):q.attrib for q in l.findall('./pins/pin')}for l in xml.findall('.//libparts/libpart')}
# Parse embedded source lib_symbols, not PCB pinfunction fields.
def parse(s):
 toks=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s);stack=[];root=None
 for t in toks:
  if t=='(':
   a=[]
   if stack:stack[-1].append(a)
   stack.append(a)
  elif t==')':
   a=stack.pop()
   if not stack:root=a
  else:stack[-1].append(json.loads(t)if t.startswith('"')else t)
 return root
def children(x,k):return [a for a in x if isinstance(a,list)and a and a[0]==k]
def walk(x,k):
 for a in x:
  if isinstance(a,list):
   if a and a[0]==k:yield a
   yield from walk(a,k)
emb={}
for f in (D/'native').rglob('*.kicad_sch'):
 a=parse(f.read_text())
 for ls in children(a,'lib_symbols'):
  for sy in children(ls,'symbol'):
   pins={}
   for q in walk(sy,'pin'):
    num=children(q,'number');name=children(q,'name')
    if num and name:pins[num[0][1]]={'name':name[0][1],'electrical_type':q[1]}
   emb[(str(f.relative_to(D/'native')),sy[1])]=pins
pad={q.m_Uuid.AsString():(f,q)for f in b.GetFootprints()for q in f.Pads()};track={q.m_Uuid.AsString():q for q in b.GetTracks()};drc=json.loads((D/'checks/candidate/drc.json').read_text());counts={};edges=[]
for i,v in enumerate(drc['unconnected_items']):
 nets=set()
 for x in v['items']:
  u=x['uuid']
  if u in pad:nets.add(pad[u][1].GetNetname())
  elif u in track:nets.add(track[u].GetNetname())
 if len(nets)!=1:raise RuntimeError((i,nets))
 n=nets.pop();counts[n]=counts.get(n,0)+1;edges.append({'index':i,'net':n,**v})
rows=[];errors=[]
for net in xml.findall('.//nets/net'):
 n=net.get('name');terms=[]
 for q in net.findall('node'):
  ref=q.get('ref');num=q.get('pin');c=comps[ref];ls=c.find('libsource');key=(ls.get('lib'),ls.get('part'));lp=lib[key].get(num);sheet=c.find('property[@name="Sheetfile"]').get('value');ep=emb.get((sheet,':'.join(key)),{}).get(num)
  canon=lambda x: '' if x in (None,'~','') else x
  ok=bool(lp and ep and canon(lp['name'])==canon(ep['name']) and canon(q.get('pinfunction'))==canon(lp['name']))
  if not ok:errors.append({'ref':ref,'pin':num,'net':n,'libpart':lp,'embedded':ep,'node':q.attrib})
  loc=[{'uuid':u,'xy_mm':[pp.GetPosition().x/1e6,pp.GetPosition().y/1e6],'layers':pp.GetLayerSet().FmtHex()}for u,(ff,pp)in pad.items()if ff.GetReference()==ref and pp.GetNumber()==num]
  terms.append({'ref':ref,'package_pin':num,'source_pin_function':lp['name']if lp else None,'electrical_type':lp['type']if lp else None,'embedded_verified':ok,'library':':'.join(key),'sheet':sheet,'physical_pads':loc})
 rows.append({'net':n,'drc_missing_connections':counts.get(n,0),'physical_components':physical.get(n,[]),'minimum_component_joins':max(0,len(physical.get(n,[]))-1),'source_terminals':terms})
out={'pcb_sha':hashlib.sha256((D/'native/mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'drc_total':sum(counts.values()),'net_counts':counts,'source_mapping_errors':errors,'nets':rows,'drc_edges':edges}
(O/'inventory.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'counts':counts,'errors':errors,'total':sum(counts.values()),'physical_joins':sum(r['minimum_component_joins']for r in rows)},indent=2))
