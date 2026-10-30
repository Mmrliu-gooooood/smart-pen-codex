from pathlib import Path
import os,sys,json,hashlib,math,subprocess
os.environ['XDG_CONFIG_HOME']='/tmp/indeoutline1247';sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A,Part
O=Path(__file__).resolve().parent;W=O.parent;C=W/'assembly_outline_sync_20261030_1239';B=2.264793176328504;F=B+.93
M=json.load(open(W/'assembly_dvp_route_masks_20261030_1228/route_masks_y20_38.json'));L=json.load(open(W/'assembly_context_audit_0818_20261030/all103_sync.json'))['rows'];inv=json.load(open(W/'assembly_context_audit_0818_20261030/inventory.json'))
def req(x,msg):
 if not x:raise RuntimeError(msg)
# Independent ledger transform, rather than accepting precomputed route-mask dimensions.
expected=[];moves={'J202':(7,88.8,None),'R240':(11,70.5,180),'R241':(11.85,73.35,90),'C207':(10.85,65,-90)}
for r in L:
 if r['ref']=='J108':continue
 for e in r['contexts'][0]['entities']:
  bb=e['projected_current_bounds_not_final_assembly'];xy=[bb[0]+7,127-bb[5],bb[3]+7,127-bb[2]];h=bb[4]-bb[1]
  if r['ref']in moves:
   nx,ny,ang=moves[r['ref']];ox,oy,oa=r['current_pose'][:3];ang=oa if ang is None else ang;a=math.radians(ang-oa);ps=[]
   for x in [xy[0],xy[2]]:
    for y in [xy[1],xy[3]]:ps.append((nx+(x-ox)*math.cos(a)+(y-oy)*math.sin(a),ny-(x-ox)*math.sin(a)+(y-oy)*math.cos(a)))
   xy=[min(x for x,y in ps),min(y for x,y in ps),max(x for x,y in ps),max(y for x,y in ps)]
  expected.append((r['ref'],xy,h,r['current_pose'][3]))
for ref,dx,dy,h in [('U205',3.7,2.7,1.25),('C209',.62,1.52,.70)]:
 r=next(r for r in L if r['ref']==ref);x,y=r['current_pose'][:2];expected.append((ref,[x-dx/2,y-dy/2,x+dx/2,y+dy/2],h,'F.Cu'))
req(len(expected)==104,'expected104')
for r in M['all_static_rectangles']:
 matches=[v for v in expected if v[0]==r['ref']and v[3]==r['side']and abs(v[2]-r['height'])<1e-8 and all(abs(a-b)<1e-8 for a,b in zip(v[1],r['xy_bounds']))];req(len(matches)==1,'mask budget mismatch '+r['ref'])
req({r['ref']for r in M['all_static_rectangles']}|{r['ref']for r in M['unqualified_operations']}=={r['ref']for r in L},'103 refs')
# Reconstruct accepted outline independently from literal native edge data extracted by pcbnew.
q=W/'smart_pen_next_20261028/hardware/sccb_local_reference_1216/native/mainboard_revD.kicad_pcb'
code="import pcbnew as p,json,sys;b=p.LoadBoard(sys.argv[1]);print(json.dumps([[[e.GetStart().x/1e6,e.GetStart().y/1e6],[e.GetEnd().x/1e6,e.GetEnd().y/1e6]]for e in b.GetDrawings()if e.GetLayer()==p.Edge_Cuts]))"
es=json.loads(subprocess.check_output(['/usr/bin/python3','-c',code,str(q)],text=True));chain=[es[0][0]]
while es:
 i=next(i for i,e in enumerate(es)if chain[-1]in e);a,b=es.pop(i);chain.append(b if chain[-1]==a else a)
req(len(chain)==7 and chain[0]==chain[-1],'native closed6');area=abs(sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(chain,chain[1:]))/2);req(abs(area-1372.2)<1e-8,'area')
board=Part.Face(Part.makePolygon([A.Vector(x-7,B,127-y)for x,y in chain])).extrude(A.Vector(0,.93,0));rows=[]
for ctx in inv['contexts']:
 src=Path(ctx['path']);req(hashlib.sha256(src.read_bytes()).hexdigest()==ctx['sha256'],'source hash');d=A.openDocument(str(src));pre='CTX_'if ctx['context']=='RevC'else'REF_CTX_';old={o.Label:o.Shape.copy()for o in d.Objects if hasattr(o,'Shape')and o.TypeId!='App::DocumentObjectGroup'and not o.Shape.isNull()and not o.Label.startswith(pre)and o.Label not in ['Context_ONLY','REF_Context_ONLY']};A.closeDocument(d.Name)
 d=A.openDocument(str(C/(ctx['context']+'_exact_outline_NOFAB.FCStd')));S={o.Label:o.Shape.copy()for o in d.Objects if hasattr(o,'Shape')and not o.Shape.isNull()};saved=S['Native_outline_dcbd_99p8_t0p93_NOFAB'];req(saved.cut(board).Volume+board.cut(saved).Volume<1e-8,'board moved or changed')
 for label,s in old.items():
  t=S[label];req(s.isValid()and t.isValid(),'invalid mechanical');req(abs(s.Volume-t.Volume)<1e-7,'mechanical volume changed');req(s.exportBrepToString()==t.exportBrepToString()or s.cut(t).Volume+t.cut(s).Volume<1e-8,'mechanical changed '+label)
 installs=[(k,s)for k,s in S.items()if k.startswith('INSTALL_')];req(len(installs)==104,'104saved')
 for k,s in installs:
  ref=k.split('_')[1];bb=s.BoundBox;xy=[bb.XMin+7,127-bb.ZMax,bb.XMax+7,127-bb.ZMin];req(any(v[0]==ref and all(abs(a-b)<1e-8 for a,b in zip(v[1],xy))and abs(v[2]-bb.YLength)<1e-8 for v in expected),'saved envelope mismatch')
 gates=[o for o in d.Objects if o.Label.startswith('UNQUALIFIED_OPERATION_')];req(len(gates)==6,'6gates');ss=list(S.values());step=Part.Shape();step.read(str(C/(ctx['context']+'_exact_outline_NOFAB.step')));req(step.isValid()and len(step.Solids)==sum(len(s.Solids)for s in ss),'STEP validity/count');err=abs(step.Volume-sum(s.Volume for s in ss));req(err<max(.002,sum(s.Volume for s in ss)*1e-6),'STEP volume');shift=saved.copy();shift.translate(A.Vector(0,0,-1.7));v=shift.cut(saved).Volume;req(abs(v-22.134)<1e-7,'negative shift');rows.append({'context':ctx['context'],'saved_board_symmetric_difference':0,'mechanical_objects_unchanged':len(old),'static_solids':104,'operation_gates':6,'step_solid_count':len(step.Solids),'step_volume_error':err,'negative_shift_added_volume':v});A.closeDocument(d.Name)
(O/'independent_saved.json').write_text(json.dumps({'native_vertices':chain,'native_area':area,'ledger104_envelopes_preserved':True,'contexts':rows},indent=2)+'\n');print(rows)
