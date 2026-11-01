"""Bounded actual active-C decoder sweep. Synthetic fixed code, no camera claims."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import ctypes as C, math, subprocess, tempfile, json, hashlib, collections, time
from dataclasses import asdict
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]/'publication_20261031/target_repo'
sys.path.insert(0,str(ROOT/'tests'))
from roi_opt_fixture import Render,render,vectors
from test_roi_vision import Config,Result
from test_roi_opt import Prior,OptResult
sources=['firmware/vision/roi_opt.c','firmware/vision/roi_opt.h','firmware/vision/roi.h','firmware/codec/anoto.c','firmware/codec/anoto.h','firmware/codec/sequences.h','tests/roi_opt_fixture.py','tests/roi_fixture.py','tests/test_roi_opt.py','tests/test_roi_vision.py','tests/fixtures/microdots_vectors.json']
hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources}
vector=vectors()[2]
cases=[]
for pitch in [60/7,10.,12.]:
 for ratio in [math.cos(math.radians(15)),math.cos(math.radians(30)),math.cos(math.radians(45)),.9,.8,.7]:
  cases.append(dict(group='affine_no_perspective_control',pitch=pitch,tilt=0,offset=1/6,ratio=ratio))
rows=[]
with tempfile.TemporaryDirectory(prefix='optics-active-c-') as tmp:
 tmp=Path(tmp);bridge=tmp/'bridge.c';bridge.write_text('#include "roi_opt.h"\nsize_t opt_workspace_size(void){return sizeof(pen_roi_workspace);}\n')
 so=tmp/'roi_opt.so';command=['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-pedantic','-shared','-fPIC','-I'+str(ROOT/'firmware/vision'),str(bridge),str(ROOT/'firmware/vision/roi_opt.c'),str(ROOT/'firmware/codec/anoto.c'),'-lm','-o',str(so)]
 subprocess.run(command,check=True)
 lib=C.CDLL(str(so));lib.opt_workspace_size.restype=C.c_size_t
 ws_size=lib.opt_workspace_size();ws=(C.c_double*((ws_size+7)//8))()
 decode=lib.pen_roi_decode_opt;decode.argtypes=[C.POINTER(C.c_uint8),C.c_size_t,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Config),C.c_void_p,C.POINTER(Prior),C.POINTER(OptResult)];decode.restype=C.c_int
 for k,case in enumerate(cases):
  angle=math.radians(case['tilt'])
  # Affine control has anisotropic scale only; renderer coordinates are cells.
  # No physical tilt or perspective is asserted for these controls.
  spec=Render(pitch=case['pitch'],scale_y=case['ratio'],perspective_y=0,offset=case['offset'],radius=1/6,width=200,height=200,tx=100.35,ty=99.65)
  pixels=render(vector['directions'],spec)
  pgm=b'P5\n200 200\n255\n'+pixels;name=f'control_{k:03d}.pgm';(OUT/name).write_bytes(pgm)
  image=(C.c_uint8*len(pixels)).from_buffer_copy(pixels);cfg=Config(710,1000,*vector['section']);result=OptResult();C.memset(C.byref(result),0xa5,C.sizeof(result));before=bytes(result)
  start=time.monotonic();status=decode(image,len(pixels),200,200,200,C.byref(cfg),ws,None,C.byref(result));elapsed=time.monotonic()-start
  if status: 
   if bytes(result)!=before:raise RuntimeError('rejected output mutated')
   classification='reject';decoded=None
  else:
   decoded=dict(x=result.decoded.x,y=result.decoded.y,directions=list(result.decoded.directions),pitch_px=result.decoded.pitch_px,y_scale=result.y_scale,angle_deg=result.decoded.angle_deg,residual_cells=result.decoded.residual_cells)
   classification='correct_accept' if [result.decoded.x,result.decoded.y]==vector['xy'] and list(result.decoded.directions)==vector['directions'] else 'wrong_accept'
  row=dict(id=k,**case,status=status,classification=classification,decoded=decoded,spec=asdict(spec),pgm=name,pixel_sha256=hashlib.sha256(pixels).hexdigest(),pgm_sha256=hashlib.sha256(pgm).hexdigest(),host_decode_seconds=elapsed)
  rows.append(row);print(k,case,classification,status,flush=True)
for p,h in hashes.items():
 if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise RuntimeError('source changed '+p)
summary=dict(total=len(rows),counts=dict(collections.Counter(r['classification'] for r in rows)),by_tilt={str(t):dict(collections.Counter(r['classification'] for r in rows if r['group']=='tilt_offset' and r['tilt']==t)) for t in [0,15,30,45,60]},by_offset={str(o):dict(collections.Counter(r['classification'] for r in rows if r['group']=='tilt_offset' and r['offset']==o)) for o in [.10,1/6,.25]},workspace_bytes=ws_size,vector_index=2,truth=vector,compile_command=command,source_sha256=hashes,limits=['Affine anisotropy control only, no physical perspective/tilt interpretation; one fixed observed6x6 code.','Axis ratios cos15/cos30/cos45 and exact searched .9/.8/.7; perspective=0.','Physical radius0.05mm; offset varied .03/.05/.075mm; no blur/noise/lens distortion/ink.','Active cold orthogonal C only; no V3/V4/warm prior; native host O2, not sanitizer or MCU timing.','No image geometry or coordinates passed to C; config supplies paper dimensions and encoded section only.','Finite18 controls do not bound wrong-accept probability or physical tilt acceptance.'])
(OUT/'controls_results.json').write_text(json.dumps(rows,indent=2)+'\n');(OUT/'controls_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary['counts']),flush=True)
