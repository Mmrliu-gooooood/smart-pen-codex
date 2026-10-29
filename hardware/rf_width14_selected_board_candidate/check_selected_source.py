from pathlib import Path
import xml.etree.ElementTree as E,hashlib,json,pcbnew as p,re
D=Path(__file__).resolve().parent;S=D.parent/'mainboard_fixture_allocation_v3/mainboard_projection'
def req(v,m):
 if not v:raise RuntimeError(m)
for f in S.rglob('*.kicad_sch'):req((D/f.relative_to(S)).read_bytes()==f.read_bytes(),'source revision drift '+str(f))
x=E.parse(D/'mainboard_revD.xml');cs={c.get('ref'):c for c in x.findall('./components/comp')};ns={(n.get('ref'),n.get('pin')):net.get('name') for net in x.findall('./nets/net') for n in net};req(len(cs)==83 and len(ns)==303,'sourcecounts')
b=p.LoadBoard(str(D/'mainboard_revD.kicad_pcb'));fs={f.GetReference():f for f in b.GetFootprints()};req(len(fs)==79,'physicalcount')
for ref,f in fs.items():
 c=cs[ref];req(f.GetPath().AsString()=='/cebe562b-54ce-58d7-a4f0-094e70dd7d0a'+c.find('sheetpath').get('tstamps')+c.findtext('tstamps'),'rootpath '+ref)
 for pad in f.Pads():req(pad.GetNetname()==ns.get((ref,pad.GetNumber()),''),'padnet '+ref)
missing=set(cs)-set(fs);req(missing=={'J103','J104','J105','J202'},'missing set')
req(hashlib.sha256((D/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest()=='016d963f764430b6122da29039a5573792e3f0c78078180b18582af69b044c7e','PCB drift')
rpt=(D/'drc.rpt').read_text();req(re.findall(r'^\[([^]]+)\]:',rpt,re.M)==['missing_footprint']*4,'unexpected DRC')
req((D/'drc.exit').read_text().strip()=='5','DRCexit');req((D/'erc.exit').read_text().strip()=='5' and 'ERC messages: 1  Errors 0  Warnings 1' in (D/'erc.rpt').read_text(),'ERC classification')
print(json.dumps({'status':'SELECTED_BOARD_PRESENT_PADS_ROUTED_FOUR_UNIMPLEMENTED_INTERFACES_NOFAB','source_components':len(cs),'source_endpoints':len(ns),'placed':len(fs),'missing':sorted(missing),'native_DRC_geometry':0,'native_unconnected':0,'native_ERC_errors':0,'native_ERC_warnings':1,'source_sheet_hashes':{str(f.relative_to(D)):hashlib.sha256(f.read_bytes()).hexdigest() for f in D.rglob('*.kicad_sch')}},indent=2))
