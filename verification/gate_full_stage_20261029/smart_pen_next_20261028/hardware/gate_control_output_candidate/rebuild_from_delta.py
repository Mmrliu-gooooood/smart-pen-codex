"""Rebuild this bounded candidate from immutable ae805 plus explicit deltas; never overwrites source."""
from pathlib import Path
import os,json,re,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache';os.environ['XDG_DATA_HOME']='/tmp/rf-independent/data'
import pcbnew as p
D=Path(__file__).resolve().parent;source=D.parent/'gate_input_local_routing/mainboard_revD.kicad_pcb'
if hashlib.sha256(source.read_bytes()).hexdigest()!='ae805cea5d51e864588bdf052b64e1bacce118a122b9f98ce21ddaa15345a691':raise RuntimeError('Dependency hash mismatch')
removed={r['uuid']for r in json.loads((D/'removed_local_copper.json').read_text())};raw=re.sub(r'\n\t\((?:segment|via)\n.*?\n\t\)',lambda m:''if any(u in m[0]for u in removed)else m[0],source.read_text(),flags=re.S)
O=D/'guard_boards';O.mkdir(exist_ok=True);out=O/'rebuilt_from_delta.kicad_pcb';out.write_text(raw);b=p.LoadBoard(str(out));pt=lambda q:p.VECTOR2I(*(round(v*1e6)for v in q))
fps={f.GetReference():f for f in b.GetFootprints()}
for ref,pos in {'R301':(5.7,66.5),'R302':(5.7,73),'TP301':(4.325,74.5),'C302':(9.5,74)}.items():fps[ref].SetPosition(pt(pos))
mods=json.loads((D/'modified_existing_copper.json').read_text())
for t in b.GetTracks():
 if t.m_Uuid.AsString()in mods:r=mods[t.m_Uuid.AsString()];t.SetStart(pt(r['new_a']));t.SetEnd(pt(r['new_z']))
uuid_map={}
for r in json.loads((D/'new_routes.json').read_text()):
 if r['type']=='track':
  t=p.PCB_TRACK(b);t.SetStart(pt(r['a']));t.SetEnd(pt(r['z']));t.SetWidth(p.FromMM(r['width']));t.SetLayer(b.GetLayerID(r['layer']))
 else:
  t=p.PCB_VIA(b);t.SetPosition(pt(r['xy']));t.SetWidth(p.FromMM(r['diameter']));t.SetDrill(p.FromMM(r['drill']));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu)
 uuid_map[t.m_Uuid.AsString()]=r['uuid'];t.SetNet(b.FindNet(r['net']));b.Add(t)
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(out),b)
raw=out.read_text()
for a,z in uuid_map.items():raw=raw.replace('(uuid "'+a+'")','(uuid "'+z+'")')
out.write_text(raw)
print(json.dumps({'dependency_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'reconstructed_pcb_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'output':str(out),'verification':'Run audit_gate.py on this output; raw serialization hash can differ by item ordering.'},indent=2))
