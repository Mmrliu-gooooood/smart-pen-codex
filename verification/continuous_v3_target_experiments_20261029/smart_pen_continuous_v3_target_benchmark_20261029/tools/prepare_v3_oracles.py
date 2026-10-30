"""Post-return replay oracles only; sources/images verified against independently frozen V3."""
from host_api import *
import json,hashlib,tempfile
p=ROOT;src=p.parent/'smart_pen_continuous_roi_v3_candidate_20261029';m=json.loads((p/'fixtures/manifest.json').read_text());known={r['file'] for r in m['fixtures']}
for name,status in [('extended_fov51.pgm',0),('v3_seed_overflow.pgm',-4)]:
 if name not in known:
  data=(p/'fixtures'/name).read_bytes();raw=data.split(b'\n255\n',1)[1]
  m['fixtures'].append(dict(file=name,source_path='tests/fixtures/continuous/'+name,pgm_sha256=hashlib.sha256(data).hexdigest(),pixel_sha256=hashlib.sha256(raw).hexdigest(),width=200,height=200,stride=200,paper_width=710,paper_height=1000,section=[10,2],expected_status=status,transform_numeric_tolerance=1e-5))
# Only new fixed scale/overflow rows are populated from replay. Existing frozen V3 rows must match.
with tempfile.TemporaryDirectory() as tmp:
 lib=build(tmp);assert lib.ws_size()==32640;ws=(C.c_double*((lib.ws_size()+7)//8))();cfg=Config(710,1000,10,2)
 for f in m['fixtures']:
  raw=(p/'fixtures'/f['file']).read_bytes().split(b'\n255\n',1)[1];im=(C.c_uint8*len(raw)).from_buffer_copy(raw);out=Frame();C.memset(C.byref(out),165,C.sizeof(out));before=bytes(out);lib.bench_trace_reset()
  status=lib.pen_roi_decode_continuous(im,len(raw),200,200,200,C.byref(cfg),ws,C.byref(out));stats=lib.bench_trace_get();assert status==f['expected_status'];assert not status or bytes(out)==before;assert bytes(im)==raw
  f['refine_stats']=[stats.cold_candidates,stats.seeds,stats.iterations,stats.models];f['expected_trace_calls']=lib.bench_trace_calls()
  if not status:
   actual=dict(x=out.roi.decoded.x,y=out.roi.decoded.y,directions=list(out.roi.decoded.directions),crop=[out.left,out.top,out.width,out.height],dots=out.roi.decoded.dots,windows=out.roi.decoded.windows,edge_components=out.edge_components,edge_pixels=out.edge_pixels,attempts=out.crop_attempts,paper_to_frame=list(out.paper_to_frame),frame_to_paper=list(out.frame_to_paper),refine_seeds=out.refine_seeds,refine_iterations=out.refine_iterations,refine_models=out.refine_models)
   for k,v in actual.items():
    if k in f:assert f[k]==v,(f['file'],k)
    else:f[k]=v
  legacy=Opt();C.memset(C.byref(legacy),165,C.sizeof(legacy));old=bytes(legacy);rc=lib.pen_roi_decode_opt_frozen(im,len(raw),200,200,200,C.byref(cfg),ws,None,C.byref(legacy));assert rc!=0 and bytes(legacy)==old;f['legacy_expected_status']=rc
  if f['file']=='v3_seed_overflow.pgm':assert f['refine_stats'][1:]==[65,0,0] and f['expected_trace_calls']==1
(p/'fixtures/manifest.json').write_text(json.dumps(m,indent=2)+'\n')
print([(f['file'],f['expected_status'],f['refine_stats']) for f in m['fixtures']])
