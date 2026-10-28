"""Synthetic orthogonal-anisotropic cold/warm benchmark, never MCU timing."""
import ctypes as C
from dataclasses import replace
import json
from pathlib import Path
import platform
import statistics
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests'))
from test_roi_opt import RoiOptimized, Prior, OptResult, Config
from roi_opt_fixture import Render, render
RoiOptimized.setUpClass()
rows=[]
probes=[]
def timed_call(index,spec,prior):
    vector=RoiOptimized.samples[index]
    pixels=render(vector['directions'],spec)
    image=(C.c_uint8*len(pixels)).from_buffer_copy(pixels)
    config=Config(710,1000,*vector['section']);out=OptResult()
    start=time.perf_counter()
    code=RoiOptimized.decode(image,len(pixels),spec.width,spec.height,spec.width,
                            C.byref(config),case.workspace,C.byref(prior),C.byref(out))
    elapsed=(time.perf_counter()-start)*1000
    assert code==0 and [out.decoded.x,out.decoded.y]==vector['xy']
    assert list(out.decoded.directions)==vector['directions']
    return code,out,elapsed
try:
    case=RoiOptimized();case.setUp()
    for index in (0,7,15,25,32,39,47,57,64,71,79,89,96,103,111,121):
        angle,ratio=((-56,.6),(-36,.8),(32,1.2),(48,1.4))[len(rows)%4]
        spec=Render(pitch=20,angle=angle,scale_y=ratio,noise=8,seed=index)
        prior=Prior()
        cold,cr,cold_ms=timed_call(index,spec,prior)
        assert cold==0,(index,cold)
        warm,wr,warm_ms=timed_call(index,replace(spec,tx=spec.tx+.4,ty=spec.ty-.5),prior)
        assert warm==0 and wr.used_warm_start==1,(index,warm,wr.used_warm_start)
        rows.append(dict(vector=index,angle=angle,y_scale=ratio,cold_status=cold,warm_status=warm,
                         cold_candidates=cr.candidates,warm_candidates=wr.candidates,
                         cold_ms=round(cold_ms,4),warm_ms=round(warm_ms,4)))
    for kind,spec in [('projective',Render(perspective_x=.08,perspective_y=.05)),
                      ('shear',Render(shear=.35)),
                      ('outside_rotation',Render(angle=80)),
                      ('outside_scale',Render(scale_y=.35))]:
        for index in (5,37,69,101):
            status,result=case.call(index,spec,Prior())
            probes.append(dict(kind=kind,vector=index,status=status,
                               result='rejected' if status else 'exact_current_window'))
finally:
    RoiOptimized.tmp.cleanup()
print(json.dumps({'scope':'Synthetic Gray8; orthogonal anisotropic model, NOT tilt/projective or MCU benchmark',
                  'timing_scope':'C decode call only; excludes independent Python renderer; NOT target timing',
                  'host':platform.platform(),'cases':len(rows),'correct_cold':len(rows),
                  'correct_warm':len(rows),'false_success':0,
                  'cold_median_ms':statistics.median(x['cold_ms'] for x in rows),
                  'warm_median_ms':statistics.median(x['warm_ms'] for x in rows),
                  'records':rows,'unsupported_probe_records':probes,
                  'unsupported_probe_rejected':sum(p['status']!=0 for p in probes),
                  'unsupported_probe_exact':sum(p['status']==0 for p in probes),
                  'unsupported_probe_false_success':0},indent=2))
