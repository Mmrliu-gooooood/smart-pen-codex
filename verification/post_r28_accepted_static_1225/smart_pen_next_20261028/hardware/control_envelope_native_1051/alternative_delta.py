from pathlib import Path
import os,json,hashlib,sys
os.environ['XDG_CONFIG_HOME']='/tmp/control1051alt'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];A=D.parent/'control_bias_native_1041/native/mainboard_revD.kicad_pcb';B=D/'native/mainboard_revD.kicad_pcb';a=p.LoadBoard(str(A));b=p.LoadBoard(str(B));at={t.m_Uuid.AsString():t for t in a.GetTracks()};bt={t.m_Uuid.AsString():t for t in b.GetTracks()};removed=sorted(set(at)-set(bt));added=sorted(set(bt)-set(at));oldm=json.loads((D.parent/'control_bias_native_1041/materialization.json').read_text());newm=json.loads((D/'materialization.json').read_text())
if removed!=oldm['added']or added!=newm['added']:raise RuntimeError('replacement limited to exact control additions')
sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));from finite_copper import build,components,shape
from native_polygon import native_fractured_once
ag={n:components(v)for n,v in build(a).items()};bg={n:components(v)for n,v in build(b).items()}
if ag!=bg:raise RuntimeError('alternative retains all physical partitions')
def planes(b):
 out={}
 for z in b.Zones():
  if not z.GetIsRuleArea():out.setdefault(z.GetLayer(),p.SHAPE_POLY_SET()).BooleanAdd(native_fractured_once(z.GetFilledPolysList(z.GetLayer())))
 return out
pa,pb=planes(a),planes(b);loss=[];count=0
for u in set(at)&set(bt):
 t=at[u]
 if isinstance(t,p.PCB_VIA):continue
 for l in {p.F_Cu:[p.In1_Cu],p.B_Cu:[p.In4_Cu],p.In3_Cu:[p.In2_Cu,p.In4_Cu]}.get(t.GetLayer(),[]):
  count+=1;s=shape(t,t.GetLayer());x=p.SHAPE_POLY_SET();x.BooleanIntersection(s,pa[l]);y=p.SHAPE_POLY_SET();y.BooleanIntersection(s,pb[l]);x.BooleanSubtract(y)
  if x.Area()/1e12>1e-8:loss.append({'uuid':u,'area_mm2':x.Area()/1e12})
if loss:raise RuntimeError(loss)
print(json.dumps({'status':'REPLACEMENT_OF_MECHANICALLY_GATED_CONTROL_ROUTING_NOT_BASELINE_ADOPTION','gated_control_sha256':hashlib.sha256(A.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(B.read_bytes()).hexdigest(),'removed_gated_control_uuids':removed,'added_replacement_uuids':added,'same_all_net_physical_partitions':True,'common_old_projection_count':count,'common_old_reference_loss':loss},indent=2))
