"""Independent continuous-paper synthetic gate; no oracle enters C decoder.
Run with pinned upstream directions from the separate viewport audit.
"""
import argparse
import ctypes as C
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests'))
from test_roi_continuous import ContinuousROI,FrameResult
from test_roi_vision import Config


def project(x,y,s):
    p=60/s['fov'];co=math.cos(math.radians(s.get('angle',0)));si=math.sin(math.radians(s.get('angle',0)))
    qx=x-s['ox']-100/p;qy=y-s['oy']-100/p
    den=1+s.get('perspective_x',0)*qx+s.get('perspective_y',0)*qy
    u=qx+s.get('shear',0)*qy;v=qy*s.get('ratio',1)
    return 100+p*(co*u-si*v)/den,100+p*(si*u+co*v)/den


def render(dirs,s):
    p=60/s['fov'];co=math.cos(math.radians(s.get('angle',0)));si=math.sin(math.radians(s.get('angle',0)))
    image=np.full((200,200),240,dtype=np.uint8);omitted=set(map(tuple,s.get('omit',[])))
    center_x=s['ox']+100/p;center_y=s['oy']+100/p
    # generous spatial domain; fixture parameters keep this wholly in paper.
    for y in range(math.floor(center_y)-30,math.ceil(center_y)+31):
        for x in range(math.floor(center_x)-30,math.ceil(center_x)+31):
            if (x,y) in omitted:continue
            dx,dy=((0,-1),(-1,0),(1,0),(0,1))[dirs[y,x]]
            cx=x+dx/6;cy=y+dy/6;radius=1/6
            bb=[project(cx+rx,cy+ry,s) for rx in (-radius,radius) for ry in (-radius,radius)]
            x0=max(0,math.floor(min(t[0] for t in bb))-1);x1=min(200,math.ceil(max(t[0] for t in bb))+1)
            y0=max(0,math.floor(min(t[1] for t in bb))-1);y1=min(200,math.ceil(max(t[1] for t in bb))+1)
            if x1<=x0 or y1<=y0:continue
            yy,xx=np.mgrid[y0:y1,x0:x1];cov=np.zeros_like(xx)
            for sy in range(4):
                for sx in range(4):
                    u=(xx+(sx+.5)/4-100)/p;v=(yy+(sy+.5)/4-100)/p
                    qy=(-si*u+co*v)/s.get('ratio',1);qx=co*u+si*v-s.get('shear',0)*qy
                    denominator=1-s.get('perspective_x',0)*qx-s.get('perspective_y',0)*qy
                    qx=qx/denominator+center_x;qy=qy/denominator+center_y
                    cov+=((qx-cx)**2+(qy-cy)**2<=radius**2)&(denominator>0)
            image[y0:y1,x0:x1]=np.minimum(image[y0:y1,x0:x1],240-np.rint(210*cov/16).astype(np.uint8))
    if s.get('blur',0):
        # Deterministic separable Gaussian, no OpenCV/Pillow kernel dependence.
        sigma=s['blur'];r=math.ceil(3*sigma);k=np.exp(-np.arange(-r,r+1)**2/(2*sigma*sigma));k/=k.sum()
        buf=image.astype(float)
        for axis in (0,1):buf=np.apply_along_axis(lambda v:np.convolve(np.pad(v,r,mode='edge'),k,mode='valid'),axis,buf)
        image=np.rint(buf).astype(np.uint8)
    if s.get('noise',0):
        rng=np.random.default_rng(s.get('seed',13579));n=s['noise']
        image=np.clip(image.astype(np.int16)+rng.integers(-n,n+1,image.shape),0,255).astype(np.uint8)
    damage=s.get('damage')
    if damage=='stroke': image[94:98,40:160]=30
    if damage=='edge_stroke': image[51:55,40:160]=30
    if damage=='blob': image[85:115,85:115]=30
    if damage=='erase': image[88:112,88:112]=240
    if damage=='full_black': image[:]=0
    if damage=='blank': image[:]=240
    if damage=='checker': image[:]=np.indices(image.shape).sum(axis=0)%2*210+30
    if damage=='random_pixels': image[:]=np.random.default_rng(s.get('seed',13579)).integers(0,256,image.shape,dtype=np.uint8)
    if damage=='contrast': image[:]=200+np.rint((image.astype(float)-30)*.15).astype(np.uint8)
    return image


class RefineStats(C.Structure):
    _fields_=[(k,C.c_uint32) for k in ('cold_candidates','seeds','iterations','refined_models')]

def evaluate(lib,ws,im,s,dirs):
    image=np.ascontiguousarray(im);before=image.copy();cfg=Config(710,1000,*s.get('section',(10,2)))
    result=FrameResult();C.memset(C.byref(result),165,C.sizeof(result));old=bytes(result)
    lib.reset_last_refine_stats()
    start=time.perf_counter();status=lib.pen_roi_decode_continuous(image.ctypes.data_as(C.POINTER(C.c_uint8)),image.size,200,200,200,C.byref(cfg),ws,C.byref(result));seconds=time.perf_counter()-start
    assert np.array_equal(before,image),'input modified'
    assert not status or bytes(result)==old,'failure modified result'
    stats=RefineStats();lib.get_last_refine_stats(C.byref(stats))
    record={**s,'status':status,'seconds':seconds,'sha256':hashlib.sha256(image.tobytes()).hexdigest(),'fit_diagnostics':{k:getattr(stats,k) for k,_ in RefineStats._fields_}}
    if status==0:
        x,y=result.roi.decoded.x,result.roi.decoded.y;a=result.paper_to_frame
        match=list(result.roi.decoded.directions)==dirs[y:y+6,x:x+6].reshape(-1).tolist()
        errors=[];contained=True;omitted=set(map(tuple,s.get('omit',[])))
        for yy in range(y,y+6):
            for xx in range(x,x+6):
                px,py=project(xx,yy,s);predx=a[0]*xx+a[1]*yy+a[2];predy=a[3]*xx+a[4]*yy+a[5]
                errors.append(math.hypot(predx-(px-.5),predy-(py-.5)))
                dx,dy=((0,-1),(-1,0),(1,0),(0,1))[dirs[yy,xx]]
                cx,cy=project(xx+dx/6,yy+dy/6,s)
                contained &= result.left<=cx<result.left+result.width and result.top<=cy<result.top+result.height and (xx,yy) not in omitted
        allowed=not s.get('must_reject',False)
        record.update(x=x,y=y,roi=result.width,left=result.left,top=result.top,dots=result.roi.decoded.dots,windows=result.roi.decoded.windows,
                      edge_components=result.edge_components,edge_pixels=result.edge_pixels,attempts=result.crop_attempts,candidates=result.roi.candidates,
                      fitted_angle=result.roi.decoded.angle_deg,fitted_pitch=result.roi.decoded.pitch_px,fitted_y_scale=result.roi.y_scale,
                      exact_symbols=match,window_supported=bool(contained),transform_max_error_px=max(errors),
                      correct=bool(match and contained and max(errors)<=.10*(60/s['fov']) and allowed),
                      refine_seeds=result.refine_seeds,refine_iterations=result.refine_iterations,refine_models=result.refine_models)
    return record


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--audit',type=Path,default=ROOT.parent/'smart_pen_viewport_audit_20261028');ap.add_argument('--out',type=Path,default=ROOT/'verification/continuous');a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    provenance={'source_base':subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),'compiler':subprocess.check_output(['cc','--version'],text=True).splitlines()[0],
                'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'firmware/vision/roi_continuous.c',ROOT/'firmware/vision/roi_continuous.h',ROOT/'firmware/vision/roi_opt.c',ROOT/'firmware/vision/roi_opt.h',Path(__file__)]},
                'audit_direction_sha256':hashlib.sha256((a.audit/'upstream_directions.npy').read_bytes()).hexdigest()}
    (a.out/'provenance.json').write_text(json.dumps(provenance,indent=2))
    dirs=np.load(a.audit/'upstream_directions.npy');old=json.loads((a.audit/'results.json').read_text())
    cases=[]
    for r in old:
        if r['size']==200:cases.append(dict(group='baseline',fov=r['fov_mm'],phase=r['phase'],ox=r['ox_cells'],oy=r['oy_cells'],baseline_sha256=r['image_sha256']))
    origins=[r for r in cases if r['fov']==6]
    for fov in (5,6,7):
        for angle in (-60,-45,-30,-14,14,30,45,60):
            for phase in (0,7,17,26):
                ref=origins[phase];cases.append(dict(group='rotation',fov=fov,ox=ref['ox'],oy=ref['oy'],phase=phase,angle=angle))
    for fov in (5.1,5.3,5.5,5.7,6.1,6.3,6.5,6.7,6.9):
        for phase in (0,7,17,26):
            ref=origins[phase];cases.append(dict(group='fractional_fov',fov=fov,ox=ref['ox'],oy=ref['oy'],phase=phase))
    for fov in (5,6,7):
        for blur in (.4,.8,1.2,1.6):
            for phase in (0,17):
                ref=origins[phase];cases.append(dict(group='blur',fov=fov,ox=ref['ox'],oy=ref['oy'],phase=phase,blur=blur))
        for noise in (8,20,40):
            ref=origins[0];cases.append(dict(group='noise',fov=fov,ox=ref['ox'],oy=ref['oy'],noise=noise))
        for damage in ('stroke','edge_stroke','blob','erase','full_black','blank','checker','random_pixels','contrast'):
            ref=origins[0];cases.append(dict(group='damage',fov=fov,ox=ref['ox'],oy=ref['oy'],damage=damage,must_reject=damage!='erase'))
        for perturb in (dict(shear=.05),dict(shear=.35),dict(perspective_x=.01,perspective_y=.005),dict(perspective_x=.05,perspective_y=.03),dict(ratio=.6),dict(ratio=1.4),dict(angle=80)):
            ref=origins[0];cases.append(dict(group='model_boundary',fov=fov,ox=ref['ox'],oy=ref['oy'],**perturb))
        ref=origins[0];cases.append(dict(group='wrong_section',fov=fov,ox=ref['ox'],oy=ref['oy'],section=[1,1],must_reject=True))
    for seed in range(16):
        ref=origins[seed];cases.append(dict(group='fake_dots',fov=(5,6,7)[seed%3],ox=ref['ox'],oy=ref['oy'],seed=seed,must_reject=True))
    ContinuousROI.setUpClass();lib=ContinuousROI.lib;ws=(C.c_double*((ContinuousROI.ws_size+7)//8))();results=[]
    try:
        for index,s in enumerate(cases):
            source=dirs
            if s['group']=='fake_dots':source=np.random.default_rng(s['seed']).integers(0,4,dirs.shape,dtype=np.uint8)
            im=render(source,s)
            if s['group']=='baseline':assert hashlib.sha256(im.tobytes()).hexdigest()==s['baseline_sha256'],'renderer differs from frozen upstream baseline'
            rec=evaluate(lib,ws,im,s,dirs);results.append(rec)
            if rec['status']==0 and not rec['correct']:
                name=f'false_{index}.pgm';(a.out/name).write_bytes(b'P5\n200 200\n255\n'+im.tobytes());rec['fixture']=name
            (a.out/'results.json').write_text(json.dumps(results,indent=2))
            print(f'{index+1}/{len(cases)} {s["group"]} FOV={s["fov"]} status={rec["status"]} correct={rec.get("correct")}',flush=True)
    finally:ContinuousROI.tearDownClass()
    summaries=[]
    for group in sorted(set(r['group'] for r in results)):
        rows=[r for r in results if r['group']==group];ok=[r for r in rows if r['status']==0]
        summaries.append(dict(group=group,n=len(rows),statuses=dict(Counter(r['status'] for r in rows)),false_success=sum(not r['correct'] for r in ok),max_transform_error_px=max((r['transform_max_error_px'] for r in ok),default=None),host_median_ms=float(np.median([r['seconds'] for r in rows])*1000),host_max_ms=max(r['seconds'] for r in rows)*1000))
    (a.out/'summary.json').write_text(json.dumps(dict(synthetic_only=True,workspace_bytes=ContinuousROI.ws_size,cases=len(results),groups=summaries),indent=2));print(json.dumps(summaries,indent=2))
    return int(any(not r['correct'] for r in results if r['status']==0) or any(r['status']!=0 for r in results if r['group']=='baseline'))
if __name__=='__main__':sys.exit(main())
