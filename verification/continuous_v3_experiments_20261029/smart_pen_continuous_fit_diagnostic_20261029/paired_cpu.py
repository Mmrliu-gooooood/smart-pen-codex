"""Paired host process-CPU comparison, not MCU latency/FPS or hardware evidence."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import ctypes as C
import json,hashlib,time,subprocess,tempfile,statistics
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
V2=BASE/'smart_pen_continuous_roi_candidate_20261028';V3=BASE/'smart_pen_continuous_roi_v3_candidate_20261029'
sys.path.insert(0,str(V3/'tests'));from test_roi_vision import Config
cfg=Config(710,1000,10,2)
cases=[('fov5',V2/'tests/fixtures/continuous/fov5_roi200_phase0.pgm',0,0),('fov6',V2/'tests/fixtures/continuous/fov6_roi200_phase0.pgm',0,0),('fov7',V2/'tests/fixtures/continuous/fov7_roi200_phase0.pgm',0,0),('fractional51',V2/'tests/fixtures/continuous/extended_fov51.pgm',-3,0),('rotation45',V2/'tests/fixtures/continuous/extended_rot45.pgm',-3,0),('fake',V2/'tests/fixtures/continuous/extended_fake_dots.pgm',-3,-3),('no_complete_window',HERE/'pixels/case_109.pgm',-3,-3)]
with tempfile.TemporaryDirectory() as tmp:
 tmp=Path(tmp);runners={}
 for label,root in [('v2',V2),('v3',V3)]:
  (tmp/(label+'.c')).write_text('#include "roi_continuous.h"\nsize_t ws_size(void){return sizeof(pen_continuous_workspace);}\nsize_t result_size(void){return sizeof(pen_continuous_result);}\n')
  so=tmp/(label+'.so');subprocess.run(['cc','-std=c11','-O2','-shared','-fPIC','-I'+str(root/'firmware/vision'),str(tmp/(label+'.c')),str(root/'firmware/vision/roi_continuous.c'),str(root/'firmware/vision/roi_opt.c'),str(root/'firmware/codec/anoto.c'),'-lm','-o',str(so)],check=True)
  lib=C.CDLL(str(so));lib.ws_size.restype=C.c_size_t;lib.result_size.restype=C.c_size_t
  lib.pen_roi_decode_continuous.argtypes=[C.POINTER(C.c_uint8),C.c_size_t,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Config),C.c_void_p,C.c_void_p]
  runners[label]=(lib,(C.c_double*((lib.ws_size()+7)//8))(),(C.c_double*((lib.result_size()+7)//8))())
 rows=[]
 for name,path,v2rc,v3rc in cases:
  pixels=path.read_bytes().split(b'\n',3)[3];image=(C.c_uint8*len(pixels)).from_buffer_copy(pixels)
  for iteration in range(8):
   for label in (('v2','v3') if iteration%2==0 else ('v3','v2')):
    lib,ws,result=runners[label];C.memset(result,165,C.sizeof(result));before=bytes(result)
    wall=time.perf_counter_ns();cpu=time.process_time_ns();status=lib.pen_roi_decode_continuous(image,len(pixels),200,200,200,C.byref(cfg),ws,result);cpu=time.process_time_ns()-cpu;wall=time.perf_counter_ns()-wall
    assert status==(v2rc if label=='v2' else v3rc),(name,label,status)
    assert status==0 or bytes(result)==before
    rows.append(dict(name=name,version=label,iteration=iteration,status=status,cpu_ms=cpu/1e6,wall_ms=wall/1e6,pixel_sha256=hashlib.sha256(pixels).hexdigest()))
  print(name,flush=True)
 summary=[]
 for name,*_ in cases:
  group={v:[r for r in rows if r['name']==name and r['version']==v] for v in ('v2','v3')}
  cpu={v:statistics.median(x['cpu_ms'] for x in rs) for v,rs in group.items()}
  summary.append(dict(name=name,cpu_median_ms=cpu,cpu_ratio_v3_over_v2=cpu['v3']/cpu['v2'],wall_median_ms={v:statistics.median(x['wall_ms'] for x in rs) for v,rs in group.items()}))
 (HERE/'paired_cpu.json').write_text(json.dumps(dict(host_only=True,compiler=subprocess.check_output(['cc','--version'],text=True).splitlines()[0],method='8 paired alternating calls/fixture, process CPU and wall time; competing agents may affect wall. Not target timing.',rows=rows,summary=summary),indent=2));print(json.dumps(summary,indent=2))
