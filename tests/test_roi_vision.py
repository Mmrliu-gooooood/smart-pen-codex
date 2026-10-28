"""Raw grayscale acquisition tests, independently rasterized upstream patterns.

No grid origin, pitch, angle, dot coordinates or directions enter C API.
The fixtures are deterministic synthetic inputs, not real-camera validation.
"""
import ctypes as C
from dataclasses import replace
import random
from pathlib import Path
import subprocess
import tempfile
import time
import unittest

from roi_fixture import Render, render, vectors

ROOT = Path(__file__).resolve().parents[1]


class Config(C.Structure):
    _fields_ = [('paper_width', C.c_uint16), ('paper_height', C.c_uint16),
                ('section_u', C.c_uint8), ('section_v', C.c_uint8)]


class Result(C.Structure):
    _fields_ = [('x', C.c_uint16), ('y', C.c_uint16),
                ('dots', C.c_uint16), ('windows', C.c_uint16),
                ('pitch_px', C.c_float), ('angle_deg', C.c_float),
                ('residual_cells', C.c_float), ('directions', C.c_uint8*36)]


class RoiVision(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        so = Path(cls.tmp.name)/'roi.so'
        subprocess.run(['cc', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                        '-pedantic', '-shared', '-fPIC',
                        str(ROOT/'firmware/vision/roi.c'),
                        str(ROOT/'firmware/codec/anoto.c'), '-lm', '-o', str(so)], check=True)
        cls.lib = C.CDLL(str(so))
        cls.decode = cls.lib.pen_roi_decode
        cls.decode.argtypes = [C.POINTER(C.c_uint8), C.c_size_t,
                               C.c_uint, C.c_uint, C.c_uint,
                               C.POINTER(Config), C.POINTER(Result)]
        cls.decode.restype = C.c_int
        cls.samples = vectors()
        cls.timings = []

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()
        if cls.timings:
            print('ROI synthetic calls=%d host median_ms=%.3f max_ms=%.3f (not MCU timing)' % (
                len(cls.timings), sorted(cls.timings)[len(cls.timings)//2]*1000,
                max(cls.timings)*1000))

    def call(self, pixels, spec, vector, *, stride=None, length=None):
        stride = stride or spec.width
        if stride != spec.width:
            pixels = b''.join(pixels[y*spec.width:(y+1)*spec.width] +
                              bytes([7])*(stride-spec.width) for y in range(spec.height))
        image = (C.c_uint8*len(pixels)).from_buffer_copy(pixels)
        result = Result()
        C.memset(C.byref(result), 0xA5, C.sizeof(result))
        before = bytes(result)
        cfg = Config(710, 1000, *vector['section'])
        start = time.perf_counter()
        code = self.decode(image, len(pixels) if length is None else length,
                           spec.width, spec.height, stride, C.byref(cfg), C.byref(result))
        self.timings.append(time.perf_counter()-start)
        if code != 0:
            self.assertEqual(bytes(result), before, 'failure modified caller result')
        else:
            self.assertEqual([result.x, result.y], vector['xy'], 'false coordinate success')
            self.assertEqual(list(result.directions), vector['directions'])
        return code, result

    def test_translation_rotation_scale_and_noise(self):
        for index in (0, 7, 32, 39, 64, 71, 96, 103):
            for pitch, angle in ((12, -12), (18, 0), (24, 12)):
                with self.subTest(vector=index, pitch=pitch, angle=angle):
                    spec = Render(pitch=pitch, angle=angle, tx=39.35, ty=34.65,
                                  noise=12, seed=100+index)
                    code, result = self.call(render(self.samples[index]['directions'], spec),
                                             spec, self.samples[index])
                    self.assertEqual(code, 0)
                    self.assertAlmostEqual(result.pitch_px, pitch, delta=.9)
                    self.assertAlmostEqual(result.angle_deg, angle, delta=2)

    def test_padded_stride(self):
        spec = Render()
        self.assertEqual(self.call(render(self.samples[2]['directions'], spec), spec,
                                   self.samples[2], stride=spec.width+17)[0], 0)

    def test_perspective_and_other_offsets_never_false_success(self):
        # These probes deliberately do NOT promise perspective/other paper support.
        for perspective, offset in ((.003, 1/6), (.015, 1/6), (.06, 1/6),
                                     (0, .25), (0, .30)):
            for index in (3, 35, 67, 99):
                spec = Render(angle=7, perspective_x=perspective,
                              perspective_y=perspective/2, offset=offset, noise=8)
                self.call(render(self.samples[index]['directions'], spec), spec, self.samples[index])

    def test_missing_dots_fail_closed(self):
        for omit in ((0,), (17,), (0, 8, 20, 35), tuple(range(12))):
            spec = Render(omit=omit)
            self.assertNotEqual(self.call(render(self.samples[4]['directions'], spec),
                                         spec, self.samples[4])[0], 0)

    def test_negative_images(self):
        spec = Render()
        size = spec.width*spec.height
        rng = random.Random(301)
        negatives = [bytes([color])*size for color in (0, 127, 255)]
        negatives.append(bytes(rng.randrange(256) for _ in range(size)))
        negatives.append(bytes(0 if (x//5+y//5)%2 else 255
                               for y in range(spec.height) for x in range(spec.width)))
        negatives.append(render([0]*36, spec))
        # Ink stroke crossing real dots must not turn into a coordinate output.
        ink = render(self.samples[4]['directions'], spec)
        for y in range(spec.height):
            for x in range(65, 72):
                ink[y*spec.width+x] = 0
        negatives.append(ink)
        for index, image in enumerate(negatives):
            with self.subTest(negative=index):
                self.assertNotEqual(self.call(image, spec, self.samples[4])[0], 0)

    def test_adversarial_geometry_and_section(self):
        spec = Render()
        vector = self.samples[4]
        pixels = render(vector['directions'], spec)
        cases = {}
        cases['mirror'] = b''.join(pixels[y*spec.width:(y+1)*spec.width][::-1]
                                  for y in range(spec.height))
        cases['quarter_turn'] = bytes(pixels[(spec.height-1-x)*spec.width+y]
                                      for y in range(spec.height) for x in range(spec.width))
        cases['low_contrast'] = bytes(200 + p//10 for p in pixels)
        cropped = bytearray(pixels)
        for y in range(spec.height):
            for x in range(36):
                cropped[y*spec.width+x] = 240
        cases['boundary_crop'] = cropped
        extra = bytearray(pixels)
        for y in range(163, 166):
            for x in range(157, 160):
                extra[y*spec.width+x] = 30
        cases['extra_dot'] = extra
        crowded = bytearray([240]) * len(pixels)
        for y in range(4, 188, 8):
            for x in range(4, 188, 8):
                for dy in range(2):
                    for dx in range(2):
                        crowded[(y+dy)*spec.width+x+dx] = 30
        cases['too_many_components'] = crowded
        for name, image in cases.items():
            with self.subTest(case=name):
                self.assertNotEqual(self.call(image, spec, vector)[0], 0)
        wrong = dict(vector, section=[(vector['section'][0]+1)%63, vector['section'][1]])
        self.assertNotEqual(self.call(pixels, spec, wrong)[0], 0)

    def test_truncated_input(self):
        spec = Render()
        self.assertNotEqual(self.call(render(self.samples[0]['directions'], spec), spec,
                                     self.samples[0], length=spec.width*spec.height-1)[0], 0)


if __name__ == '__main__':
    unittest.main()
