"""Optimized candidate raw grayscale tests; no ground-truth geometry enters C."""
import ctypes as C
from dataclasses import replace
import math
from pathlib import Path
import random
import subprocess
import tempfile
import unittest
from roi_opt_fixture import Render, render, vectors
from test_roi_vision import Config, Result
ROOT=Path(__file__).resolve().parents[1]

class Prior(C.Structure):
    _fields_=[('valid',C.c_uint32),('pitch_px',C.c_float),('angle_deg',C.c_float),('y_scale',C.c_float)]
class OptResult(C.Structure):
    _fields_=[('decoded',Result),('y_scale',C.c_float),('candidates',C.c_uint32),('used_warm_start',C.c_uint8)]

class RoiOptimized(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        root=Path(cls.tmp.name)
        bridge=root/'bridge.c'
        bridge.write_text('#include "roi_opt.h"\nsize_t opt_workspace_size(void){return sizeof(pen_roi_workspace);}\n')
        so=root/'roi_opt.so'
        subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-pedantic',
                        '-shared','-fPIC','-I'+str(ROOT/'firmware/vision'),str(bridge),
                        str(ROOT/'firmware/vision/roi_opt.c'),str(ROOT/'firmware/codec/anoto.c'),'-lm','-o',str(so)],check=True)
        cls.lib=C.CDLL(str(so));cls.lib.opt_workspace_size.restype=C.c_size_t
        cls.ws_size=cls.lib.opt_workspace_size()
        cls.decode=cls.lib.pen_roi_decode_opt
        cls.decode.argtypes=[C.POINTER(C.c_uint8),C.c_size_t,C.c_uint,C.c_uint,C.c_uint,
                             C.POINTER(Config),C.c_void_p,C.POINTER(Prior),C.POINTER(OptResult)]
        cls.decode.restype=C.c_int
        cls.samples=vectors()
    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()
    def setUp(self):
        # Explicit caller storage with native double alignment; reused every call.
        self.workspace=(C.c_double*((self.ws_size+7)//8))()
    def call(self,index,spec,prior=None,*,pixels=None,section=None,null_workspace=False,length=None):
        vector=self.samples[index]
        pixels=render(vector['directions'],spec) if pixels is None else pixels
        image=(C.c_uint8*len(pixels)).from_buffer_copy(pixels)
        cfg=Config(710,1000,*(section if section is not None else vector['section']))
        result=OptResult();C.memset(C.byref(result),0xa5,C.sizeof(result));before=bytes(result)
        status=self.decode(image,len(pixels) if length is None else length,spec.width,spec.height,
                           spec.width,C.byref(cfg),None if null_workspace else self.workspace,
                           None if prior is None else C.byref(prior),C.byref(result))
        if status:
            self.assertEqual(bytes(result),before,'failure changed output')
            if prior is not None:
                self.assertEqual(prior.valid,0,'failure preserved stale valid prior')
        else:
            self.assertEqual([result.decoded.x,result.decoded.y],vector['xy'],'false coordinate success')
            self.assertEqual(list(result.decoded.directions),vector['directions'])
        return status,result
    def test_extended_orthogonal_anisotropic_acquisition(self):
        for index,angle,ratio in [(0,-56,.6),(35,-36,.8),(67,32,1.2),(99,48,1.4)]:
            with self.subTest(index=index,angle=angle,ratio=ratio):
                prior=Prior()
                spec=Render(pitch=20,angle=angle,scale_y=ratio,noise=8,seed=index)
                code,out=self.call(index,spec,prior)
                self.assertEqual(code,0)
                self.assertEqual(out.used_warm_start,0)
                self.assertEqual(prior.valid,1)
                self.assertAlmostEqual(out.y_scale,ratio,delta=.11)
                self.assertAlmostEqual(out.decoded.angle_deg,angle,delta=2)
    def test_warm_start_redecodes_current_pixels_and_reuses_workspace(self):
        prior=Prior();spec=Render(pitch=20,angle=30,scale_y=.8,noise=7)
        code,cold=self.call(7,spec,prior);self.assertEqual(code,0)
        shifted=replace(spec,tx=spec.tx+1.2,ty=spec.ty-.75,seed=812)
        code,warm=self.call(7,shifted,prior);self.assertEqual(code,0)
        self.assertEqual(warm.used_warm_start,1)
        self.assertLess(warm.candidates,cold.candidates)
        # Geometry prior is not a cached coordinate: another paper window must decode anew.
        code,out=self.call(8,shifted,prior);self.assertEqual(code,0)
        self.assertEqual(out.used_warm_start,1)
        self.assertNotEqual(self.samples[7]['xy'],self.samples[8]['xy'])
    def test_stale_geometry_hint_falls_back(self):
        prior=Prior();first=Render(pitch=20,angle=-48,scale_y=.6)
        self.assertEqual(self.call(0,first,prior)[0],0)
        second=Render(pitch=24,angle=52,scale_y=1.2)
        code,out=self.call(0,second,prior);self.assertEqual(code,0)
        self.assertEqual(out.used_warm_start,0)
    def test_blank_occlusion_wrong_section_never_reuse_previous_result(self):
        spec=Render(pitch=20,angle=30,scale_y=.8)
        for case in ('blank','occluded','wrong_section'):
            with self.subTest(case=case):
                prior=Prior();self.assertEqual(self.call(0,spec,prior)[0],0)
                if case=='blank':
                    code,_=self.call(0,spec,prior,pixels=bytes([240])*(256*256))
                elif case=='occluded':
                    code,_=self.call(0,replace(spec,omit=(17,)),prior)
                else:
                    code,_=self.call(0,spec,prior,section=(1,1))
                self.assertNotEqual(code,0)
    def test_invalid_hints_fail_closed_or_reacquire(self):
        spec=Render(pitch=20,angle=16,scale_y=1.)
        for prior in (Prior(1,math.nan,0,1),Prior(1,20,math.inf,1),Prior(1,20,0,0),
                      Prior(99,20,0,1),Prior(1,-1,0,1),Prior(1,1e20,0,1)):
            code,out=self.call(3,spec,prior)
            # Either reject or freshly acquire; never a false-success coordinate.
            if code==0:
                self.assertEqual(out.used_warm_start,0)
        rng=random.Random(382)
        for _ in range(8):
            prior=Prior.from_buffer_copy(rng.randbytes(C.sizeof(Prior)))
            code,out=self.call(3,spec,prior)
            if code==0:
                self.assertEqual(out.used_warm_start,0)
    def test_unmodeled_projective_and_shear_never_false_success(self):
        for spec in (Render(perspective_x=.08,perspective_y=.05),Render(shear=.35),
                     Render(angle=80),Render(scale_y=.35)):
            self.call(5,spec,Prior())
    def test_api_buffer_and_workspace_contract(self):
        spec=Render();prior=Prior(1,18,0,1)
        self.assertNotEqual(self.call(0,spec,prior,null_workspace=True)[0],0)
        self.assertNotEqual(self.call(0,spec,prior,length=100)[0],0)
    def test_opt_object_has_no_heap_dependency(self):
        obj=Path(self.tmp.name)/'roi_opt.o'
        subprocess.run(['cc','-std=c11','-O2','-c',str(ROOT/'firmware/vision/roi_opt.c'),'-o',str(obj)],check=True)
        undefined=subprocess.check_output(['nm','-u',str(obj)],text=True)
        for forbidden in ('malloc','calloc','realloc','free'):
            self.assertFalse(any(line.split()[-1]==forbidden for line in undefined.splitlines()),undefined)

if __name__=='__main__':unittest.main()
