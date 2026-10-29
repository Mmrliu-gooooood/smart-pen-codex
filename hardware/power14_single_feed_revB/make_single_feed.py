from pathlib import Path
import pcbnew as k,json,hashlib
D=Path(__file__).resolve().parent;S=D.parent/'power_integrated_layout_14x45';src=S/'power_integrated_study.kicad_pcb'
if hashlib.sha256(src.read_bytes()).hexdigest()!='5c5764e7576c9461464c12da3531410e63ef4db32a28a67a5fa6125ef0b92014':raise RuntimeError('baseline mismatch')
b=k.LoadBoard(str(src));remove=['174e62ed-1e66-4399-a9de-ab6b5cfd5a4c','2ed5de36-fc66-4c5f-b1f9-481c80239f06','5861a9b2-5b80-42fc-b6e6-084cf70c7d2c','78498a5e-0ad8-4a74-9ab9-6093e1834da4','85a5fbe7-f1ea-44dc-9b60-e9e0c0b7ab78','a187ea52-25cd-4175-9249-5a0a776e7793','df0299b4-1439-4e05-a850-1d5d052061b2','1c46960c-b83b-426b-841c-9d177b08e837','4685d76c-edc4-4503-aa6f-fd4c7b191d69'];got=[]
for t in list(b.GetTracks()):
 if t.m_Uuid.AsString() in remove:
  if t.GetNetname()!='VBUS_5V' or t.GetLayer()!=k.F_Cu:raise RuntimeError('Unexpected removal')
  got.append(t.m_Uuid.AsString());b.Delete(t)
if set(got)!=set(remove):raise RuntimeError('missing removal')
net=b.FindNet('VBUS_5V');pts=[(7.75,4.8),(7.75,3.75),(10.15,3.75),(11.65,5.25)];added=[]
for a,z in zip(pts,pts[1:]):
 t=k.PCB_TRACK(b);t.SetStart(k.VECTOR2I(*(k.FromMM(x) for x in a)));t.SetEnd(k.VECTOR2I(*(k.FromMM(x) for x in z)));t.SetWidth(k.FromMM(.3));t.SetLayer(k.F_Cu);t.SetNet(net);b.Add(t)
b.BuildConnectivity();filler=k.ZONE_FILLER(b);filler.Fill(b.Zones());k.SaveBoard(str(D/'power_integrated_study.kicad_pcb'),b)
saved=k.LoadBoard(str(D/'power_integrated_study.kicad_pcb')); original=k.LoadBoard(str(src)); original_ids={t.m_Uuid.AsString() for t in original.GetTracks()}; added=sorted(t.m_Uuid.AsString() for t in saved.GetTracks() if t.m_Uuid.AsString() not in original_ids)
(D/'single_feed_delta.json').write_text(json.dumps({'baseline_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'removed':remove,'added':added,'new_path_mm':pts,'new_width_mm':.3},indent=2))
