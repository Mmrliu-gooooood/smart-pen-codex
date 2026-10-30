"""Independent byte-for-byte C/Python interoperability tests (requires cc)."""
import ctypes
import random
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest
import zlib

from software.pen_bridge import Packet


class Sample(ctypes.Structure):
    _fields_ = [('device',ctypes.c_uint32),('seq',ctypes.c_uint32),
                ('page',ctypes.c_uint32),('session',ctypes.c_uint64),
                ('timestamp_us',ctypes.c_uint64),('x_um',ctypes.c_int32),
                ('y_um',ctypes.c_int32),('confidence',ctypes.c_uint16),
                ('flags',ctypes.c_uint8)]


class CrosswireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler=shutil.which('cc')
        if compiler is None:
            raise unittest.SkipTest('C compiler unavailable; crosswire NOT verified')
        cls.temp=tempfile.TemporaryDirectory()
        root=Path(__file__).resolve().parents[1]
        library=Path(cls.temp.name)/'pen.so'
        subprocess.run([compiler,'-std=c11','-Wall','-Wextra','-Werror','-pedantic',
                        '-shared','-fPIC',str(root/'firmware/portable/pen.c'),
                        '-o',str(library)],check=True,capture_output=True,text=True)
        cls.lib=ctypes.CDLL(str(library))
        cls.lib.pen_encode.argtypes=[ctypes.POINTER(ctypes.c_uint8),ctypes.POINTER(Sample)]
        cls.lib.pen_encode.restype=ctypes.c_int
        cls.lib.pen_decode.argtypes=[ctypes.POINTER(Sample),ctypes.POINTER(ctypes.c_uint8)]
        cls.lib.pen_decode.restype=ctypes.c_int

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def roundtrip(self,p):
        sample=Sample(**p.__dict__)
        out=(ctypes.c_uint8*48)()
        self.assertEqual(self.lib.pen_encode(out,ctypes.byref(sample)),0)
        self.assertEqual(bytes(out),p.encode())
        self.assertEqual(Packet.decode(bytes(out)),p)
        decoded=Sample()
        incoming=(ctypes.c_uint8*48).from_buffer_copy(p.encode())
        self.assertEqual(self.lib.pen_decode(ctypes.byref(decoded),incoming),0)
        self.assertEqual({name:getattr(decoded,name) for name in p.__dict__},p.__dict__)

    def test_signed_unsigned_edges(self):
        for coordinate in [-2**31,-1,0,1,2**31-1]:
            for session in [1,2**63-1,2**63,2**64-1]:
                self.roundtrip(Packet(7,2**32-1,session,2**32-1,2**64-1,
                                      2**32-1,coordinate,-1-coordinate,1000))

    def test_512_deterministic_random_vectors(self):
        rng=random.Random(0x535031)
        for _ in range(512):
            self.roundtrip(Packet(rng.randrange(8),rng.randrange(2**32),
                                  rng.randrange(1,2**64),rng.randrange(2**32),
                                  rng.randrange(2**64),rng.randrange(1,2**32),
                                  rng.randrange(-2**31,2**31),rng.randrange(-2**31,2**31),
                                  rng.randrange(1001)))

    def test_corruption_and_semantics_fail_closed_in_both(self):
        original=Packet(3,1,1,0,123,1,-1,2,900).encode()
        cases=[]
        for i in range(48):
            raw=bytearray(original);raw[i]^=1;cases.append(raw)
        for offset,value in [(2,2),(3,8),(42,1),(28,0),(8,0)]:
            raw=bytearray(original);raw[offset]=value
            raw[44:]=struct.pack('<I',zlib.crc32(raw[:44]));cases.append(raw)
        for raw in cases:
            before=Sample(device=12345)
            self.assertEqual(self.lib.pen_decode(ctypes.byref(before),
                (ctypes.c_uint8*48).from_buffer_copy(raw)),-1)
            self.assertEqual(before.device,12345)
            with self.assertRaises(ValueError): Packet.decode(raw)

if __name__=='__main__': unittest.main()
