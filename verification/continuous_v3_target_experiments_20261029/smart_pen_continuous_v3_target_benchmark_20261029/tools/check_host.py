from host_api import *
from oracle import validate
import json,tempfile,hashlib
p=ROOT;rows=[]
with tempfile.TemporaryDirectory() as tmp:
 lib=build(tmp);assert lib.ws_size()==32640;ws=(C.c_double*((lib.ws_size()+7)//8))();cfg=Config(710,1000,10,2)
 for f in json.loads((p/'fixtures/manifest.json').read_text())['fixtures']:
  raw=(p/'fixtures'/f['file']).read_bytes().split(b'\n255\n',1)[1];assert hashlib.sha256(raw).hexdigest()==f['pixel_sha256'];im=(C.c_uint8*len(raw)).from_buffer_copy(raw)
  for decoder in ['frozen_opt','continuous_v3']:
   out=Frame();C.memset(C.byref(out),165,C.sizeof(out));before=bytes(out)
   lib.bench_trace_reset()
   if decoder=='continuous_v3': status=lib.pen_roi_decode_continuous(im,len(raw),200,200,200,C.byref(cfg),ws,C.byref(out))
   else: status=lib.pen_roi_decode_opt_frozen(im,len(raw),200,200,200,C.byref(cfg),ws,None,C.byref(out.roi))
   assert bytes(im)==raw
   r=dict(instrumented=decoder=='continuous_v3',fixture=f['file'],decoder=decoder,status=status,failure_output_preserved=not status or bytes(out)==before)
   if decoder=='continuous_v3':
    d=lib.bench_trace_get();r.update(refine_stats=[d.cold_candidates,d.seeds,d.iterations,d.models],trace_calls=lib.bench_trace_calls())
   if not status:
    r.update(result_refine_stats=[out.refine_seeds,out.refine_iterations,out.refine_models],x=out.roi.decoded.x,y=out.roi.decoded.y,dots=out.roi.decoded.dots,windows=out.roi.decoded.windows,candidates=out.roi.candidates,used_warm=out.roi.used_warm,directions=list(out.roi.decoded.directions),crop=[out.left,out.top,out.width,out.height],crop_attempts=out.crop_attempts,edge_components=out.edge_components,edge_pixels=out.edge_pixels,paper_to_frame=list(out.paper_to_frame),frame_to_paper=list(out.frame_to_paper))
   verdict,errors=validate(r,f);assert not errors,(r,errors);r['oracle_verdict']=verdict;rows.append(r)
 print(json.dumps(dict(scope='host functional only; no timing and no actual target log',workspace_bytes=lib.ws_size(),records=rows),indent=2))
