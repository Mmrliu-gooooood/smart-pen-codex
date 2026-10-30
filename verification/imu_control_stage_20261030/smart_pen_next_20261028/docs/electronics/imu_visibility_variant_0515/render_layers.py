from pathlib import Path
import sys,json,html
D=Path(__file__).resolve().parent;R=D.parents[2];sys.path.insert(0,str(R/'docs/electronics/imu_control_joint_plan_0444'));import geometry as g
p=g.p;m=json.loads((D/'strategy1.json').read_text());colors={'AON_I2C_SCL':'#1264a3','AON_I2C_SDA':'#00866b','PICKUP_INT_N':'#bc5800','3V3_AON':'#ae2f68'}
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="2250" viewBox="0 0 1000 2250">','<rect width="1000" height="2250" fill="white"/>','<text x="24" y="28" font-family="sans-serif" font-size="21" font-weight="bold">IMU complete connectivity model — NOT NATIVE / NO FAB / NO POWER</text>']
for i,(net,c)in enumerate(colors.items()):svg.append(f'<text x="{24+i*245}" y="54" font-family="sans-serif" font-size="14" fill="{c}">{net}</text>')
for j,l in enumerate([p.F_Cu,p.In3_Cu,p.B_Cu]):
 ox=28+j*330;oy=225;sc=20
 def xy(a):return(ox+a[0]*sc,oy+a[1]*sc)
 def line(a,b,w,c,opacity=1):
  x,y=xy(a);u,v=xy(b);svg.append(f'<line x1="{x}" y1="{y}" x2="{u}" y2="{v}" stroke="{c}" stroke-width="{w*sc}" stroke-linecap="round" opacity="{opacity}"/>')
 svg.append(f'<text x="{ox}" y="83" font-family="sans-serif" font-size="18">{g.b.GetLayerName(l)}</text>')
 for item in g.b.GetDrawings():
  if item.GetLayer()==p.Edge_Cuts:line([item.GetStart().x/1e6,item.GetStart().y/1e6],[item.GetEnd().x/1e6,item.GetEnd().y/1e6],.05,'#222')
 for q in g.pads:
  if not q.IsOnLayer(l):continue
  sh=g.shape(q,l);polys=[]
  for k in range(sh.OutlineCount()):
   chain=sh.COutline(k);points=[xy((chain.CPoint(i).x/1e6,chain.CPoint(i).y/1e6))for i in range(chain.PointCount())];polys.append('M'+' L'.join(f'{x},{y}'for x,y in points)+' Z')
  svg.append('<path d="'+' '.join(polys)+'" fill="#c3c6ca"/>')
 for t in g.old:
  if t.m_Uuid.AsString()in m['removed']or not t.IsOnLayer(l):continue
  if isinstance(t,p.PCB_VIA):
   x,y=xy(g.xy(t));svg.append(f'<circle cx="{x}" cy="{y}" r="{t.GetWidth(p.F_Cu)/2e6*sc}" fill="#bbb"/><circle cx="{x}" cy="{y}" r="{t.GetDrillValue()/2e6*sc}" fill="white"/>')
  else:line([t.GetStart().x/1e6,t.GetStart().y/1e6],[t.GetEnd().x/1e6,t.GetEnd().y/1e6],t.GetWidth()/1e6,'#aaa',.75)
 for ts in m['parts'].values():
  for t in ts:
   c=colors[t['net']]
   if t['type']=='via':
    x,y=xy(t['a']);svg.append(f'<circle cx="{x}" cy="{y}" r="{t["width"]/2*sc}" fill="{c}"/><circle cx="{x}" cy="{y}" r="{t["drill"]/2*sc}" fill="white"/>')
   elif t['layer']==g.b.GetLayerName(l):line(t['a'],t['b'],t['width'],c)
 for f in g.b.GetFootprints():
  if f.GetReference()in ['U101','U501','R501','R502','J107','JP201']:
   a=f.GetPosition();x,y=xy((a.x/1e6,a.y/1e6));svg.append(f'<text x="{x+3}" y="{y-5}" font-family="sans-serif" font-size="11" fill="#333">{html.escape(f.GetReference())}</text>')
svg+=['<text x="24" y="2190" font-family="sans-serif" font-size="14">Gray: retained source copper/pads. Colored: new model objects. Plane copper intentionally not shown.</text>','<text x="24" y="2212" font-family="sans-serif" font-size="14">Numerous grid micro-turns, courtyard/process gates and all hardware tests remain unresolved.</text>','</svg>']
(D/'layers.svg').write_text('\n'.join(svg)+'\n')
import xml.etree.ElementTree as ET;ET.parse(D/'layers.svg')
