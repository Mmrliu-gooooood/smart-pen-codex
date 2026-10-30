from pathlib import Path
import sys,json,hashlib,collections,math
D=Path(__file__).resolve().parent;R=D.parents[2];S=R/'docs/electronics/imu_full_joint_plan_0505';sys.path.insert(0,str(R/'docs/electronics/imu_control_joint_plan_0444'));import geometry as g
p=g.p;sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));from finite_copper import shape
old=json.loads((S/'strategy1.json').read_text());new=json.loads((D/'strategy1.json').read_text());rep=json.loads((D/'simplification.json').read_text());sig=lambda t:json.dumps(t,sort_keys=True)
def req(c,m):
 if not c:raise RuntimeError(m)
req(hashlib.sha256((S/'strategy1.json').read_bytes()).hexdigest()==new['original_model_sha256'],'originalsource');req(new['parent_sha']==old['parent_sha']and new['removed']==old['removed'],'sameparent/delta')
changed={r['tag']for r in rep['reports']};protected={}
for tag,ts in old['parts'].items():
 if tag not in changed:req(ts==new['parts'][tag],'analytical local unchanged '+tag)
 ov=collections.Counter(sig(t)for t in ts if t['type']=='via');nv=collections.Counter(sig(t)for t in new['parts'][tag]if t['type']=='via');req(ov==nv,'vias exact '+tag)
 widths={t['width']for t in ts if t['type']=='track'};req(all(t['width']in widths for t in new['parts'][tag]if t['type']=='track'),'widths')
for r in rep['reports']:
 tag=r['tag'];count=collections.Counter(sig(t)for t in new['parts'][tag]);fixed=[old['parts'][tag][i]for i in r['fixed_segment_indices']];fc=collections.Counter(sig(t)for t in fixed);req(all(count[k]>=v for k,v in fc.items()),'protectedbranch/via segment '+tag);protected[tag]=len(fixed)
keep=[]
def poly(model):
 result={}
 for ts in model['parts'].values():
  for t in ts:
   if t['type']=='via':q=g.via(t['net'],t['a']);q.SetWidth(p.F_Cu,round(t['width']*1e6));q.SetDrill(round(t['drill']*1e6))
   else:q=g.track(t['net'],g.b.GetLayerID(t['layer']),t['a'],t['b'],t['width'])
   keep.append(q)
   for l in g.L:
    if q.IsOnLayer(l):result.setdefault((t['net'],l),p.SHAPE_POLY_SET()).BooleanAdd(shape(q,l))
 return result
op=poly(old);np=poly(new);diff=[]
for k,a in op.items():
 b=np[k];rm=p.SHAPE_POLY_SET();rm.BooleanSubtract(a,b);ad=p.SHAPE_POLY_SET();ad.BooleanSubtract(b,a)
 if rm.Area()>1 or ad.Area()>1:diff.append({'net':k[0],'layer':g.b.GetLayerName(k[1]),'removed_mm2':rm.Area()/1e12,'added_mm2':ad.Area()/1e12,'symmetric_difference_mm2':(rm.Area()+ad.Area())/1e12})
# Existing planes' via antipad changes are identical because every via remains exactly unchanged.
print(json.dumps({'status':'EXACT_VISIBILITY_DIFFERENTIAL_AUDIT','original_model_sha':new['original_model_sha256'],'protected_original_contact_segments_by_part':protected,'unchanged_analytical_parts':sorted(set(old['parts'])-changed),'all_vias_exact_per_part':True,'all_widths_preserved':True,'all_parent_removals_identical':True,'new_plane_antipad_geometry_identical_to_original_model':True,'changed_copper_by_net_layer':diff,'limits':['Changed copper is explicitly NOT geometrically identical; only constrained shortcut replacements','Finite predicates, full pad graphs and reference projection screen independently rerun in verify.py','No timing/signal-integrity or manufacturing approval']},indent=2))
