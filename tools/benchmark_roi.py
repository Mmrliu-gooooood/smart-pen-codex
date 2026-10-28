"""Reproducible host-only synthetic benchmark; emits JSON, never MCU claims."""
import ctypes as C
import json
from pathlib import Path
import platform
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tests'))
from test_roi_vision import Config, Result, RoiVision
from roi_fixture import Render, render

RoiVision.setUpClass()
records = []
try:
    for index, vector in enumerate(RoiVision.samples):
        for transform in range(2):
            spec = (Render() if transform == 0 else Render(
                pitch=(12,18,24)[index%3], angle=(-12,0,12)[index%3],
                tx=39.35, ty=34.65, noise=12, seed=100+index))
            pixels = render(vector['directions'], spec)
            image = (C.c_uint8*len(pixels)).from_buffer_copy(pixels)
            cfg = Config(710,1000,*vector['section']); result = Result()
            start = time.perf_counter()
            code = RoiVision.decode(image,len(pixels),spec.width,spec.height,spec.width,
                                    C.byref(cfg),C.byref(result))
            elapsed = (time.perf_counter()-start)*1000
            correct = (code == 0 and [result.x,result.y] == vector['xy'] and
                       list(result.directions) == vector['directions'])
            records.append({'vector':index, 'transform':transform,'status':code,
                            'correct':correct,'ms':round(elapsed,4)})
finally:
    RoiVision.tmp.cleanup()
ms = [r['ms'] for r in records]
report = {'scope':'synthetic Gray8, upstream independent a4_fixed vectors; NOT real camera or MCU',
          'host':platform.platform(), 'python':platform.python_version(),
          'compiler_flags':'-std=c11 -O2 -Wall -Wextra -Werror -pedantic -shared -fPIC',
          'samples':len(records),'exact_success':sum(r['correct'] for r in records),
          'rejected':sum(r['status']!=0 for r in records),
          'false_success':sum(r['status']==0 and not r['correct'] for r in records),
          'median_ms':statistics.median(ms),'max_ms':max(ms), 'records':records}
print(json.dumps(report,indent=2))
if report['exact_success'] != report['samples']:
    raise SystemExit(1)
