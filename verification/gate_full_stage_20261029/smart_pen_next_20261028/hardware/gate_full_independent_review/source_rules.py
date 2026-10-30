from pathlib import Path
import json,hashlib,sys,xml.etree.ElementTree as E,collections
D=Path(__file__).resolve().parent;H=D.parent;S=H/'gate_control_output_candidate';B=H/'gate_input_local_routing';A=H/'gate_supply_native_mpn_source'
def req(v,m):
 if not v:raise RuntimeError(m)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={}
for folder,want in [(S,'70f161b643809f8c930c2b32bf82725be6ba742d52635171442646c5bfd6cf52'),(B,'6c6c93af899a132c19bcb04fa51918fdae25c73c7b09ec636fe911791d94953b'),(A,'d9ee61999f3520b4ddd34ccc2bf32919809f872f04905611f2bfae4abba374b8')]:
 req(sha(folder/'manifest.json')==want,'manifest changed');m=json.loads((folder/'manifest.json').read_text());fs=m.get('files',m)
 for n,h in fs.items():req(sha(folder/n)==(h['sha256'] if isinstance(h,dict) else h),'frozen file changed '+n)
 inputs[folder.name]={'manifest':want,'files':len(fs)}
for f in (A/'mainboard_projection').rglob('*.kicad_sch'):req(f.read_bytes()==(D/'native_snapshot'/f.relative_to(A/'mainboard_projection')).read_bytes(),'native source drift')
def src(file):
 x=E.parse(file);return {c.get('ref'):c for c in x.findall('./components/comp')},{(q.get('ref'),q.get('pin')):n.get('name') for n in x.findall('./nets/net') for q in n}
c,n=src(D/'fresh.xml');bc,bn=src(B/'fresh.xml');req(n==bn and set(c)==set(bc),'source identity changed')
for ref in c:
 for field in ['value','footprint','tstamps']:req(c[ref].findtext(field)==bc[ref].findtext(field),'source field delta '+ref)
contract=json.loads((S/'native_mpn_contract.json').read_text())
for ref,row in contract['parts'].items():
 fields={f.get('name'):f.text for f in c[ref].findall('./fields/field')}
 for field,key in [('MPN','mpn'),('Manufacturer','manufacturer'),('ProcurementStatus','status')]:req(fields.get(field)==row[key],'native MPN changed '+ref)
expected={('U301','1'):'3V3_AON',('U301','2'):'GND',('U301','3'):'CAM_ON',('U301','4'):'CAM_CT',('U301','5'):'CAM_QOD',('U301','6'):'CAM_3V3_PRELINK',('R106','1'):'CAM_PWR_EN',('R106','2'):'GND',('R301','1'):'CAM_ON',('R301','2'):'GND',('R302','1'):'CAM_PWR_EN',('R302','2'):'CAM_ON',('R303','1'):'CAM_3V3_PRELINK',('R303','2'):'CAM_QOD',('C303','1'):'CAM_CT',('C303','2'):'GND',('JP301','1'):'CAM_3V3_PRELINK',('JP301','2'):'CAM_3V3_SW',('U101','47'):'CAM_PWR_EN',('U204','8'):'3V3_AON'}
req(all(n.get(k)==v for k,v in expected.items()),'Gate/default network mismatch')
for ref,prefix in [('R106','100k'),('R301','100k'),('R302','1k'),('R303','100')]:req(c[ref].findtext('value').startswith(prefix),'Gate resistor value '+ref)
for ext in ['kicad_pro','kicad_dru']:req((D/'native_snapshot'/('mainboard_revD.'+ext)).read_bytes()==(B/('mainboard_revD.'+ext)).read_bytes(),'rule drift')
sys.path.insert(0,str(S));import pcb_preflight as pf
lock=json.loads((S/'preflight_lock.json').read_text());cfg=pf.verify(D/'native_snapshot/mainboard_revD.kicad_pcb',lock);cfg.pop('checked_utc',None)
try:pf.verify(D/'native_snapshot/mainboard_revD.kicad_pcb',lock,'manufacturing')
except ValueError:pass
else:raise RuntimeError('Manufacturing released')
a=json.loads((B/'drc.json').read_text());b=json.loads((D/'drc.json').read_text())
def key(v):return(v['type'],v.get('severity'),v.get('description'),tuple(sorted(i.get('uuid','') for i in v.get('items',[]))))
ka=collections.Counter(key(v) for v in a['violations']);kb=collections.Counter(key(v) for v in b['violations']);added=list((kb-ka).elements());gone=list((ka-kb).elements());req(len(added)==2 and all(v[0]=='track_dangling' for v in added),'Unexpected fresh new DRC')
req([len(b[k]) for k in ['violations','unconnected_items','schematic_parity']]==[28,41,0],'full DRC counts')
print(json.dumps({'dependencies':inputs,'source_entities':len(c),'source_endpoints':len(n),'native_MPN_refs':list(contract['parts']),'gate_source_default_map':{'.'.join(k):v for k,v in expected.items()},'configuration':cfg,'manufacturing_rejected':True,'full_DRC':{'before':[135,54,0],'after':[28,41,0],'new_entries':added,'removed_entries':len(gone),'remaining_types':dict(collections.Counter(v['type'] for v in b['violations']))},'source_hashes':{str(f.relative_to(D/'native_snapshot')):sha(f) for f in (D/'native_snapshot').rglob('*.kicad_sch')}},indent=2))
