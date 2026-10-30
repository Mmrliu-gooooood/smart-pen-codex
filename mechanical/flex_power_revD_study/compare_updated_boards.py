import sys,json,math
from pathlib import Path
sys.path.extend(['/usr/lib/freecad/lib','/usr/lib/freecad-python3/lib'])
import FreeCAD as A,Part
V=A.Vector;R=Path(__file__).resolve().parent;reports=[]
for variant in ['bias4','href3']:
 E=json.loads((R/'inputs'/f'{variant}_board_extract.json').read_text())['mainboard'];d=A.openDocument(str(R/'D18_STACKED_213_CONDITIONAL_NOFAB.FCStd'))
 for o in list(d.Objects):
  if o.Name.startswith('Main_'):d.removeObject(o.Name)
 d.getObject('Mainboard_XCLK5_12x95').Label='Mainboard_'+variant+'_12x95';d.getObject('Mainboard_XCLK5_12x95').Basis=E['sha256']
 for p in E['parts']:
  if p['dnp']:continue
  a,b,c,dd=p['bounds'];h=p['height']+.15;y=2.9-h if p['back'] else 3.7;o=d.addObject('Part::Feature','Main_'+p['ref']);o.Shape=Part.makeBox(c-a,h,dd-b,V(a-6,y,127-dd));o.addProperty('App::PropertyString','Basis');o.Basis=p['footprint']+'; '+p['height_basis']+' +.15 solder'
 physical=[o for o in d.Objects if o.Name not in ['RF_reserved_UNQUALIFIED','Barrel_OD18_wall1p2_reference']];collisions=[];outside={};inner=Part.makeCylinder(7.8,215,V(0,0,-1));rad=[]
 for i,o in enumerate(physical):
  outside[o.Name]=o.Shape.cut(inner).Volume
  for other in physical[i+1:]:
   v=o.Shape.common(other.Shape).Volume
   if v>1e-6:collisions.append([o.Name,other.Name,v])
  if o.Name.startswith('Main_'):
   bb=o.Shape.BoundBox;rad.append((7.8-max(math.hypot(x,y) for x in [bb.XMin,bb.XMax] for y in [bb.YMin,bb.YMax]),o.Name))
 power=d.getObject('Power14x45_THICKNESS_BUDGET4p15').Shape
 rpt=dict(variant=variant,source_sha256=E['sha256'],release='NOFAB, href3 was moving candidate when extracted' if variant=='href3' else 'NOFAB',actual_footprints=len(E['parts']),back_refs=[p['ref'] for p in E['parts'] if p['back']],collisions=collisions,outside_nonzero={k:v for k,v in outside.items() if v>1e-6},min_main_rect_margin=min(rad),R220_to_power_mm=power.distToShape(d.getObject('Main_R220').Shape)[0])
 stem='D18_STACKED_213_'+variant.upper()+'_NOFAB';d.recompute();d.saveAs(str(R/(stem+'.FCStd')));Part.export(d.Objects,str(R/(stem+'.step')));A.closeDocument(d.Name)
 d=A.openDocument(str(R/(stem+'.FCStd')));rpt['native_valid']=all(o.Shape.isValid() for o in d.Objects if hasattr(o,'Shape'));A.closeDocument(d.Name);s=Part.Shape();s.read(str(R/(stem+'.step')));rpt['step_valid']=s.isValid();reports.append(rpt)
(R/'updated_board_comparison.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports,indent=2))
