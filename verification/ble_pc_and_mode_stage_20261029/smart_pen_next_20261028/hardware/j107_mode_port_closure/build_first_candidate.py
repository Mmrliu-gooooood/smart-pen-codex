from pathlib import Path
import os,json,hashlib,re,shutil
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache';os.environ['XDG_DATA_HOME']='/tmp/rf-independent/data'
import pcbnew as p
D=Path(__file__).resolve().parent;S=D.parent/'gate_cam_on_path_maintenance';N=D/'native';src=S/'native/mainboard_revD.kicad_pcb'
if hashlib.sha256(src.read_bytes()).hexdigest()!='1c4907d04a2bf2dea3a53f89266bc49c0cb96a0683b4898b58cd36b6525ec16d':raise RuntimeError('Wrong current baseline')
if N.exists():raise RuntimeError('First candidate already exists; do not overwrite')
shutil.copytree(S/'native',N)
ids={'3ac5bb80-3c7d-4b2f-a6da-470db2406f74','e4f8df0a-430c-47de-81ff-a856e125fcf0','3fe4721f-b482-47d6-8d38-5609ed06408d'}
b0=p.LoadBoard(str(src));removed=[]
for t in b0.GetTracks():
 if t.m_Uuid.AsString()in ids:removed.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'type':'via'if isinstance(t,p.PCB_VIA)else'track','layer':b0.GetLayerName(t.GetLayer()),'a':[p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y)],'z':[p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y)],'width':p.ToMM(t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth())})
if len(removed)!=3 or any(r['net']!='GND'for r in removed):raise RuntimeError('Old GND tail identity mismatch')
raw=re.sub(r'\n\t\((?:segment|via)\n.*?\n\t\)',lambda m:''if any(u in m[0]for u in ids)else m[0],src.read_text(),flags=re.S);dest=N/'mainboard_revD.kicad_pcb';dest.write_text(raw);b=p.LoadBoard(str(dest));rows=[];pt=lambda q:p.VECTOR2I(*(round(v*1e6)for v in q))
def track(net,layer,a,z,w):
 t=p.PCB_TRACK(b);t.SetStart(pt(a));t.SetEnd(pt(z));t.SetWidth(p.FromMM(w));t.SetLayer(b.GetLayerID(layer));t.SetNet(b.FindNet(net));b.Add(t);rows.append({'uuid':t.m_Uuid.AsString(),'net':net,'type':'track','layer':layer,'a':a,'z':z,'width':w})
def via(net,q):
 t=p.PCB_VIA(b);t.SetPosition(pt(q));t.SetWidth(p.FromMM(.6));t.SetDrill(p.FromMM(.3));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNet(b.FindNet(net));b.Add(t);rows.append({'uuid':t.m_Uuid.AsString(),'net':net,'type':'via','xy':q,'diameter':.6,'drill':.3})
track('USB_EN1','F.Cu',[8.2,81.5],[9.4,81.5],.15);via('USB_EN1',[9.4,81.5]);track('USB_EN1','B.Cu',[9.4,81.5],[7.45,81.5],.15)
track('USB_EN2','F.Cu',[8.2,83.9],[9.4,84.9],.15);via('USB_EN2',[9.4,84.9]);track('USB_EN2','In3.Cu',[9.4,84.9],[7.45,84.9],.15)
track('GND','F.Cu',[8.2,86.3],[9.45,86.3],.5)
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(dest),b)
(D/'j107_delta.json').write_text(json.dumps({'input_pcb_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'candidate_pcb_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'removed':removed,'added':rows,'rationale':'Replace obsolete old J106 input-GND V landing (016d old pad centre9,84), preserve actual present J106 return and right stitchvia, then independently close current J107 three pads. No footprints/modes/default pulls changed.'},indent=2))
oldrows=json.loads((S/'new_routes.json').read_text());(D/'new_routes.json').write_text(json.dumps(oldrows+rows,indent=2));oldremoved=json.loads((S/'removed_local_copper.json').read_text());(D/'removed_local_copper.json').write_text(json.dumps(oldremoved+removed,indent=2))
for n in ['modified_existing_copper.json','native_mpn_contract.json','source_binding.json','pcb_preflight.py','preflight_lock.json']:
 shutil.copy2(S/n,D/n)
print(hashlib.sha256(dest.read_bytes()).hexdigest())
