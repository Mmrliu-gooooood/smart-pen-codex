import unittest,tempfile,ctypes as C,sys
from pathlib import Path
from build import build,ROOT
sys.path.insert(0,str(ROOT/'tests'))
from test_roi_vision import Config
from test_roi_opt import OptResult
class CandidateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.lib=C.CDLL(str(build(cls.tmp.name,False)))
  cls.lib.candidate_workspace_size.restype=C.c_size_t
  cls.lib.candidate_decode.argtypes=[C.POINTER(C.c_uint8),C.c_size_t,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Config),C.c_void_p,C.POINTER(OptResult),C.c_void_p]
 def test_off_exact_active_positive(self):
  p=Path(__file__).resolve().parent.parent/'optics_paper_screen_20261031_1752/decoder_probe/001.pgm'
  pixels=p.read_bytes().split(b'\n',3)[3];im=(C.c_uint8*len(pixels)).from_buffer_copy(pixels);ws=(C.c_double*((self.lib.candidate_workspace_size()+7)//8))();out=OptResult()
  self.assertEqual(self.lib.candidate_decode(im,len(pixels),200,200,200,C.byref(Config(710,1000,0,0)),ws,C.byref(out),None),0)
  self.assertEqual((out.decoded.x,out.decoded.y),(156,51))
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
class AliasTests(CandidateTests):
 def test_output_diagnostics_alias_rejected_unchanged(self):
  p=Path(__file__).resolve().parent.parent/'optics_paper_screen_20261031_1752/decoder_probe/001.pgm'
  pixels=p.read_bytes().split(b'\n',3)[3];im=(C.c_uint8*len(pixels)).from_buffer_copy(pixels);ws=(C.c_double*((self.lib.candidate_workspace_size()+7)//8))();out=OptResult();C.memset(C.byref(out),0xa5,C.sizeof(out));before=bytes(out)
  self.assertEqual(self.lib.candidate_decode(im,len(pixels),200,200,200,C.byref(Config(710,1000,0,0)),ws,C.byref(out),C.byref(out)),-1)
  self.assertEqual(bytes(out),before)

if __name__=='__main__':unittest.main()
