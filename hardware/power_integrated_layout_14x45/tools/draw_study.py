from pathlib import Path
import pcbnew as p,json,math
D=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(D/'power_integrated_study.kicad_pcb'));S=18
v=['<svg xmlns="http://www.w3.org/2000/svg" width="950" height="960" viewBox="0 0 950 960"><rect width="950" height="960" fill="white"/><style>text{font-family:monospace;font-size:12px}</style><text x="20" y="24">14 x 45 mm / 4 layers / thermal routed candidate / NOFAB</text>']
for layer,off,title in [(p.F_Cu,40,'FRONT: 182 core track/via items retained'),(p.B_Cu,390,'BACK: X-ray coordinates (not mirrored)')]:
 v.append(f'<text x="{off}" y="48">{title}</text><rect x="{off}" y="70" width="252" height="810" fill="#f5f5ef" stroke="black"/>')
 def xy(q):return off+p.ToMM(q.x)*S,70+p.ToMM(q.y)*S
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA):
   x,y=xy(t.GetPosition());v.append(f'<circle cx="{x}" cy="{y}" r="3" fill="#999"/>')
  elif t.GetLayer()==layer:
   x,y=xy(t.GetStart());xx,yy=xy(t.GetEnd());v.append(f'<path d="M{x},{y}L{xx},{yy}" stroke="#b88" stroke-width="{p.ToMM(t.GetWidth())*S}"/>')
 for f in b.GetFootprints():
  if f.GetLayer()!=layer:continue
  for g in f.GraphicalItems():
   if g.GetLayer() in [p.F_CrtYd,p.B_CrtYd]:
    x,y=xy(g.GetStart());xx,yy=xy(g.GetEnd());v.append(f'<path d="M{x},{y}L{xx},{yy}" stroke="#568" stroke-width="1"/>')
  for a in f.Pads():
   box=a.GetBoundingBox();x,y=xy(box.GetPosition());w=p.ToMM(box.GetWidth())*S;h=p.ToMM(box.GetHeight())*S;v.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#d8b64b" stroke="#333" stroke-width=".4"/>')
   xx,yy=xy(a.GetPosition());v.append(f'<text x="{xx}" y="{yy+3}" text-anchor="middle" style="font-size:8px">{a.GetNumber()}</text>')
  x,y=xy(f.GetPosition());v.append(f'<text x="{x}" y="{y-4}" text-anchor="middle" fill="#125">{f.GetReference()}</text>')
 if layer==p.B_Cu:
  for x,y,w,h in [(3.6,16.8,4.8,4.8),(3.6,5.5,4.8,5)]:v.append(f'<rect x="{off+x*S}" y="{70+y*S}" width="{w*S}" height="{h*S}" fill="none" stroke="#d44" stroke-dasharray="5,3"/>')
v.append('<text x="20" y="920">Red boxes: engineering placement exclusions below BQ heat / SW-inductor regions.</text><text x="20" y="940">Not thermal qualification. Two offboard NTCs excluded from board, retained in BOM.</text></svg>')
(D/'preview'/'placement.svg').write_text(''.join(v))
