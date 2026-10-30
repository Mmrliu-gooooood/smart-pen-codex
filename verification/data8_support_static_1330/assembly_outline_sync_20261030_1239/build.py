from pathlib import Path
import sys,json,hashlib,os
os.environ['XDG_CONFIG_HOME']='/tmp/outline1239';sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A,Part
import subprocess
R=Path(__file__).resolve().parent;W=R.parent;O=Path(os.environ.get('OUTLINE_OUTPUT',str(R)));O.mkdir(parents=True,exist_ok=True);B=2.264793176328504;T=.93;F=B+T
src=W/'smart_pen_next_20261028/hardware/sccb_local_reference_1216/native/mainboard_revD.kicad_pcb';SHA='dcbd2e6501c8294ece5ecf7b41ffcc86ccc7f58f7cb54ececfdf24962a50f697'
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
def check(v,msg):
 if not v:raise RuntimeError(msg)
def box(bb):return Part.makeBox(*[bb[k+3]-bb[k]for k in range(3)],A.Vector(*bb[:3]))
def bounds(s):
 b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def hit(a,b):
 x,y=bounds(a),bounds(b)
 if any(min(x[k+3],y[k+3])-max(x[k],y[k])<=1e-8 for k in range(3)):return 0.
 return a.common(b).Volume
check(sha(src)==SHA,'PCB binding')
extract="""import pcbnew as p,json,sys
b=p.LoadBoard(sys.argv[1]);es=[]
for g in b.GetDrawings():
 if g.GetLayer()==p.Edge_Cuts:
  if g.GetShape()!=p.SHAPE_T_SEGMENT:raise RuntimeError('nonsegment')
  es.append([[g.GetStart().x/1e6,g.GetStart().y/1e6],[g.GetEnd().x/1e6,g.GetEnd().y/1e6]])
print(json.dumps({'edges':es,'thickness':b.GetDesignSettings().GetBoardThickness()/1e6}))
"""
native=json.loads(subprocess.check_output(['/usr/bin/python3','-c',extract,str(src)],text=True));edges=native['edges'].copy()
chain=[edges.pop(0)[0]]
# Re-read all edges so ordering and direction come only from native connectivity.
edges=native['edges'].copy()
while edges:
 found=False
 for i,(a,b)in enumerate(edges):
  if chain[-1]in[a,b]:chain.append(b if chain[-1]==a else a);edges.pop(i);found=True;break
 check(found,'outline disconnected')
check(chain[0]==chain[-1]and len(chain)==7,'one six-edge closed outline')
pts=[A.Vector(x-7,B,127-y)for x,y in chain];face=Part.Face(Part.makePolygon(pts));exact=face.extrude(A.Vector(0,T,0));old=box([-7,B,32,7,F,133.5]);check(abs(face.Area-1372.2)<1e-6,'native area');check(abs(exact.Volume-1276.146)<1e-6,'volume');check(exact.cut(old).Volume<1e-8,'subset');check(exact.isValid(),'valid')
I=json.load(open(W/'assembly_context_audit_0818_20261030/inventory.json'));M=json.load(open(W/'assembly_dvp_route_masks_20261030_1228/route_masks_y20_38.json'));check(M['basis_sha256']==SHA,'envelope binding');env=[]
for r in M['all_static_rectangles']:
 x0,y0,x1,y1=r['xy_bounds'];lo,hi=(F,F+r['height'])if r['side']=='F.Cu'else(B-r['height'],B);env.append((r,box([x0-7,lo,127-y1,x1-7,hi,127-y0])))
check(len(env)==104 and len(set(r['ref']for r,s in env))==97,'full static ledger count');check(len(M['unqualified_operations'])==6,'operation records')
result={'pcb_sha256':SHA,'native_vertices':chain,'native_thickness_attribute_mm':native['thickness'],'budget_thickness_mm':T,'transform':'X=x-7; Z=127-y; B Y=2.264793176328504; F budget Y=B+.93','outline_bounds':bounds(exact),'native_area_mm2':face.Area,'board_volume_mm3':exact.Volume,'historical_rectangle_volume_mm3':old.Volume,'removed_mm3':old.cut(exact).Volume,'static_ref_count':97,'static_entity_count':104,'operation_refs':M['unqualified_operations'],'contexts':[]}
for c in I['contexts']:
 q=Path(c['path']);check(sha(q)==c['sha256'],'source CAD hash');sd=A.openDocument(str(q));pre='CTX_'if c['context']=='RevC'else'REF_CTX_';mechanical=[]
 for obj in sd.Objects:
  if not hasattr(obj,'Shape')or obj.TypeId=='App::DocumentObjectGroup' or obj.Shape.isNull():continue
  if obj.Label.startswith(pre)or obj.Label in ['Context_ONLY','REF_Context_ONLY']:continue
  mechanical.append((obj.Label,obj.Shape.copy()))
 A.closeDocument(sd.Name);d=A.newDocument('SYNC_'+c['context']);items=[]
 def add(label,s,kind):
  ob=d.addObject('Part::Feature','Item');ob.Label=label;ob.Shape=s;ob.addProperty('App::PropertyString','Status');ob.Status=kind;items.append(ob);return ob
 for label,s in mechanical:add(label,s,'Historical geometry unchanged; NOT manufacturing qualified')
 add('Native_outline_dcbd_99p8_t0p93_NOFAB',exact,'Exact native XY; .93 thickness budget, NOT measured finished thickness')
 for k,(r,s)in enumerate(env):add('INSTALL_'+r['ref']+'_'+str(k),s,r['basis'])
 for r in M['unqualified_operations']:
  ob=d.addObject('App::FeaturePython','OperationGate');ob.Label='UNQUALIFIED_OPERATION_'+r['ref'];ob.addProperty('App::PropertyString','Evidence');ob.Evidence=json.dumps(r)
 d.recompute();path=O/(c['context']+'_exact_outline_NOFAB.FCStd');d.saveAs(str(path));Part.export(items,str(O/(c['context']+'_exact_outline_NOFAB.step')))
 collisions=[]
 for label,s in mechanical:
  ov=hit(old,s);nv=hit(exact,s)
  if ov>1e-7 or nv>1e-7:collisions.append({'object':label,'historical_rectangle_overlap_mm3':ov,'exact_outline_overlap_mm3':nv})
  check(nv<=ov+1e-6,'subset must not create board collision')
 row={'context':c['context'],'source_sha256':c['sha256'],'mechanical_objects':len(mechanical),'board_collisions':collisions,'file':path.name,'board_valid':exact.isValid(),'mechanical_changed':False,'head_datum_nominal_gap_mm':1.7 if c['context']!='RevC'else None,'right_RF_X_finger_gap_mm':2.0 if c['context'].startswith('ACCESS')else None}
 A.closeDocument(d.Name);rd=A.openDocument(str(path));rs=[o.Shape for o in rd.Objects if hasattr(o,'Shape')and not o.Shape.isNull()];check(len(rs)==len(items),'roundtrip shape count');row['roundtrip_shape_count']=len(rs);A.closeDocument(rd.Name);check(sha(q)==c['sha256'],'source unchanged');result['contexts'].append(row)
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['operation_refs']},indent=2))
