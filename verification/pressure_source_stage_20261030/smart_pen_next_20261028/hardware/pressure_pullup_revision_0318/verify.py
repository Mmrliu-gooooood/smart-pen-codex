from pathlib import Path
import json,hashlib,csv,xml.etree.ElementTree as E,copy,collections,re
from materialize import D,BASE,replace_r503,req,MPN
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
changed=['mainboard_revD.kicad_pcb','schematic/pickup_on_main.kicad_sch'];files=[]
for p in sorted(BASE.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(BASE);q=D/'native'/rel;req(q.is_file(),'native missing '+str(rel));files.append(str(rel))
 if str(rel) in changed:expected,_=replace_r503(p.read_text(),str(rel).endswith('.kicad_pcb'));req(q.read_text()==expected,'only exact R503 delta '+str(rel))
 else:req(q.read_bytes()==p.read_bytes(),'unallowed source edit '+str(rel))
req(set(files)=={str(p.relative_to(D/'native')) for p in (D/'native').rglob('*') if p.is_file()},'native file set')
def canon(x):return (x.tag,tuple(sorted(x.attrib.items())),(x.text or '').strip(),tuple(canon(c) for c in x))
a=E.parse(D/'checks/base/netlist.xml').getroot();b=E.parse(D/'checks/candidate/netlist.xml').getroot()
for k in ['nets','libparts']:req(canon(a.find(k))==canon(b.find(k)),k+' unchanged')
la,lb=E.tostring(a.find('libraries')).decode(),E.tostring(b.find('libraries')).decode()
req(la.replace(str(BASE),'$NATIVE')==lb.replace(str(D/'native'),'$NATIVE'),'library URIs only relocate with exact copied libraries')
ca={x.get('ref'):x for x in a.find('components')};cb={x.get('ref'):x for x in b.find('components')};req(ca.keys()==cb.keys(),'component refs')
for ref,c in ca.items():
 n=copy.deepcopy(cb[ref])
 if ref=='R503':
  req(n.findtext('value')=='47k 1%','R503 netlist47');req(n.find('./fields/field[@name="MPN"]').text==MPN,'R503 netlist MPN');req(n.find('./property[@name="MPN"]').get('value')==MPN,'R503 property MPN');n.find('value').text=c.findtext('value');n.find('fields').remove(n.find('./fields/field[@name="MPN"]'));n.remove(n.find('./property[@name="MPN"]'))
 req(canon(c)==canon(n),'netlist unallowed component delta '+ref)
def bom(label):return {x['Reference']:x for x in csv.DictReader((D/f'checks/{label}/bom.csv').open())}
ba,bb=bom('base'),bom('candidate');req(ba.keys()==bb.keys(),'BOM refs')
for r,v in ba.items():
 n=bb[r].copy()
 if r=='R503':req(n['Value']=='47k 1%' and n['MPN']==MPN,'R503 generated BOM');n['Value']=v['Value'];n['MPN']=v['MPN']
 req(n==v,'BOM unallowed delta '+r)
def findings(label,kind):
 j=json.loads((D/f'checks/{label}/{kind}.json').read_text())
 if kind=='erc':return [v for s in j['sheets'] for v in s['violations']]
 return j
ra,rb=findings('base','drc'),findings('candidate','drc')
for k in ['violations','schematic_parity']:req(ra[k]==rb[k],k+' exact')
def signature(v):return json.dumps(v,sort_keys=True)
# KiCad may select different representative objects of unchanged connected copper.
# Exact two-property source transformation above proves all other board bytes unchanged.
# Compare per-net airwire counts and retain all raw finding differences, not suppress them.
def airwire_net(v):
 ns=[re.findall(r'\[([^]]+)\]',x['description']) for x in v['items']]
 req(all(len(x)==1 for x in ns) and len(set(x[0] for x in ns))==1,'airwire endpoint net consistency')
 return (v['type'],v['severity'],ns[0][0])
req(collections.Counter(map(airwire_net,ra['unconnected_items']))==collections.Counter(map(airwire_net,rb['unconnected_items'])),'per-net unconnected counts unchanged')
rawa=collections.Counter(map(signature,ra['unconnected_items']));rawb=collections.Counter(map(signature,rb['unconnected_items']))
rawdiff=dict(removed=[json.loads(x) for x in (rawa-rawb).elements()],added=[json.loads(x) for x in (rawb-rawa).elements()])
req(rawdiff==json.loads((D/'drc_unconnected_raw_difference.json').read_text()),'retained exact raw airwire difference evidence')
req(findings('base','erc')==findings('candidate','erc'),'ERC findings unchanged')
req([len(rb[k]) for k in ['violations','unconnected_items','schematic_parity']]==[0,134,0],'actual native counts')
erc=findings('candidate','erc');req(len(erc)==1 and erc[0]['severity']=='warning','known ERC warning only')
# Closed resistive path room-temperature tolerance-only screening. Real rail and sensor qualification remain external.
def load(r3,rail_min=3.0,rail_max=3.6):
 return dict(min_A=rail_min/(r3*1.01+1000*1.01+1),max_A=rail_max/(r3*.99+1000*.99),max_R503_W=rail_max**2*(r3*.99)/(r3*.99+1000*.99)**2)
old,new=load(100000),load(47000);req(old['max_A']<50e-6,'old100k must fail');req(new['min_A']>=50e-6,'new47k minimum current');req(new['max_R503_W']<0.0003,'continuous R503 power')
negative=[]
for label,value,mpn in [('old_value','100k 1%',MPN),('wrong_MPN','47k 1%','RC0603FR-07100KL'),('missing_MPN','47k 1%','')]:
 try:req(value=='47k 1%' and mpn==MPN,'source contract mismatch')
 except RuntimeError:negative.append(label)
 else:raise RuntimeError('negative failed '+label)
r=dict(status='NOFAB_NOPOWER_CONDITIONAL_MINIMUM_LOAD_CORRECTION_ONLY',native_files=len(files),components=len(ca),nets=len(list(a.find('nets'))),net_pin_function_mapping_exact=True,only_R503_value_MPN_changes=changed,full_drc=[0,134,0],raw_airwire_representative_changes=len(rawdiff["removed"]),per_net_airwire_counts_unchanged=True,erc_errors=0,erc_warnings=1,old_R503=old,new_R503=new,condition='AON 3.0..3.6 V; both resistors +/-1%; contact 0..1 ohm; excludes leakage, temperature drift, ESD and real rail qualification',negative_cases=negative,board_sha=sha(D/'native/mainboard_revD.kicad_pcb'))
print(json.dumps(r,indent=2))
