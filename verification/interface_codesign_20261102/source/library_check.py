import pcbnew as p,json
from pathlib import Path
D=Path(__file__).resolve().parent;C=D/'candidate';b=p.LoadBoard(str(C/'mainboard_revD.kicad_pcb'));f=next(f for f in b.GetFootprints()if f.GetReference()=='J107');print('board loaded',flush=True);g=p.FootprintLoad(str(C/'GateStudy.pretty'),'J107_DistributedWireLands3_NOFAB');print('lib loaded',bool(g),flush=True);b.Add(g);g.Flip(g.GetPosition(),False);print('flipped',flush=True);g.SetOrientationDegrees(f.GetOrientationDegrees());g.SetPosition(f.GetPosition());print('placed',flush=True);a={q.GetNumber():q for q in f.Pads()};out=[]
for q in g.Pads():
 z=a[q.GetNumber()];out.append({'pad':q.GetNumber(),'lib_xy':[q.GetPosition().x/1e6,q.GetPosition().y/1e6],'board_xy':[z.GetPosition().x/1e6,z.GetPosition().y/1e6],'lib_angle':q.GetOrientationDegrees(),'board_angle':z.GetOrientationDegrees(),'size_equal':q.GetSize()==z.GetSize(),'xy_equal':q.GetPosition()==z.GetPosition(),'shape_equal':q.GetShape()==z.GetShape(),'mask_equal':q.GetLocalSolderMaskMargin()==z.GetLocalSolderMaskMargin()})
(D/'library_check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if len(out)!=3 or not all(r['xy_equal']and r['size_equal']and r['shape_equal']and r['mask_equal']and r['lib_angle']==r['board_angle']for r in out):raise RuntimeError('library geometry does not reproduce native J107')
# Also compare native courtyard polygons and actual per-terminal silk labels after placement.
f.BuildCourtyardCaches();g.BuildCourtyardCaches();a=p.SHAPE_POLY_SET(f.GetCourtyard(p.B_CrtYd));z=p.SHAPE_POLY_SET(g.GetCourtyard(p.B_CrtYd));d=p.SHAPE_POLY_SET(a);d.BooleanSubtract(z);q=p.SHAPE_POLY_SET(z);q.BooleanSubtract(a)
if d.Area()!=0 or q.Area()!=0:raise RuntimeError('library courtyard does not reproduce native')
def texts(fp):return sorted((t.GetText(),t.GetPosition().x,t.GetPosition().y,t.GetTextSize().x,t.GetTextSize().y,t.GetTextThickness(),t.GetLayer())for t in fp.GraphicalItems()if t.GetClass()=='PCB_TEXT')
if texts(f)!=texts(g):raise RuntimeError('library silk does not reproduce native')
(D/'library_check_summary.json').write_text(json.dumps({'pads_exact':True,'courtyards_exact':True,'silk_geometry_exact':True,'source_native_sha256':__import__('hashlib').sha256((C/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest()},indent=2))
