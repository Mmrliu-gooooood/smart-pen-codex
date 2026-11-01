"""Actual archived V3 versus byte-frozen active probe; no source/image changes."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import ctypes as C,json,hashlib,subprocess,tempfile,collections,time,math
OUT=Path(__file__).resolve().parent;WORK=OUT.parents[1]
BASE=WORK/'publication_20261031/target_repo'
V3=BASE/'verification/continuous_v3_experiments_20261029/smart_pen_continuous_roi_v3_candidate_20261029'
PROBE=WORK/'optics_paper_screen_20261031_1752/decoder_probe'
sys.path.insert(0,str(V3/'tests'))
from test_roi_continuous import Config,FrameResult
sourcepaths=[V3/p for p in ['firmware/vision/roi_continuous.c','firmware/vision/roi_continuous.h','firmware/vision/roi_opt.c','firmware/vision/roi_opt.h','firmware/vision/roi.h','firmware/codec/anoto.c','firmware/codec/anoto.h','firmware/codec/sequences.h','tests/test_roi_continuous.py','tests/test_roi_opt.py','tests/test_roi_vision.py','tests/roi_opt_fixture.py','tests/roi_fixture.py']]
sourcehash={str(p.relative_to(WORK)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sourcepaths}
rows=json.loads((PROBE/'results.json').read_text())+json.loads((PROBE/'controls_results.json').read_text())
truth=json.loads((PROBE/'summary.json').read_text())['truth'];inputhash={str((PROBE/p).relative_to(WORK)):hashlib.sha256((PROBE/p).read_bytes()).hexdigest() for p in ['results.json','controls_results.json','summary.json','controls_summary.json','MANIFEST.json']+[r['pgm'] for r in rows]}
outrows=[];commands=[]
with tempfile.TemporaryDirectory(prefix='optics-v3-replay-') as tmp:
 libs=[]
 for trace in [False,True]:
  so=Path(tmp)/('trace.so' if trace else 'direct.so')
  cmd=['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-pedantic','-shared','-fPIC','-I'+str(V3/'firmware/vision'),str(OUT/'bridge.c')]
  if trace:cmd+=['-DTRACE','-Wl,--wrap=pen_roi_decode_refined_transform']
  cmd += [str(V3/p) for p in ['firmware/vision/roi_continuous.c','firmware/vision/roi_opt.c','firmware/codec/anoto.c']]+['-lm','-o',str(so)]
  commands.append(cmd);subprocess.run(cmd,check=True);lib=C.CDLL(str(so));lib.ws_size.restype=C.c_size_t;lib.result_size.restype=C.c_size_t
  if lib.result_size()!=C.sizeof(FrameResult):raise RuntimeError('V3 ABI mismatch')
  if lib.ws_size()!=32640 or lib.result_size()!=192:raise RuntimeError('Unexpected host ABI')
  fn=lib.pen_roi_decode_continuous;fn.argtypes=[C.POINTER(C.c_uint8),C.c_size_t,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Config),C.c_void_p,C.POINTER(FrameResult)];fn.restype=C.c_int
  libs.append((lib,fn,(C.c_double*((lib.ws_size()+7)//8))()))
 for i,row in enumerate(rows):
  pgm=(PROBE/row['pgm']).read_bytes();header,pixels=pgm.split(b'\n',3)[:3],pgm.split(b'\n',3)[3]
  if header!=[b'P5',b'200 200',b'255'] or len(pixels)!=40000 or hashlib.sha256(pixels).hexdigest()!=row['pixel_sha256'] or hashlib.sha256(pgm).hexdigest()!=row['pgm_sha256']:raise RuntimeError('changed input')
  calls=[]
  for j,(lib,fn,ws) in enumerate(libs):
   if j:lib.reset_trace()
   image=(C.c_uint8*len(pixels)).from_buffer_copy(pixels);config=Config(710,1000,*truth['section']);out=FrameResult();C.memset(C.byref(out),0xa5,C.sizeof(out));before=bytes(out)
   start=time.monotonic();rc=fn(image,len(pixels),200,200,200,C.byref(config),ws,C.byref(out));elapsed=time.monotonic()-start
   if bytes(image)!=pixels:raise RuntimeError('input modified')
   if rc and bytes(out)!=before:raise RuntimeError('rejected output mutated')
   calls.append((rc,bytes(out),out,elapsed))
  if calls[0][:2]!=calls[1][:2]:raise RuntimeError('trace changed result')
  stats=(C.c_uint*8)();libs[1][0].trace(stats)
  rc,raw,result,elapsed=calls[0]
  if rc:classification='reject';decoded=None;crop=None
  else:
   d=result.roi.decoded
   classification='correct_accept' if [d.x,d.y]==truth['xy'] and list(d.directions)==truth['directions'] else 'wrong_accept'
   decoded=dict(x=d.x,y=d.y,directions=list(d.directions),pitch_px=d.pitch_px,y_scale=result.roi.y_scale,angle_deg=d.angle_deg,residual_cells=d.residual_cells,windows=d.windows,dots=d.dots,refine_seeds=result.refine_seeds,refine_iterations=result.refine_iterations,refine_models=result.refine_models,paper_to_frame=list(result.paper_to_frame),frame_to_paper=list(result.frame_to_paper))
   crop=dict(left=result.left,top=result.top,width=result.width,height=result.height,attempts=result.crop_attempts,removed_edge_components=result.edge_components,removed_edge_pixels=result.edge_pixels)
  core=(dict(calls=stats[0],left=(200-stats[1])//2,top=(200-stats[2])//2,width=stats[1],height=stats[2],stride=stats[3],cold_candidates=stats[4],seeds=stats[5],iterations=stats[6],refined_models=stats[7]) if stats[0] else None)
  support=None
  if crop:
   # Post-return conservative full-dot support oracle only. No truth enters C.
   sp=row['spec'];co=math.cos(math.radians(sp['angle']));si=math.sin(math.radians(sp['angle']));margin=float('inf')
   for dot,direction in enumerate(truth['directions']):
    dx,dy=((0,-1),(-1,0),(1,0),(0,1))[direction]
    cx=dot%6-2.5+dx*sp['offset'];cy=dot//6-2.5+dy*sp['offset']
    for rx in [-sp['radius'],sp['radius']]:
     for ry in [-sp['radius'],sp['radius']]:
      x,y=cx+rx,cy+ry;z=1+sp['perspective_x']*x+sp['perspective_y']*y
      xx,yy=x+sp['shear']*y,y*sp['scale_y']
      px=sp['tx']+sp['pitch']*(co*xx-si*yy)/z;py=sp['ty']+sp['pitch']*(si*xx+co*yy)/z
      margin=min(margin,px-crop['left'],crop['left']+crop['width']-px,py-crop['top'],crop['top']+crop['height']-py)
   support=dict(projected_dot_bounding_squares_inside_crop=margin>=0,minimum_conservative_margin_px=margin,oracle='postdecode true dot squares; sufficient conservative full-circle support, not physical calibration')
  record=dict(index=i,pgm=row['pgm'],pixel_sha256=row['pixel_sha256'],pgm_sha256=row['pgm_sha256'],group=row['group'],spec=row['spec'],active_status=row['status'],active_classification=row['classification'],v3_status=rc,v3_classification=classification,returned_crop=crop,postdecode_support=support,core_trace=core,decode_output=decoded,rejection_crop_note=('result untouched; no returned ROI; core not reached, exact attempted count not exposed' if rc and not core else 'result untouched; selected crop observed only at wrapped core entry' if rc else None),trace_direct_byte_equal=True,host_decode_seconds=elapsed)
  outrows.append(record);print(i,row['pgm'],row['classification'],'->',classification,rc,'crop',crop or core,flush=True)
for paths in [sourcehash,inputhash]:
 for p,h in paths.items():
  if hashlib.sha256((WORK/p).read_bytes()).hexdigest()!=h:raise RuntimeError('changed dependency '+p)
summary=dict(total=len(outrows),active_counts=dict(collections.Counter(r['active_classification'] for r in outrows)),v3_counts=dict(collections.Counter(r['v3_classification'] for r in outrows)),transitions=dict(collections.Counter(r['active_classification']+' -> '+r['v3_classification'] for r in outrows)),status_counts=dict(collections.Counter(r['v3_status'] for r in outrows)),returned_crops=dict(collections.Counter(str(r['returned_crop']['width']) for r in outrows if r['returned_crop'])),core_not_reached=sum(r['core_trace'] is None for r in outrows),workspace_bytes=32640,result_bytes=192,truth=truth,compile_commands=commands,source_sha256=sourcehash,input_sha256=inputhash,scope='Existing archived V3 unchanged, actual96/80conditionalcrop; same70byte-frozen synthetic PGMs; no oracle passed to C; direct and trace byte-equal on every case; not physical qualification')
(OUT/'results.json').write_text(json.dumps(outrows,indent=2)+'\n');(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:summary[k] for k in ['total','active_counts','v3_counts','transitions','status_counts','returned_crops','core_not_reached']},indent=2),flush=True)
