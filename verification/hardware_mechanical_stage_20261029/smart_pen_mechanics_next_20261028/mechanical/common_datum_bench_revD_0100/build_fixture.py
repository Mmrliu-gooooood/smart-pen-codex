import sys,json,math,hashlib
from pathlib import Path
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
R=Path(__file__).resolve().parent;V=A.Vector
src=R.parent/'contact_oblique_harness_revC_0038/contact_oblique_harness.FCStd';d=A.openDocument(str(src));context={o.Name:o.Shape.copy() for o in d.Objects if hasattr(o,'Shape')};A.closeDocument(d.Name)
def box(x0,x1,y0,y1,z0,z1):return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cyl(r,z0,z1,x=0,y=-3.8):return Part.makeCylinder(r,z1-z0,V(x,y,z0))
B=2.264793176328504;F=B+.93
base=box(-25,25,-16,-11,20,124).fuse(box(-25,-10,-16,-11,124,138))
# Common base includes independent cassette cradle, PCB edge posts, and left-side axial stops.
parts={}
for z in [45,95]:
 for side in [-1,1]:
  x0,x1=(-12,-7.5) if side<0 else(7.5,12)
  post=box(x0,x1,-11,B,z-2,z+2)
  # Fixed B datum; three primary pads, fourth backed off .1 to avoid 4-point forced flattening.
  y=B if(z,side)!=(95,1)else B-.1
  ledge=box(-7.5,-6.75,y-.7,y,z-1,z+1) if side<0 else box(6.75,7.5,y-.7,y,z-1,z+1)
  base=base.fuse(post).fuse(ledge)
  # Detachable keeper, height adjusted using actual board thickness/shims, not fixed maxthickness pressure.
  cap=box(-12,-6.75,F,F+1.5,z-1,z+1) if side<0 else box(6.75,12,F,F+1.5,z-1,z+1)
  sx=side*10
  cap=cap.cut(Part.makeCylinder(.9,3,V(sx,F-.1,z),V(0,1,0)))
  base=base.cut(Part.makeCylinder(.8,8,V(sx,B-6,z),V(0,1,0)))
  parts[f'PCB_keeper_{side}_{z}']=cap
  parts[f'Keeper_hardstop_spacer_{side}_{z}']=Part.makeCylinder(1.5,F-B,V(sx,B,z),V(0,1,0)).cut(Part.makeCylinder(.9,F-B+.2,V(sx,B-.1,z),V(0,1,0)))
  # Reuse exact previously documented M1.6x8 head/shaft envelope, threads suppressed.
  parts[f'Keeper_screw_{side}_{z}']=Part.makeCylinder(.8,8,V(sx,F+1.5-8,z),V(0,1,0)).fuse(Part.makeCylinder(1.5,1.6,V(sx,F+1.5,z),V(0,1,0)))
# Head datum Z32 and tail positive stop on nonradiator left edge at Z133.5.
base=base.fuse(box(-12,-5,-11,B+1,30.5,32))
base=base.fuse(box(-12,-5,-11,B-1,132.5,137))
tail=box(-12,-5,B-1,B+1,132.5,136.5).cut(box(-7,-4,B-1.1,B+1.1,132.4,133.5))
slot=Part.makeCylinder(.9,3,V(-10,B-1.1,134),V(0,1,0)).fuse(Part.makeCylinder(.9,3,V(-10,B-1.1,135),V(0,1,0))).fuse(box(-10.9,-9.1,B-1.1,B+1.9,134,135))
parts['Tail_stop_adjustable_pm0p5']=tail.cut(slot).removeSplitter()
base=base.cut(Part.makeCylinder(.8,8,V(-10,B-7,134.5),V(0,1,0)))
parts['Tail_stop_screw']=Part.makeCylinder(.8,8,V(-10,B+1-8,134.5),V(0,1,0)).fuse(Part.makeCylinder(1.5,1.6,V(-10,B+1,134.5),V(0,1,0)))
# Right edge adjustable locating shims: .5 nominal space, fitted after actual PCB width measurement.
for z in [45,95]:
 parts['PCB_side_shim_R_'+str(z)]=box(7,7.5,B+.1,F-.1,z-.6,z+.6)
 parts['PCB_side_shim_L_'+str(z)]=box(-7.5,-7,B+.1,F-.1,z-.6,z+.6)

# Tail stop joins only left external arm; no bridge beneath/through RF region x[-1.5,5],z[127,133.5].
# Split collar at z69..72: installed clearance .2 radial. Shim qualification is explicitly required.
bottom=box(-7,7,-11,-3.8,69,72).cut(cyl(4.0,68.9,72.1))
base=base.fuse(bottom)
cap=cyl(5.0,69,72).common(box(-6,6,-3.8,2,68.9,72.1)).cut(cyl(4.0,68.9,72.1))
for x in [-6.2,6.2]:
 cap=cap.fuse(box(x-1.5,x+1.5,-3.8,-1.8,69,72))
 base=base.fuse(box(x-1.5,x+1.5,-11,-3.8,69,72))
 cap=cap.cut(Part.makeCylinder(.9,3,V(x,-4,70.5),V(0,1,0)))
 base=base.cut(Part.makeCylinder(.8,8,V(x,-10,70.5),V(0,1,0)))
 parts['Collar_screw_'+str(x)]=Part.makeCylinder(.8,8,V(x,-9.8,70.5),V(0,1,0)).fuse(Part.makeCylinder(1.5,1.6,V(x,-1.8,70.5),V(0,1,0)))
parts['Cassette_top_collar']=cap.removeSplitter()
# Trial conformal shims fill measured ring gap; no claim of elastic compound, preload or retention qualification.
ring=cyl(4,69,72).cut(cyl(3.8,68.9,72.1))
parts['Cassette_lower_shim_TRIAL']=ring.common(box(-5,5,-9,-3.8,68,73));parts['Cassette_upper_shim_TRIAL']=ring.common(box(-5,5,-3.8,2,68,73))
# Rectangular front flange fork gives axial capture and anti-rotation independently of round collar friction.
for side in [-1,1]:
 x0,x1=(3.6,8) if side>0 else(-8,-3.6)
 fork=box(x0,x1,-11,-.3,63.4,68.6)
 for z0,z1 in [(63.4,64.3),(67.7,68.6)]:
  fork=fork.fuse(box(2.8,7,-1.1,-.3,z0,z1)if side>0 else box(-7,-2.8,-1.1,-.3,z0,z1))
 fork=fork.cut(cyl(4,63.3,68.7))
 sx=side*6
 # Open-ended key groove allows sideways jaw insertion around the seated cassette.
 boss=box(sx-1.5,sx+1.5,-11,-10,64.5,67.5)
 base=base.fuse(boss).cut(Part.makeCylinder(.8,7,V(sx,-16.1,66),V(0,1,0)))
 fork=fork.cut(box(x0-.1,x1+.1,-11.1,-9.9,64.4,67.6))
 fork=fork.cut(Part.makeCylinder(.9,5,V(sx,-11.1,66),V(0,1,0))).cut(Part.makeCylinder(1.6,8,V(sx,-7,66),V(0,1,0)))
 if side>0:fork=fork.cut(Part.makeCylinder(1.6,5,V(3.4,.6,66),V(1,0,0)))
 parts['Fork_jaw_'+('R'if side>0 else'L')]=fork.removeSplitter()
 for zz0,zz1,label in [(64.4,64.5,'front'),(67.5,67.6,'rear')]:parts['Fork_keyshim_'+('R'if side>0 else'L')+'_'+label]=box(sx-1.5,sx+1.5,-11,-10,zz0,zz1)
 parts['Fork_screw_'+('R'if side>0 else'L')]=Part.makeCylinder(.8,8,V(sx,-15,66),V(0,1,0)).fuse(Part.makeCylinder(1.5,1.6,V(sx,-7,66),V(0,1,0)))
 # .1 nominal axial shims against the flange, adjusted from actual measurement.
 for z0,z1 in [(64.3,64.4),(67.6,67.7)]:parts[f'Axial_shim_{side}_{z0}']=box(2.9,3.5,-1.1,-.3,z0,z1)if side>0 else box(-3.5,-2.9,-1.1,-.3,z0,z1)
 parts[f'Antirot_shim_{side}']=box(3.5,3.6,-2.25,-1.0,65,67)if side>0 else box(-3.6,-3.5,-2.25,-1.0,65,67)
# Relief for actual cassette front screw head; do not bury it in the antirotation fork.
relief=Part.makeCylinder(1.6,5,V(3.4,.6,66),V(1,0,0))
base=base.cut(relief)
parts['Antirot_shim_1']=parts['Antirot_shim_1'].cut(relief).removeSplitter()
parts['Common_base']=base.removeSplitter()
hits=[]
for n,s in parts.items():
 for m,t in context.items():
  v=s.common(t).Volume
  if v>1e-7:hits.append([n,m,v])
local=[]
for i,(n,s) in enumerate(parts.items()):
 for m,t in list(parts.items())[i+1:]:
  v=s.common(t).Volume
  if v>1e-7:local.append([n,m,v])
# Conservative project RF prism uses exact native rule-area projection, full Y extent beyond fixture.
rf=box(-1.5,5,-20,20,127,133.5);rfhits={k:s.common(rf).Volume for k,s in parts.items()if s.common(rf).Volume>1e-7}
doc=A.newDocument('CommonDatumBenchRevD')
for n,s in parts.items():o=doc.addObject('Part::Feature',n);o.Label=n;o.Shape=s
for n,s in context.items():o=doc.addObject('Part::Feature','REF_'+n);o.Label='REF_'+n;o.Shape=s
doc.recompute();doc.saveAs(str(R/'common_datum_bench.FCStd'));A.closeDocument(doc.Name)
doc=A.openDocument(str(R/'common_datum_bench.FCStd'));valid=all(o.Shape.isValid()for o in doc.Objects if hasattr(o,'Shape'));A.closeDocument(doc.Name)
nat=json.loads((R/'native_contract.json').read_text())
if hashlib.sha256(Path(nat['source']).read_bytes()).hexdigest()!=nat['sha256']:raise ValueError('PCB changed')
res=dict(native_sha256=nat['sha256'],status='INITIAL_FIXTURE_NOFAB_NOT_BARREL',source_cad_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),context_collisions=hits,fixture_collisions=local,RF_project_prism_collisions=rfhits,reopen_valid=valid,part_solid_counts={k:len(s.Solids)for k,s in parts.items()},pcb_datums=dict(B=B,F_at_max_thickness=F,Z_head=32,Z_tail=133.5,edge_x=[-7,7],contact_engagement=.25,clamp_Z=[45,95]),cassette_capture=dict(collar_Z=[69,72],collar_inner_radius=4,axis=[0,-3.8],front_flange_Z=[64.4,67.6],axial_trial_shims=.1,radial_trial_shim=.2),native_RF_rule=[5.5,-6.5,12,0])
(R/'fixture_results.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
