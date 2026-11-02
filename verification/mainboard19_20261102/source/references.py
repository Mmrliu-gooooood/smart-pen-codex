from pathlib import Path
import pcbnew as p,json,sys
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D/'review_dependencies'))
from native_polygon import native_fractured_once
c=json.loads((D/'native_contract.json').read_text());a=p.LoadBoard(str(D/'parent/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(D/'candidate/mainboard_revD.kicad_pcb'));added={r['uuid']for r in c['objects']};removed=set(c['removed'])
def planes(board):
 out={}
 for z in board.Zones():
  if not z.GetIsRuleArea():out.setdefault((z.GetLayer(),z.GetNetname()),p.SHAPE_POLY_SET()).BooleanAdd(native_fractured_once(z.GetFilledPolysList(z.GetLayer())))
 return out
def sub(x,y):q=p.SHAPE_POLY_SET(x);q.BooleanSubtract(y);return q
def inter(x,y):q=p.SHAPE_POLY_SET(x);q.BooleanIntersection(y);return q
pa,pb=planes(a),planes(b);refs={p.F_Cu:[(p.In1_Cu,'GND')],p.In2_Cu:[(p.In1_Cu,'GND')],p.In3_Cu:[(p.In2_Cu,'3V3_AON'),(p.In4_Cu,'GND')],p.B_Cu:[(p.In4_Cu,'GND')]};newrows=[];changed=[];retained_count=0
for t in b.GetTracks():
 if t.GetClass()=='PCB_VIA':continue
 u=t.m_Uuid.AsString();shape=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(shape,t.GetLayer(),0,50,p.ERROR_OUTSIDE)
 for k in refs.get(t.GetLayer(),[]):
  row={'uuid':u,'net':t.GetNetname(),'layer':b.GetLayerName(t.GetLayer()),'reference_layer':b.GetLayerName(k[0]),'reference_net':k[1]}
  if u in added:
   row.update(length_mm=t.GetLength()/1e6,uncovered_mm2=sub(shape,pb[k]).Area()/1e12);newrows.append(row)
  else:
   retained_count+=1;lost=inter(shape,sub(pa[k],pb[k])).Area()/1e12;gained=inter(shape,sub(pb[k],pa[k])).Area()/1e12
   if lost or gained:row.update(lost_mm2=lost,gained_mm2=gained);changed.append(row)
print('reference measures done',len(newrows),len(changed),flush=True)
# Native morphological erosion is a bottleneck proxy, not an electrical-current or absolute minimum-width qualification.
def morph(poly,width):
 q=p.SHAPE_POLY_SET(poly);q.Inflate(-round(width*1e6/2),p.CORNER_STRATEGY_ROUND_ALL_CORNERS,250);q.Simplify();parts=[]
 for i in range(q.OutlineCount()):
  z=q.Subset(i,i+1);area=z.Area()/1e12
  if area>.01:
   bb=z.BBox();parts.append({'area_mm2':area,'bbox_mm':[bb.GetX()/1e6,bb.GetY()/1e6,bb.GetRight()/1e6,bb.GetBottom()/1e6]})
 return {'total_area_mm2':q.Area()/1e12,'total_components':q.OutlineCount(),'components_gt_0_01_mm2':sorted(parts,key=lambda x:-x['area_mm2'])}
morphs=[]
for w in [.1,.15,.2,.25,.3,.4,.5,.75,1.0,1.5,2.0]:
 morphs.append({'erosion_width_mm':w,'parent':morph(pa[p.In2_Cu,'3V3_AON'],w),'candidate':morph(pb[p.In2_Cu,'3V3_AON'],w)});print('neck proxy',w,flush=True)
caps=[]
for f in b.GetFootprints():
 if f.GetReference().startswith('C'):
  for q in f.Pads():
   if q.GetNetname()=='3V3_AON':caps.append({'terminal':f.GetReference()+'.'+q.GetNumber(),'value':f.GetValue(),'position_mm':[q.GetPosition().x/1e6,q.GetPosition().y/1e6]})
out={'native_sha256':c['candidate_sha256'],'retained_reference_projections':retained_count,'retained_changed_reference_projections':changed,'new_reference_projections':newrows,'AON_morphological_bottleneck_proxy':morphs,'AON_capacitor_terminals_topological_core_checked_separately':caps,'limits':'Morphological widths are explicit geometric erosion probes, not an absolute minimum PDN neck, impedance/current density or power qualification. All capacitor terminals require finite partition verification; continuity alone does not establish equivalent PDN.'}
(D/('references_O.json'if not __debug__ else'references.json')).write_text(json.dumps(out,indent=2));print('done',flush=True)
