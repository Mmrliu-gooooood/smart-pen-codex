from pathlib import Path
import pcbnew as p
D=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(D/'illumination_NOFAB.kicad_pcb'));S=35;out=['<svg xmlns="http://www.w3.org/2000/svg" width="820" height="720"><rect width="820" height="720" fill="white"/><style>text{font-family:monospace;font-size:13px}</style><text x="20" y="25">8 x 15 mm / 0.8 mm / 2 layers / SERIES RESISTOR, NOT CONSTANT CURRENT</text><text x="20" y="48">NOFAB: LED source/optic safety/assembly/temperature not qualified.</text>']
for layer,ox,title in [(p.F_Cu,35,'FRONT assembly / pad numbers'),(p.B_Cu,440,'BACK copper X-ray, not mirrored')]:
 oy=100;out.append(f'<text x="{ox}" y="85">{title}</text><rect x="{ox}" y="{oy}" width="280" height="525" fill="#faf8ee" stroke="black"/>')
 def point(q):return ox+p.ToMM(q.x)*S,oy+p.ToMM(q.y)*S
 for z in b.Zones():
  if z.GetLayer()!=layer:continue
  poly=z.GetFilledPolysList(layer)
  for i in range(poly.OutlineCount()):
   c=poly.COutline(i);pts=' '.join(f'{point(c.CPoint(j))[0]},{point(c.CPoint(j))[1]}' for j in range(c.PointCount()));out.append(f'<polygon points="{pts}" fill="#ddeddf"/>')
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA):
   x,y=point(t.GetPosition());out.append(f'<circle cx="{x}" cy="{y}" r="{.3*S}" fill="#777"/><circle cx="{x}" cy="{y}" r="{.15*S}" fill="white"/>')
  elif t.GetLayer()==layer:
   x,y=point(t.GetStart());xx,yy=point(t.GetEnd());out.append(f'<path d="M{x},{y}L{xx},{yy}" stroke="#b45" stroke-width="{p.ToMM(t.GetWidth())*S}" fill="none"/>')
 if layer==p.F_Cu:
  for f in b.GetFootprints():
   for a in f.Pads():
    box=a.GetBoundingBox();x,y=point(box.GetPosition());w=p.ToMM(box.GetWidth())*S;h=p.ToMM(box.GetHeight())*S;out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#d8b85d" stroke="#333"/>');x,y=point(a.GetPosition());out.append(f'<text x="{x}" y="{y+4}" text-anchor="middle">{a.GetNumber()}</text>')
   x,y=point(f.GetPosition()); offsets={'R1':(40,3),'JP1':(40,3),'Q1':(0,-30),'J1':(0,-43),'J2':(0,-42)};dx,dy=offsets.get(f.GetReference(),(0,-25));out.append(f'<text x="{x+dx}" y="{y+dy}" text-anchor="middle" fill="#124">{f.GetReference()}</text>')
 out.append(f'<text x="{ox}" y="650">J1: 1=3V3, 2=GND, 3=GPIO48</text><text x="{ox}" y="675">J2: 1=LED_A, 2=LED_K</text>')
out.append('</svg>');(D/'preview/assembly.svg').write_text(''.join(out))
