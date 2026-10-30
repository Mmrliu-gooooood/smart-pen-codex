"""Bounded pixel-only continuous-frame API; synthetic fixtures, no geometry input."""
import ctypes as C
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from test_roi_vision import Config
from test_roi_opt import OptResult
ROOT=Path(__file__).resolve().parents[1]

class Transform(C.Structure):
    _fields_=[('origin_x',C.c_double),('origin_y',C.c_double),
              ('x_dx',C.c_double),('x_dy',C.c_double),
              ('y_dx',C.c_double),('y_dy',C.c_double)]
class FrameResult(C.Structure):
    _fields_=[('roi',OptResult),('left',C.c_uint16),('top',C.c_uint16),
              ('width',C.c_uint16),('height',C.c_uint16),
              ('edge_components',C.c_uint16),('edge_pixels',C.c_uint16),
              ('crop_attempts',C.c_uint8),('paper_to_frame',C.c_double*6),
              ('frame_to_paper',C.c_double*6),('refine_seeds',C.c_uint16),('refine_iterations',C.c_uint16),('refine_models',C.c_uint16)]

class ContinuousROI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();tmp=Path(cls.tmp.name)

        src=[ROOT/'firmware/vision/roi_continuous.c',ROOT/'firmware/vision/roi_opt.c',ROOT/'firmware/codec/anoto.c']
        subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-pedantic','-shared','-fPIC','-I'+str(ROOT/'firmware/vision'),str(ROOT/'tests/roi_refine_trace_bridge.c'),'-Wl,--wrap=pen_roi_decode_refined_transform',*map(str,src),'-lm','-o',str(tmp/'test.so')],check=True)
        cls.lib=C.CDLL(str(tmp/'test.so'));cls.lib.ws_size.restype=C.c_size_t;cls.lib.result_size.restype=C.c_size_t
        cls.ws_size=cls.lib.ws_size();cls.decode=cls.lib.pen_roi_decode_continuous
        cls.oracles=json.loads((ROOT/'tests/fixtures/continuous/manifest.json').read_text())['fixtures']
        cls.decode.argtypes=[C.POINTER(C.c_uint8),C.c_size_t,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Config),C.c_void_p,C.POINTER(FrameResult)]
        cls.decode.restype=C.c_int
    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()
    def setUp(self):self.ws=(C.c_double*((self.ws_size+7)//8))()
    def call(self,pixels,w=200,h=200,stride=None,section=(10,2),length=None,workspace=True):
        stride=w if stride is None else stride
        im=(C.c_uint8*len(pixels)).from_buffer_copy(pixels);before_im=bytes(im)
        cfg=Config(710,1000,*section);out=FrameResult();C.memset(C.byref(out),165,C.sizeof(out));before=bytes(out)
        rc=self.decode(im,len(pixels) if length is None else length,w,h,stride,C.byref(cfg),self.ws if workspace else None,C.byref(out))
        self.assertEqual(bytes(im),before_im)
        if rc:self.assertEqual(bytes(out),before,'failure changed output')
        return rc,out
    def fixture(self,fov,phase=0):
        return (ROOT/f'tests/fixtures/continuous/fov{fov}_roi200_phase{phase}.pgm').read_bytes().split(b'\n',3)[3]
    def test_profile_c_full_frames_select_current_pixel_roi(self):
        for fov in (5,6,7):
            for phase in (0,17):
                with self.subTest(fov=fov,phase=phase):
                    rc,out=self.call(self.fixture(fov,phase));self.assertEqual(rc,0)
                    self.assertEqual(out.roi.used_warm_start,0)
                    self.assertGreaterEqual(out.roi.decoded.dots,36);self.assertLessEqual(out.roi.decoded.dots,100)
                    self.assertEqual((out.width,out.height),(80,80) if fov==7 else (96,96))
                    self.assertEqual((out.left,out.top),((200-out.width)//2,)*2)
                    self.assertEqual(out.crop_attempts,2 if fov==7 else 1)
                    self.assertGreater(out.edge_components,0)
                    oracle=next(r for r in self.oracles if r['fov_mm']==fov and r['phase']==phase)
                    self.assertEqual(hashlib.sha256(self.fixture(fov,phase)).hexdigest(),oracle['image_sha256'])
                    x,y=out.roi.decoded.x,out.roi.decoded.y
                    expected=[oracle['directions'][yy-oracle['cell_top']][xx-oracle['cell_left']] for yy in range(y,y+6) for xx in range(x,x+6)]
                    self.assertEqual(list(out.roi.decoded.directions),expected)
                    a=out.paper_to_frame;p=60/fov
                    for yy in range(y,y+6):
                        for xx in range(x,x+6):
                            self.assertAlmostEqual(a[0]*xx+a[1]*yy+a[2],p*(xx-oracle['ox_cells'])-.5,delta=.1*p)
                            self.assertAlmostEqual(a[3]*xx+a[4]*yy+a[5],p*(yy-oracle['oy_cells'])-.5,delta=.1*p)
                    # Both transforms must be inverse, including paper translation.
                    a,b=out.paper_to_frame,out.frame_to_paper
                    for x,y in ((0,0),(127.25,247.75),(out.roi.decoded.x,out.roi.decoded.y)):
                        u=a[0]*x+a[1]*y+a[2];v=a[3]*x+a[4]*y+a[5]
                        self.assertAlmostEqual(b[0]*u+b[1]*v+b[2],x,places=8)
                        self.assertAlmostEqual(b[3]*u+b[4]*v+b[5],y,places=8)
    def test_reject_blank_bad_arguments_and_wrong_section(self):
        self.assertNotEqual(self.call(bytes([240])*40000)[0],0)
        good=self.fixture(6)
        for kwargs in ({'length':39999},{'workspace':False},{'w':95},{'w':257},{'stride':199},{'section':(63,2)},{'section':(1,1)}):
            self.assertNotEqual(self.call(good,**kwargs)[0],0)
    def test_large_edge_component_and_interior_damage_fail_closed(self):
        good=self.fixture(6)
        for x0,y0,x1,y1 in ((52,52,148,55),(90,90,110,110),(52,52,65,65)):
            im=bytearray(good)
            for y in range(y0,y1):im[y*200+x0:y*200+x1]=bytes([0])*(x1-x0)
            self.assertNotEqual(self.call(im)[0],0)
    def test_independent_deep_edge_ink_regression(self):
        for i in (63,64,65):
            im=(ROOT/f'tests/fixtures/continuous/case_{i:03d}.pgm').read_bytes().split(b'\n',3)[3]
            self.assertEqual(self.call(im)[0],-2,'deep border stroke erased')
    def test_fixed_rotation_scale_blur_damage_regressions(self):
        manifest=json.loads((ROOT/'tests/fixtures/continuous/extended_manifest.json').read_text())
        for row in manifest:
            with self.subTest(row=row['fixture']):
                im=(ROOT/'tests/fixtures/continuous'/row['fixture']).read_bytes().split(b'\n',3)[3]
                self.assertEqual(hashlib.sha256(im).hexdigest(),row['sha256'])
                rc,out=self.call(im);self.assertEqual(rc,row['status'])
                if not rc:
                    self.assertEqual((out.roi.decoded.x,out.roi.decoded.y),(row['x'],row['y']))
                    self.assertEqual(list(out.roi.decoded.directions),row['directions'])
                    a=out.paper_to_frame
                    for i,(u,v) in enumerate(row['grid_centers_frame']):
                        x=row['x']+i%6;y=row['y']+i//6
                        self.assertAlmostEqual(a[0]*x+a[1]*y+a[2],u,delta=.1*60/row['fov'])
                        self.assertAlmostEqual(a[3]*x+a[4]*y+a[5],v,delta=.1*60/row['fov'])
    def test_v3_refine_recovers_complete_fractional_and_rotated_windows(self):
        for name in ('extended_fov51.pgm','extended_rot45.pgm'):
            im=(ROOT/'tests/fixtures/continuous'/name).read_bytes().split(b'\n',3)[3]
            rc,out=self.call(im);self.assertEqual(rc,0)
            self.assertGreater(out.refine_seeds,0)
            self.assertLessEqual(out.refine_seeds,64)
            self.assertLessEqual(out.refine_iterations,320)
            self.assertLessEqual(out.roi.candidates,26965)
    def test_v3_actual_default_seed_overflow_rejects(self):
        im=(ROOT/'tests/fixtures/continuous/v3_seed_overflow.pgm').read_bytes().split(b'\n',3)[3]
        rc,_=self.call(im);self.assertEqual(rc,-4)
        stats=(C.c_uint32*4)();self.lib.get_last_refine_stats(stats)
        self.assertEqual(list(stats)[1:],[65,0,0])
        self.assertGreater(stats[0],0);self.assertLess(stats[0],26901)
    def test_v3_conflicting_complete_windows_never_first_success(self):
        for name,expected in (('v3_window_agree.pgm',0),('v3_window_conflict.pgm',-4)):
            im=(ROOT/'tests/fixtures/continuous'/name).read_bytes().split(b'\n',3)[3]
            rc,out=self.call(im);self.assertEqual(rc,expected)
            if not rc:
                self.assertEqual((out.roi.decoded.x,out.roi.decoded.y),(120,240))
                self.assertEqual(out.roi.decoded.windows,7)
    def test_v3_no_complete_window_is_not_inpainted(self):
        im=(ROOT/'tests/fixtures/continuous/v3_no_complete_window.pgm').read_bytes().split(b'\n',3)[3]
        rc,_=self.call(im);self.assertEqual(rc,-3)
        stats=(C.c_uint32*4)();self.lib.get_last_refine_stats(stats)
        self.assertEqual(stats[0],26901);self.assertGreater(stats[1],0)
    def test_bounded_workspace_and_no_heap(self):
        self.assertEqual(C.sizeof(FrameResult),self.lib.result_size())
        self.assertLessEqual(self.ws_size,32768)
        for name in ('roi_continuous','roi_opt'):
            obj=Path(self.tmp.name)/(name+'.o')
            subprocess.run(['cc','-std=c11','-O2','-c',str(ROOT/f'firmware/vision/{name}.c'),'-o',str(obj)],check=True)
            symbols=subprocess.check_output(['nm','-u',str(obj)],text=True)
            self.assertFalse(set(('malloc','calloc','realloc','free'))&{line.split()[-1] for line in symbols.splitlines()})
    def test_padded_stride_and_determinism(self):
        good=self.fixture(6);rc,first=self.call(good);self.assertEqual(rc,0)
        padded=b''.join(good[y*200:(y+1)*200]+b'\x00'*13 for y in range(200))
        rc,second=self.call(padded,stride=213);self.assertEqual(rc,0)
        self.assertEqual(bytes(first),bytes(second))

if __name__=='__main__':unittest.main()
