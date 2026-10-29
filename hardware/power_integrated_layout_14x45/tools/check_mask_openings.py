from pathlib import Path
import pcbnew as p,json,math
D=Path(__file__).resolve().parents[1];fp=p.FootprintLoad(str(D/'SmartPenThermal.pretty'),'TI_DSE0006A_SMDleft_ExposedDerived_NOFAB');rows=[]
for a in fp.Pads():
 n=int(a.GetNumber())
 if n>3:continue
 assert a.IsOnLayer(p.F_Cu) and not a.IsOnLayer(p.F_Mask) and not a.IsOnLayer(p.F_Paste)
 x=p.ToMM(a.GetPosition().x);y=p.ToMM(a.GetPosition().y);w=.8 if n==1 else .7;h=.25;r=.05
 for layer in [p.F_Mask,p.F_Paste]:
  gs=[g for g in fp.GraphicalItems() if g.GetLayer()==layer and abs(p.ToMM(g.GetCenter().y)-y)<.15]
  assert len(gs)==6
  rects=[g for g in gs if g.GetShape()==p.SHAPE_T_RECT];circles=[g for g in gs if g.GetShape()==p.SHAPE_T_CIRCLE];assert len(rects)==2 and len(circles)==4
  got=set()
  for g in gs:assert g.IsFilled() and g.GetWidth()==0
  for g in circles:
   assert abs(p.ToMM(g.GetRadius())-.05)<1e-6
   got.add((round(p.ToMM(g.GetCenter().x),6),round(p.ToMM(g.GetCenter().y),6)))
  expected={(round(x+dx*(w/2-r),6),round(y+dy*(h/2-r),6)) for dx in [-1,1] for dy in [-1,1]};assert got==expected
  sizes=sorted((round(p.ToMM(g.GetEnd().x-g.GetStart().x),6),round(p.ToMM(g.GetEnd().y-g.GetStart().y),6)) for g in rects);assert sizes==sorted([(round(w,6),.15),(round(w-.1,6),.25)])
  rows.append({'pin':n,'layer':p.LayerName(layer),'opening_width_mm':w,'height_mm':h,'corner_radius_mm':r,'analytic_union_area_mm2':w*h-(4-math.pi)*r*r,'primitive_counts':{'filled_rectangles':2,'filled_circles':4}})
(D/'mask_geometry_check.json').write_text(json.dumps({'status':'PASS actual native shape readback; DFM not approved','openings':rows},indent=2))
# SVG contains the ACTUAL shape coordinates, not a substituted ideal roundrect.
s=['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="580" viewBox="-1.5 -1 3 2.3"><rect x="-1.5" y="-1" width="3" height="2.3" fill="white"/>']
for a in fp.Pads():
 x=p.ToMM(a.GetPosition().x);y=p.ToMM(a.GetPosition().y);w=p.ToMM(a.GetSize().x);h=p.ToMM(a.GetSize().y);s.append(f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx=".05" fill="#dbb56a"/>')
for g in fp.GraphicalItems():
 if g.GetLayer()!=p.F_Mask:continue
 if g.GetShape()==p.SHAPE_T_RECT:
  a=g.GetStart();z=g.GetEnd();s.append(f'<rect x="{p.ToMM(a.x)}" y="{p.ToMM(a.y)}" width="{p.ToMM(z.x-a.x)}" height="{p.ToMM(z.y-a.y)}" fill="#287ca1"/>')
 elif g.GetShape()==p.SHAPE_T_CIRCLE:
  a=g.GetCenter();s.append(f'<circle cx="{p.ToMM(a.x)}" cy="{p.ToMM(a.y)}" r="{p.ToMM(g.GetRadius())}" fill="#287ca1"/>')
s.append('<text x="-1.4" y="1" font-size=".09">Left blue: actual mask union R0.05; gold: copper</text></svg>');(D/'preview/dse_mask_actual.svg').write_text(''.join(s));print('PASS six explicit R0.05 openings')
