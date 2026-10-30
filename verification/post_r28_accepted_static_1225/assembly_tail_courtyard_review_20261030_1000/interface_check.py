from pathlib import Path
import os,sys,json,hashlib,argparse
os.environ['XDG_CONFIG_HOME']='/tmp/interfaces0928';sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part,pcbnew as p
O=Path(__file__).resolve().parent;W=O.parent;F=W/'assembly_clearance_candidate_20261030_0921';parser=argparse.ArgumentParser();parser.add_argument('--board',type=Path,default=F/'tail100/native_placement_ONLY_NOFAB/mainboard_revD.kicad_pcb');args=parser.parse_args();board=args.board.resolve();b=p.LoadBoard(str(board));fps={f.GetReference():f for f in b.GetFootprints()};L=json.load(open(W/'assembly_context_audit_0818_20261030/all103_sync.json'))['rows']
if set(fps)!=set(r['ref']for r in L):raise RuntimeError('103 reference set changed')
for r in L:
 f=fps[r['ref']];pose=[f.GetPosition().x/1e6,f.GetPosition().y/1e6,f.GetOrientationDegrees(),f.GetLayerName()];expected=list(r['current_pose'])
 if r['ref']=='J202':expected[1]=88.8
 if any(abs(a-c)>1e-6 if isinstance(a,(int,float))else a!=c for a,c in zip(pose,expected)):raise RuntimeError('unsupported pose change '+r['ref'])
d=A.openDocument(str(F/'RevD_bench_relief_NOFAB.FCStd'));S={o.Label:o.Shape.copy()for o in d.Objects if hasattr(o,'Shape')};A.closeDocument(d.Name);S['REF_CTX_J202_open'].translate(A.Vector(0,0,1.7));B=2.264793176328504;T=3.194793176328504
# Baseline is preserved; J108 one-piece body explicitly NOT used as actual fitted part.
old=S['REF_CTX_J108'];baseline=[]
for k,s in S.items():
 if k=='REF_CTX_J108' or k=='REF_CTX_main_board':continue
 v=s.common(old).Volume
 if v>1e-7:baseline.append({'other':k,'volume':v})
rows=[]
for pad in fps['J108'].Pads():
 sides=[(p.F_Cu,T,1),(p.B_Cu,B,-1)];active=[(lay,z,sgn)for lay,z,sgn in sides if pad.IsOnLayer(lay)]
 if len(active)!=1:raise RuntimeError('pad not single copper side')
 lay,z,sgn=active[0];x,y=pad.GetPosition().x/1e6,pad.GetPosition().y/1e6
 for radius in [.25,.5]:
  tool=Part.makeCylinder(radius,10,A.Vector(x-7,z,127-y),A.Vector(0,sgn,0));hits=[];near=[]
  for k,s in S.items():
   if k in ['REF_CTX_J108','REF_CTX_main_board','Context_ONLY','REF_Context_ONLY']:continue
   v=tool.common(s).Volume
   if v>1e-7:hits.append({'other':k,'volume':v})
   if k.startswith('REF_CTX_'):near.append((tool.distToShape(s)[0],k))
  rows.append({'pad':pad.GetNumber(),'net':pad.GetNetname(),'xy':[x,y],'side':b.GetLayerName(lay),'radius':radius,'travel':10,'hits':hits,'nearest_components':sorted(near)[:5]})
# Joined interface classification limited to matching actual native pad and named terminal-wire pair.
join=[]
for pad in fps['J103'].Pads():
 n=pad.GetNumber();name='CONTACT'if n=='1'else'GND';target='REF_CTX_J103_'+n;x,y=pad.GetPosition().x/1e6,pad.GetPosition().y/1e6
 if abs(y-52)>1e-6 or abs(x-({'1':3,'2':5.4}[n]))>1e-6:raise RuntimeError('J103 target changed')
 for kind in ['Solder_'+name+'_main_STUDY','Harness_'+name]:
  label='REF_'+kind;s=S[label];v=S[target].common(s).Volume
  if v<=1e-7:raise RuntimeError('expected interface contact absent')
  other='REF_CTX_J103_'+('2'if n=='1'else'1');cross=s.common(S[other]).Volume
  if cross>1e-7:raise RuntimeError('cross-terminal overlap')
  join.append({'pad':n,'net':pad.GetNetname(),'xy':[x,y],'entity':target,'joined':label,'overlap':v,'wrong_terminal_overlap':cross,'classification':'INTENDED_NAMED_SOLDER_TERMINATION_NOT_GENERAL_COLLISION_EXEMPTION'})
neg=Part.makeCylinder(.5,10,A.Vector(2.5-7,T,127-16.975),A.Vector(0,1,0));wrong_side=neg.common(S['REF_CTX_C101']).Volume
if wrong_side<=1e-7:raise RuntimeError('wrong-side negative control did not fail')
result={'wrong_side_BOOT_negative_volume':wrong_side,'board':str(board),'board_sha256':hashlib.sha256(board.read_bytes()).hexdigest(),'all103_pose_verified':True,'J108_baseline_fictitious_body_collisions':baseline,'J108_mixed_side_parametric_access':rows,'J103_exact_joined_interfaces':join,'status':'MODEL_SEMANTIC_CORRECTION_AND_ACCESS_CANDIDATE_NOFAB_NOPOWER','limitations':'No probe fixture selected. Radius/runout/registration, force, mask, material, wire strain relief remain unqualified. Historical body box retained in baseline; no physical envelope shrunk.'};(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print('J108 baseline',baseline);print('J108 routes',[(r['pad'],r['side'],r['radius'],r['hits'],r['nearest_components'][0])for r in rows]);print('J103',join)
