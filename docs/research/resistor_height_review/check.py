from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E,pcbnew
D=Path(__file__).resolve().parent; ROOT=D.parents[2]; C=ROOT/'docs/research/resistor_height_contract'
d=json.loads((C/'contract.json').read_text());P=ROOT/d['board_path'];x=E.parse(P.with_suffix('.xml'));cs={c.get('ref'):c for c in x.findall('./components/comp')};ns={(a.get('ref'),a.get('pin')):n.get('name') for n in x.findall('./nets/net') for a in n}; b=pcbnew.LoadBoard(str(P));fs={f.GetReference():f for f in b.GetFootprints()}
rows=d['resistors']; refs=[r['ref'] for r in rows]
if len(set(refs))!=9 or set(refs)!=set(d['scope_refs']):raise ValueError('unique exact refs')
for r in rows:
 ref=r['ref']; f=fs[ref]; c=cs[ref]
 if r['source_value']!=c.findtext('value'):raise ValueError('schematic value '+ref)
 pads=sorted(f.Pads(),key=lambda p:p.GetNumber())
 if r['source_net_by_pin']!={p.GetNumber():ns[(ref,p.GetNumber())] for p in pads}:raise ValueError('schematic nets '+ref)
 if r['native_pad_size_mm']!=[[p.GetSize().x/1e6,p.GetSize().y/1e6] for p in pads]:raise ValueError('pad sizes '+ref)
 if r['native_pad_centres_mm']!=[[p.GetPosition().x/1e6,p.GetPosition().y/1e6] for p in pads]:raise ValueError('pad coordinates '+ref)
 if any(abs(z-.8)>1e-6 or abs(w-.95)>1e-6 for z,w in r['native_pad_size_mm']):raise ValueError('land geometry '+ref)
 p,q=pads; spacing=((p.GetPosition().x-q.GetPosition().x)**2+(p.GetPosition().y-q.GetPosition().y)**2)**.5/1e6
 if abs(spacing-1.65)>1e-5:raise ValueError('land centres '+ref)
result={'scope':'supplemental source/net/pad review only','unique_refs':refs,'native_xml_sha256':hashlib.sha256(P.with_suffix('.xml').read_bytes()).hexdigest(),'board_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'contract_manifest_sha256':hashlib.sha256((C/'manifest.json').read_bytes()).hexdigest(),'schematic_value_and_net_identity':True,'native_pad_geometry_verified':True,'land_pattern_qualification':'OPEN; dimensions not identical to YAGEO recommendation','status':'NOFAB conditional mechanical study'}
print(json.dumps(result,indent=2))
