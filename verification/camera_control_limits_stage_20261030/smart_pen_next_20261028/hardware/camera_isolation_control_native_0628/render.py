from pathlib import Path
import json,os
os.environ['XDG_CONFIG_HOME']='/tmp/isorender0628'
import pcbnew as p
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));m=json.load(open(D/'materialization.json'));new=set(m['added']);colors={'CAM_ISO_OE_N':'#ae2363','CAM_IO_EN':'#175dba','IO_ENABLE_LINK':'#00826b','3V3_AON':'#b77a00'}
s=['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="2000" viewBox="0 0 960 2000"><rect width="960" height="2000" fill="white"/><text x="20" y="30" font-family="sans-serif" font-size="21">Camera isolation control — research / NO FAB / NO POWER</text>']
for j,l in enumerate([p.F_Cu,p.In3_Cu,p.B_Cu]):
 ox=15+j*315;oy=100;sc=18
 s.append(f'<text x="{ox}" y="75" font-family="sans-serif" font-size="18">{b.GetLayerName(l)}</text>')
 def pt(a):return(ox+a.x/1e6*sc,oy+a.y/1e6*sc)
 for f in b.GetFootprints():
  for q in f.Pads():
   if not q.IsOnLayer(l):continue
   x,y=pt(q.GetPosition());w=q.GetSize().x/1e6*sc;h=q.GetSize().y/1e6*sc
   if round(q.GetOrientationDegrees())%180==90:w,h=h,w
   s.append(f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" fill="#aaa"/>')
 for t in b.GetTracks():
  if not t.IsOnLayer(l):continue
  a,z=pt(t.GetStart()),pt(t.GetEnd());v=isinstance(t,p.PCB_VIA);c=colors.get(t.GetNetname(),'#777')if t.m_Uuid.AsString()in new else'#bbb';w=(t.GetWidth(p.F_Cu)if v else t.GetWidth())/1e6*sc
  s.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{z[0]}" y2="{z[1]}" stroke="{c}" stroke-width="{w}" stroke-linecap="round"/>')
 s.append(f'<text x="{ox}" y="1945" font-family="sans-serif" font-size="12">All prior copper retained; new colored routes only.</text>')
s.append('</svg>');(D/'layers.svg').write_text(''.join(s))
r=json.load(open(D/'reference_delta.json'))['rows'][0];s=['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="640" viewBox="0 0 800 640"><rect width="800" height="640" fill="white"/><text x="20" y="30" font-family="sans-serif" font-size="19">CAM_ON added reference edge gap — not SI qualified</text>'];ox=100;oy=80;sc=300
# local y-down coordinate crop
pt=lambda a:(ox+(a[0]-6)*sc,oy+(a[1]-69.7)*sc)
for h in r['holes']:
 ps=[pt(a)for a in h['contour']];s.append('<polygon points="'+' '.join(f'{x},{y}'for x,y in ps)+'" fill="#eee" stroke="#999"/>')
 for v in h['via_centers']:
  x,y=pt(v['xy']);s.append(f'<circle cx="{x}" cy="{y}" r="{.225*sc}" fill="none" stroke="#1565a3"/><text x="{x+8}" y="{y-10}" font-size="12">{v["net"]}</text>')
a,z=pt(r['a']),pt(r['b']);s.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{z[0]}" y2="{z[1]}" stroke="#b77a00" stroke-width="{r["width"]*sc}"/>')
for poly in r['loss_contours']:
 s.append('<polygon points="'+' '.join(f'{x},{y}'for x,y in map(pt,poly))+'" fill="red"/>')
s.append('<text x="20" y="610" font-family="sans-serif" font-size="15">Red: +0.001488810274 mm²; no additional centerline gap. Merged 3-via hole retained.</text></svg>');(D/'reference.svg').write_text(''.join(s))
