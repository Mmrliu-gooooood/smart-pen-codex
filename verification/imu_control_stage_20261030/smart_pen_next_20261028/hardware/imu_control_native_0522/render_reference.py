from pathlib import Path
import reference_delta as r
p=r.p;D=r.D;scale=480.;xmin=3.6;ymin=79.15
xy=lambda a:(80+(a[0]-xmin)*scale,95+(a[1]-ymin)*scale)
def path(poly):
 out=[]
 for ch in r.chains(poly):
  pts=[xy((ch.CPoint(i).x/1e6,ch.CPoint(i).y/1e6))for i in range(ch.PointCount())];out.append('M'+' L'.join(f'{x:.6f},{y:.6f}'for x,y in pts)+' Z')
 return' '.join(out)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000">','<rect width="1000" height="1000" fill="white"/>','<text x="40" y="32" font-family="sans-serif" font-size="22" font-weight="bold">Actual native merged hole / EXTCLK reference delta</text>','<text x="40" y="59" font-family="sans-serif" font-size="15">In2 and In4 have the same measured local delta. NO SI / manufacturing approval.</text>','<defs><clipPath id="plot"><rect x="80" y="95" width="816" height="720"/></clipPath></defs>','<rect x="80" y="95" width="816" height="720" fill="#dcebdc" stroke="#666"/>','<g clip-path="url(#plot)">']
for model,style in[(r.b[p.In4_Cu],'fill="white" stroke="#222" stroke-width="1.5"'),(r.a[p.In4_Cu],'fill="none" stroke="#8863a8" stroke-width="2" stroke-dasharray="6 5"')]:
 for oi in range(model.OutlineCount()):
  for hi in range(model.HoleCount(oi)):
   h=p.SHAPE_POLY_SET();h.AddOutline(model.Hole(oi,hi));bb=h.BBox()
   if bb.GetRight()/1e6<3.6 or bb.GetX()/1e6>5.3 or bb.GetBottom()/1e6<79.15 or bb.GetY()/1e6>80.65:continue
   svg.append(f'<path d="{path(h)}" {style}/>')
strip=r.shape(r.t,r.t.GetLayer());svg.append(f'<path d="{path(strip)}" fill="#2f83bd" opacity=".35"/>');svg.append(f'<path d="{path(r.extra)}" fill="#d22c43"/>')
x,y=xy((4.25,79.15));_,z=xy((4.25,80.65));svg.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{z}" stroke="#00538b" stroke-width="1.5" stroke-dasharray="5 4"/>')
for a,label,col in[((4.25,79.7),'Existing EXTCLK via','#1264a3'),((4.7,80.125),'New IRQ via','#bc5800')]:
 x,y=xy(a);svg.append(f'<circle cx="{x}" cy="{y}" r="108" fill="none" stroke="{col}" stroke-width="3"/><circle cx="{x}" cy="{y}" r="48" fill="white" stroke="{col}"/>');svg.append(f'<text x="{x+115}" y="{y}" font-family="sans-serif" font-size="14" fill="{col}">{label}</text>')
svg+=['</g>','<text x="40" y="850" font-family="sans-serif" font-size="15">Green: actual reference plane. White/black: native hole. Purple dashed: parent hole.</text>','<text x="40" y="877" font-family="sans-serif" font-size="15">Blue: unchanged .15mm clock strip/centerline. Red: additional uncovered projection.</text>','<text x="40" y="904" font-family="sans-serif" font-size="15">Added loss .0017414094705mm² per plane; band y-span .107654mm; centerline gap unchanged.</text>','<text x="40" y="931" font-family="sans-serif" font-size="15">IRQ nearest core GND via (2.65,83.3): center distance3.779302mm, outside this crop.</text>','<text x="40" y="958" font-family="sans-serif" font-size="15">Do not infer pass/fail from area alone. Actual contours/return behavior require independent review.</text>','</svg>']
(D/'reference_delta.svg').write_text('\n'.join(svg)+'\n')
