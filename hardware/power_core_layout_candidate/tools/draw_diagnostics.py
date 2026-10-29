#!/usr/bin/python3
from pathlib import Path
import pcbnew as p,json,html
D=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(D/'power_core_NOFAB.kicad_pcb'));S=23;ox=35;oy=40
colors={'SW_L1':'#d97706','SW_L2':'#d97706','REG_FB':'#2563eb','GND':'#777','SYS_RAW':'#b91c1c','3V3_AON':'#b91c1c','VBUS_5V':'#b91c1c','PACK_PLUS_PROTECTED':'#b91c1c'}
def xy(q):return ox+p.ToMM(q.x)*S,oy+p.ToMM(q.y)*S
def color(n):return colors.get(n.lstrip('/'),'#9333aa')
s=['<svg xmlns="http://www.w3.org/2000/svg" width="950" height="900" viewBox="0 0 950 900"><rect width="950" height="900" fill="white"/>',f'<rect x="{ox}" y="{oy}" width="{12*S}" height="{35*S}" fill="#fafafa" stroke="black"/>']
for q in b.GetTracks():
 if isinstance(q,p.PCB_VIA):
  x,y=xy(q.GetPosition());s.append(f'<circle cx="{x}" cy="{y}" r="{.3*S}" fill="{color(q.GetNetname())}"/><circle cx="{x}" cy="{y}" r="{.15*S}" fill="white"/>')
 elif q.GetLayer()==p.F_Cu:
  x,y=xy(q.GetStart());xx,yy=xy(q.GetEnd());s.append(f'<path d="M{x},{y} L{xx},{yy}" stroke="{color(q.GetNetname())}" stroke-width="{p.ToMM(q.GetWidth())*S}" fill="none" stroke-linecap="round"/>')
legend=[]
for f in sorted(b.GetFootprints(),key=lambda f:f.GetReference()):
 for a in f.Pads():
  x,y=xy(a.GetPosition());w=p.ToMM(a.GetSize().x)*S;h=p.ToMM(a.GetSize().y)*S;s.append(f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" fill="{color(a.GetNetname())}" transform="rotate({-a.GetOrientationDegrees()} {x} {y})"/>')
  if a.GetNumber()=='1':s.append(f'<text x="{x}" y="{y+3}" text-anchor="middle" font-family="sans-serif" font-size="8" fill="white">1</text>')
 x,y=xy(f.GetPosition());s.append(f'<text x="{x}" y="{y+3}" text-anchor="middle" font-family="sans-serif" font-size="10" fill="black" stroke="white" stroke-width="2" paint-order="stroke">{f.GetReference()}</text>');legend.append(f'{f.GetReference()}: {f.GetValue()}')
notes=['POWER CORE LAYOUT-P0 | NO FAB','12 x 35 x 0.8 mm / 4 layers','Diagnostic top-copper drawing, not Gerber','Orange: SW_L1 / SW_L2; blue: feedback','Red: power rails; purple: slow controls','Gray: GND; In1 continuous filled GND','In2 SYS island + local slow controls','JP1 is physically OPEN / true DNP','All wire lands: strain relief unqualified','Pin 1 marked on every footprint','SW outline closes through devices: approximate','FB stays below IC; switch routes stay above','Input/output cap return contacts checked','Not thermal, EMC or charge approval']
for i,t in enumerate(notes):s.append(f'<text x="350" y="{40+i*21}" font-family="sans-serif" font-size="14">{html.escape(t)}</text>')
for i,t in enumerate(legend):s.append(f'<text x="350" y="{360+i*20}" font-family="sans-serif" font-size="13">{html.escape(t)}</text>')
s.append('</svg>');(D/'preview/assembly_diagnostic.svg').write_text('\n'.join(s))
