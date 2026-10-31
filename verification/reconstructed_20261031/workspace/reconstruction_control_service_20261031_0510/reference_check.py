from pathlib import Path
import os,sys,json,hashlib
os.environ.update(XDG_CONFIG_HOME='/tmp/newreconstruct/config',XDG_CACHE_HOME='/tmp/newreconstruct/cache',XDG_DATA_HOME='/tmp/newreconstruct/data')
import pcbnew as p
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D/'review_dependencies'));from native_polygon import native_fractured_once
f=D/(sys.argv[1]if len(sys.argv)>1 else'final_candidate/mainboard_revD.kicad_pcb');a=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(f));at={t.m_Uuid.AsString():t for t in a.GetTracks()};bt={t.m_Uuid.AsString():t for t in b.GetTracks()}
def planes(board):
 out={}
 for z in board.Zones():
  if not z.GetIsRuleArea():out.setdefault((z.GetLayer(),z.GetNetname()),p.SHAPE_POLY_SET()).BooleanAdd(native_fractured_once(z.GetFilledPolysList(z.GetLayer())))
 return out
pa,pb=planes(a),planes(b);refs={p.F_Cu:[(p.In1_Cu,'GND')],p.B_Cu:[(p.In4_Cu,'GND')],p.In3_Cu:[(p.In4_Cu,'GND'),(p.In2_Cu,'3V3_AON')],p.In2_Cu:[(p.In1_Cu,'GND')]}
def shape(t):
 q=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(q,t.GetLayer(),0,50,p.ERROR_OUTSIDE);return q
def bbox(q):
 bb=q.BBox();return[bb.GetX()/1e6,bb.GetY()/1e6,bb.GetRight()/1e6,bb.GetBottom()/1e6]
loss=[];count=0
for u,t in at.items():
 if u not in bt or t.GetClass()=='PCB_VIA':continue
 for ref in refs.get(t.GetLayer(),[]):
  count+=1;s=shape(t);x=p.SHAPE_POLY_SET();x.BooleanIntersection(s,pa[ref]);y=p.SHAPE_POLY_SET();y.BooleanIntersection(s,pb[ref]);x.BooleanSubtract(y)
  if x.Area()>0:loss.append({'uuid':u,'net':t.GetNetname(),'layer':b.GetLayerName(t.GetLayer()),'reference_layer':b.GetLayerName(ref[0]),'reference_net':ref[1],'lost_mm2':x.Area()/1e12,'bbox':bbox(x)})
unions={}
for u,t in bt.items():
 if u in at or t.GetClass()=='PCB_VIA':continue
 unions.setdefault((t.GetNetname(),t.GetLayer()),p.SHAPE_POLY_SET()).BooleanAdd(shape(t))
new=[]
for (net,l),q in unions.items():
 for ref in refs.get(l,[]):
  x=p.SHAPE_POLY_SET();x.BooleanSubtract(q,pb[ref]);new.append({'net':net,'layer':b.GetLayerName(l),'reference_layer':b.GetLayerName(ref[0]),'reference_net':ref[1],'projection_mm2':q.Area()/1e12,'uncovered_mm2':x.Area()/1e12,'uncovered_bbox':bbox(x)if x.Area()>0 else None})
r={'status':'REFERENCE_DIAGNOSTIC_NOT_SI_ACCEPTANCE','pcb_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'all_retained_projections':count,'retained_reference_losses':loss,'new_path_uncovered':new,'interpretation':'In2 new signals use adjacent GND In1(.13mm) as dominant reference. In3 dominantGND In4(.13mm); secondary AON In2(.2028mm) also disclosed, not mislabeled ground. Missing area includes own via antipads and foreign-hole interactions; causal localization still required. No blanket zero regression claim.'};(D/'reference_checkpoint.json').write_text(json.dumps(r,indent=2));print(json.dumps({'retained_projection_count':count,'retained_loss_count':len(loss),'loss_totals':{net:sum(x['lost_mm2']for x in loss if x['net']==net)for net in set(x['net']for x in loss)},'new_projection_count':len(new)},indent=2))
