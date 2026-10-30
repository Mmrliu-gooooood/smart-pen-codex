"""Strict ctypes bridge for the explicitly versioned experimental V4 ABI only."""
import ctypes as C
import tempfile,subprocess
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent
class Config(C.Structure):
    _fields_=[('paper_width',C.c_uint16),('paper_height',C.c_uint16),('section_u',C.c_uint8),('section_v',C.c_uint8)]
class Decoded(C.Structure):
    _fields_=[('x',C.c_uint16),('y',C.c_uint16),('dots',C.c_uint16),('windows',C.c_uint16),('pitch_px',C.c_float),('angle_deg',C.c_float),('residual_cells',C.c_float),('directions',C.c_uint8*36)]
class OptResult(C.Structure):
    _fields_=[('decoded',Decoded),('y_scale',C.c_float),('candidates',C.c_uint32),('used_warm_start',C.c_uint8)]
class Result(C.Structure):
    _fields_=[('abi_version',C.c_uint32),('roi',OptResult),('left',C.c_uint16),('top',C.c_uint16),('width',C.c_uint16),('height',C.c_uint16),('paper_to_frame',C.c_double*9),('frame_to_paper',C.c_double*9)]
class Diagnostics(C.Structure):
    _fields_=[(k,C.c_uint32) for k in ('components','retained','coarse','seeds','iterations','models','overflow')]
class Decoder:
    def __init__(self):
        self.tmp=tempfile.TemporaryDirectory();t=Path(self.tmp.name);src=P/'source/firmware'
        (t/'bridge.c').write_text('#include "roi_projective.h"\nsize_t ws_size(void){return sizeof(pen_projective_workspace);}\nsize_t result_size(void){return sizeof(pen_projective_result);}\nsize_t diagnostics_size(void){return sizeof(pen_projective_diagnostics);}\n')
        cmd=['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-pedantic','-shared','-fPIC','-I'+str(src/'vision'),str(t/'bridge.c'),str(src/'vision/roi_projective.c'),str(src/'codec/anoto.c'),'-lm','-o',str(t/'v4.so')]
        subprocess.run(cmd,check=True);self.lib=C.CDLL(str(t/'v4.so'))
        for k in ('ws_size','result_size','diagnostics_size'):getattr(self.lib,k).restype=C.c_size_t
        self.workspace_bytes=self.lib.ws_size();self.ws=(C.c_double*((self.workspace_bytes+7)//8))()
        assert self.lib.result_size()==C.sizeof(Result) and self.lib.diagnostics_size()==C.sizeof(Diagnostics)
        self.fn=self.lib.pen_roi_decode_projective_v4
        self.fn.argtypes=[C.POINTER(C.c_uint8),C.c_size_t,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Config),C.c_void_p,C.POINTER(Result),C.POINTER(Diagnostics)];self.fn.restype=C.c_int
        self.lib.pen_projective_map_v4.argtypes=[C.POINTER(C.c_double),C.c_double,C.c_double,C.POINTER(C.c_double),C.POINTER(C.c_double)];self.lib.pen_projective_map_v4.restype=C.c_int
    def close(self):self.tmp.cleanup()
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def decode(self,image,config=(710,1000,10,2)):
        image=np.ascontiguousarray(image,dtype=np.uint8);before=image.tobytes();h,w=image.shape
        out=Result();C.memset(C.byref(out),165,C.sizeof(out));old=bytes(out);diag=Diagnostics();cfg=Config(*config)
        status=self.fn(image.ctypes.data_as(C.POINTER(C.c_uint8)),image.size,w,h,w,C.byref(cfg),self.ws,C.byref(out),C.byref(diag))
        assert image.tobytes()==before,'decoder modified input'
        assert status==0 or bytes(out)==old,'decoder modified result on failure'
        r=dict(status=status,diagnostics={k:getattr(diag,k) for k,_ in Diagnostics._fields_})
        if status==0:
            assert out.abi_version==4,'not V4 result'
            assert 0<=out.left<out.left+out.width<=w and 0<=out.top<out.top+out.height<=h
            z=out.roi.decoded
            assert 36<=z.dots<=128 and z.windows>=1 and not out.roi.used_warm_start
            r.update(x=z.x,y=z.y,dots=z.dots,windows=z.windows,directions=list(z.directions),H=list(out.paper_to_frame),Hinv=list(out.frame_to_paper),roi=[out.left,out.top,out.width,out.height],abi_version=out.abi_version)
            # The returned inverse must invert the returned map, independent of truth.
            a=np.array(r['H']).reshape(3,3);b=np.array(r['Hinv']).reshape(3,3);ab=a@b
            assert np.all(np.isfinite(ab)) and np.max(np.abs(ab/ab[2,2]-np.eye(3)))<1e-8
        return r
