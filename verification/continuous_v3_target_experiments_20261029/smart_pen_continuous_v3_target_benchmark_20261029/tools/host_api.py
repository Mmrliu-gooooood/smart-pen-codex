"""Compile the frozen comparison without substituting host latency for target."""
import ctypes as C,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Config(C.Structure): _fields_=[('w',C.c_uint16),('h',C.c_uint16),('u',C.c_uint8),('v',C.c_uint8)]
class Result(C.Structure): _fields_=[('x',C.c_uint16),('y',C.c_uint16),('dots',C.c_uint16),('windows',C.c_uint16),('pitch',C.c_float),('angle',C.c_float),('residual',C.c_float),('directions',C.c_uint8*36)]
class Opt(C.Structure): _fields_=[('decoded',Result),('yscale',C.c_float),('candidates',C.c_uint32),('used_warm',C.c_uint8)]
class Frame(C.Structure): _fields_=[('roi',Opt),('left',C.c_uint16),('top',C.c_uint16),('width',C.c_uint16),('height',C.c_uint16),('edge_components',C.c_uint16),('edge_pixels',C.c_uint16),('crop_attempts',C.c_uint8),('paper_to_frame',C.c_double*6),('frame_to_paper',C.c_double*6),('refine_seeds',C.c_uint16),('refine_iterations',C.c_uint16),('refine_models',C.c_uint16)]
class Diagnostics(C.Structure): _fields_=[('cold_candidates',C.c_uint32),('seeds',C.c_uint32),('iterations',C.c_uint32),('models',C.c_uint32)]
def build(tmp):
 t=Path(tmp);(t/'bridge.c').write_text('#include "roi_continuous.h"\nsize_t ws_size(void){return sizeof(pen_continuous_workspace);}\nsize_t frame_size(void){return sizeof(pen_continuous_result);}\n')
 flags=['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-pedantic','-fPIC']
 subprocess.run(flags+['-Dpen_roi_decode_opt=pen_roi_decode_opt_frozen','-c',str(ROOT/'legacy/vision/roi_opt.c'),'-o',str(t/'legacy.o')],check=True)
 subprocess.run(flags+['-shared','-I'+str(ROOT/'vision'),str(t/'bridge.c'),str(ROOT/'main/trace.c'),'-Wl,--wrap=pen_roi_decode_refined_transform',str(ROOT/'vision/roi_opt.c'),str(ROOT/'vision/roi_continuous.c'),str(ROOT/'codec/anoto.c'),str(t/'legacy.o'),'-lm','-o',str(t/'api.so')],check=True)
 lib=C.CDLL(str(t/'api.so'));lib.ws_size.restype=C.c_size_t;lib.frame_size.restype=C.c_size_t
 lib.pen_roi_decode_continuous.argtypes=[C.POINTER(C.c_uint8),C.c_size_t,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Config),C.c_void_p,C.POINTER(Frame)]
 lib.pen_roi_decode_opt_frozen.argtypes=[C.POINTER(C.c_uint8),C.c_size_t,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Config),C.c_void_p,C.c_void_p,C.POINTER(Opt)]
 lib.bench_trace_get.restype=Diagnostics
 assert lib.frame_size()==C.sizeof(Frame)
 return lib
