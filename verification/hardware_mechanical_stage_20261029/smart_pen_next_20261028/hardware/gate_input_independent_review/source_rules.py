from pathlib import Path
import sys,json,hashlib,xml.etree.ElementTree as E,math,os,collections
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config'
D=Path(__file__).resolve().parent;H=D.parent;S=H/'gate_input_local_routing';B=H/'imu_compact_0402_placement';A=H/'gate_supply_native_mpn_source'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def req(v,m):
 if not v:raise RuntimeError(m)
inputs={}
for folder,want in [(S,'6c6c93af899a132c19bcb04fa51918fdae25c73c7b09ec636fe911791d94953b'),(B,'d7240c77722bdfbd61bfdef5e62e449d92add6f5e06743fb4209b07bebc089ea'),(A,'d9ee61999f3520b4ddd34ccc2bf32919809f872f04905611f2bfae4abba374b8')]:
 req(sha(folder/'manifest.json')==want,'manifest drift');m=json.loads((folder/'manifest.json').read_text());fs=m.get('files',m)
 for n,h in fs.items():req(sha(folder/n)==h,'dependency drift '+str(folder/n))
 inputs[str(folder.relative_to(H))]={'manifest_sha256':want,'files':len(fs)}
for f in (A/'mainboard_projection').rglob('*.kicad_sch'):req(f.read_bytes()==(D/'native_snapshot'/f.relative_to(A/'mainboard_projection')).read_bytes(),'source sheet mismatch')
def src(file):
 x=E.parse(file);return {c.get('ref'):c for c in x.findall('./components/comp')},{(q.get('ref'),q.get('pin')):n.get('name') for n in x.findall('./nets/net') for q in n}
cs,ns=src(D/'fresh.xml');old,on=src(B/'fresh.xml');req(ns==on,'Net function changed');contract=json.loads((S/'native_mpn_contract.json').read_text());req(len(contract['parts'])==10,'MPN count')
for r,c in cs.items():
 for f in ['value','footprint','tstamps']:req(c.findtext(f)==old[r].findtext(f),'source field changed '+r)
for r,row in contract['parts'].items():
 fields={f.get('name'):f.text for f in cs[r].findall('./fields/field')}
 for field,key in [('MPN','mpn'),('Manufacturer','manufacturer'),('ProcurementStatus','status')]:req(fields.get(field)==row[key],'MPN mismatch '+r+'.'+field)
for ext in ['kicad_pro','kicad_dru']:req((D/'native_snapshot'/('mainboard_revD.'+ext)).read_bytes()==(B/('mainboard_revD.'+ext)).read_bytes(),'rule delta')
sys.path.insert(0,str(S));import pcb_preflight as pf
lock=json.loads((S/'preflight_lock.json').read_text());conf=pf.verify(D/'native_snapshot/mainboard_revD.kicad_pcb',lock);conf.pop('checked_utc',None);req(not conf['manufacturing_approved'],'Unexpected manufacturing approval')
try:pf.verify(D/'native_snapshot/mainboard_revD.kicad_pcb',lock,'manufacturing')
except ValueError:manufacturing_rejected=True
else:raise RuntimeError('Manufacturing gate')
a=json.loads((B/'native_drc.json').read_text());b=json.loads((D/'drc.json').read_text())
def vk(v):return(v['type'],v.get('description'),v.get('severity'),tuple(sorted(i.get('uuid','') for i in v.get('items',[]))))
req(collections.Counter(vk(v) for v in a['violations'])==collections.Counter(vk(v) for v in b['violations']),'DRC changed');req([len(b[k]) for k in ['violations','unconnected_items','schematic_parity']]==[135,54,0],'DRC counts')
import pcbnew as p
ba=p.LoadBoard(str(B/'mainboard_revD.kicad_pcb'));bb=p.LoadBoard(str(D/'native_snapshot/mainboard_revD.kicad_pcb'));ta={t.m_Uuid.AsString():t for t in ba.GetTracks()};tb={t.m_Uuid.AsString():t for t in bb.GetTracks()};removed=set(ta)-set(tb);added=set(tb)-set(ta)
metrics={}
for net in ['CAM_IO_EN','CAM_ISO_OE_N','USB_EN1']:
 before=[ta[u] for u in removed if ta[u].GetNetname()==net];after=[tb[u] for u in added if tb[u].GetNetname()==net]
 req(len(before)==1 and all(t.GetLayer()==before[0].GetLayer() for t in after),'Reroute layer/net changed')
 metrics[net]={'before_mm':sum(p.ToMM(t.GetLength()) for t in before),'after_mm':sum(p.ToMM(t.GetLength()) for t in after),'layer':bb.GetLayerName(before[0].GetLayer())}
newpower={}
for net in ['3V3_AON','GND']:
 newpower[net]=[{'uuid':u,'type':tb[u].GetClass(),'start_mm':[p.ToMM(tb[u].GetStart().x),p.ToMM(tb[u].GetStart().y)],'end_mm':[p.ToMM(tb[u].GetEnd().x),p.ToMM(tb[u].GetEnd().y)],'width_mm':p.ToMM(tb[u].GetWidth(p.F_Cu) if isinstance(tb[u],p.PCB_VIA) else tb[u].GetWidth()),'length_mm':p.ToMM(tb[u].GetLength())} for u in sorted(added) if tb[u].GetNetname()==net]
print(json.dumps({'frozen_dependencies':inputs,'native_MPN_contract':contract,'functional_endpoints_unchanged':True,'configuration':conf,'manufacturing_negative_rejected':manufacturing_rejected,'fresh_DRC':[135,54,0],'signal_reroute_metrics':metrics,'new_actual_power_geometry':newpower,'via_planar_separations_mm':{'AON':1.25,'GND':math.dist((10,63.4),(11.3,67))},'limitations':'Supply escapes are through actual fill, not direct cap-to-pin wire. No gate ON/CT/QOD/output completion or HF/PI approval.','source_hashes':{str(f.relative_to(D/'native_snapshot')):sha(f) for f in (D/'native_snapshot').rglob('*.kicad_sch')}},indent=2))
