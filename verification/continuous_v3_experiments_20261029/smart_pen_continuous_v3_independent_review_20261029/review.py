"""Independent V3 source snapshot replay, no oracle/config geometry fed to C."""
import sys
sys.dont_write_bytecode=True
import ctypes as C, json, hashlib, math, subprocess
from pathlib import Path
from collections import Counter
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parent;OLD=ROOT/'smart_pen_continuous_independent_review_20261029';AUD=ROOT/'smart_pen_viewport_audit_20261028';SNAP=P/'snapshot';V2=ROOT/'smart_pen_continuous_roi_candidate_20261028'
class Config(C.Structure):_fields_=[('paper_width',C.c_uint16),('paper_height',C.c_uint16),('section_u',C.c_uint8),('section_v',C.c_uint8)]
class Decoded(C.Structure):_fields_=[('x',C.c_uint16),('y',C.c_uint16),('dots',C.c_uint16),('windows',C.c_uint16),('pitch_px',C.c_float),('angle_deg',C.c_float),('residual_cells',C.c_float),('directions',C.c_uint8*36)]
class OptResult(C.Structure):_fields_=[('decoded',Decoded),('y_scale',C.c_float),('candidates',C.c_uint32),('used_warm_start',C.c_uint8)]
class Prior(C.Structure):_fields_=[('valid',C.c_uint32),('pitch_px',C.c_float),('angle_deg',C.c_float),('y_scale',C.c_float)]
class Result(C.Structure):_fields_=[('roi',OptResult),('left',C.c_uint16),('top',C.c_uint16),('width',C.c_uint16),('height',C.c_uint16),('edge_components',C.c_uint16),('edge_pixels',C.c_uint16),('crop_attempts',C.c_uint8),('paper_to_frame',C.c_double*6),('frame_to_paper',C.c_double*6),('refine_seeds',C.c_uint16),('refine_iterations',C.c_uint16),('refine_models',C.c_uint16)]
(P/'bridge.c').write_text('#include "roi_continuous.h"\nsize_t ws_size(void){return sizeof(pen_continuous_workspace);}\nsize_t result_size(void){return sizeof(pen_continuous_result);}\nsize_t core_ws_size(void){return sizeof(pen_roi_workspace);}\nsize_t core_result_size(void){return sizeof(pen_roi_opt_result);}\n')
subprocess.run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-pedantic','-shared','-fPIC','-I'+str(SNAP/'firmware/vision'),str(P/'bridge.c'),str(SNAP/'firmware/vision/roi_continuous.c'),str(SNAP/'firmware/vision/roi_opt.c'),str(SNAP/'firmware/codec/anoto.c'),'-lm','-o',str(P/'review.so')],check=True)
subprocess.run(['cc','-O2','-std=c11','-shared','-fPIC',str(V2/'firmware/vision/roi_opt.c'),str(V2/'firmware/codec/anoto.c'),'-lm','-o',str(P/'v2_oldapi.so')],check=True)
lib=C.CDLL(str(P/'review.so'));oldlib=C.CDLL(str(P/'v2_oldapi.so'))
for name in ('ws_size','result_size','core_ws_size','core_result_size'):getattr(lib,name).restype=C.c_size_t
assert lib.ws_size()==32640 and C.sizeof(Result)==lib.result_size()==192
assert C.sizeof(OptResult)==lib.core_result_size()==68
ws=(C.c_double*((lib.ws_size()+7)//8))();oldws=(C.c_double*((lib.core_ws_size()+7)//8))()
args=[C.POINTER(C.c_uint8),C.c_size_t,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Config),C.c_void_p]
lib.pen_roi_decode_continuous.argtypes=args+[C.POINTER(Result)]
for l in (lib,oldlib):l.pen_roi_decode_opt.argtypes=args+[C.POINTER(Prior),C.POINTER(OptResult)]
D=np.load(AUD/'upstream_directions.npy')
def read_pgm(path):
 magic,dims,maxval,pixels=path.read_bytes().split(b'\n',3);w,h=map(int,dims.split());assert magic==b'P5' and maxval==b'255' and len(pixels)==w*h
 return np.frombuffer(pixels,dtype=np.uint8).reshape(h,w)
def call(im,cfg=(710,1000,10,2)):
 im=np.ascontiguousarray(im);before=im.tobytes();out=Result();C.memset(C.byref(out),165,C.sizeof(out));old=bytes(out);h,w=im.shape;config=Config(*cfg)
 rc=lib.pen_roi_decode_continuous(im.ctypes.data_as(C.POINTER(C.c_uint8)),im.size,w,h,w,C.byref(config),ws,C.byref(out))
 assert im.tobytes()==before and (rc==0 or bytes(out)==old)
 row={'status':rc,'pixel_sha256':hashlib.sha256(before).hexdigest()}
 if rc==0:
  z=out.roi.decoded
  row.update(x=z.x,y=z.y,dots=z.dots,windows=z.windows,crop=[out.left,out.top,out.width,out.height],seeds=out.refine_seeds,iterations=out.refine_iterations,refined_models=out.refine_models,candidates=out.roi.candidates)
  assert not out.roi.used_warm_start and 36<=z.dots<=100 and out.refine_seeds<=64 and out.refine_iterations<=320
  assert out.roi.candidates-out.refine_models==26901,'OK skipped original coarse acquisition'
 return row,out

def oracle(row,out,fov,angle,cx,cy):
 if row['status']:return
 x,y=row['x'],row['y'];p=60/fov;rad=math.radians(angle);co,si=math.cos(rad),math.sin(rad)
 exact=list(out.roi.decoded.directions)==D[y:y+6,x:x+6].reshape(-1).tolist();assert exact
 a=np.array(out.paper_to_frame).reshape(2,3);b=np.array(out.frame_to_paper).reshape(2,3);errors=[];supported=True
 for r in range(6):
  for c in range(6):
   xx,yy=x+c,y+r;true=np.array([99.5+p*(co*(xx-cx)-si*(yy-cy)),99.5+p*(si*(xx-cx)+co*(yy-cy))]);fit=a@np.array([xx,yy,1]);errors.append(float(np.linalg.norm(true-fit)));assert np.max(np.abs(b@np.r_[fit,1]-[xx,yy]))<1e-8
   dx,dy=((0,-1),(-1,0),(1,0),(0,1))[D[yy,xx]];dot=np.array([99.5+p*(co*(xx+dx/6-cx)-si*(yy+dy/6-cy)),99.5+p*(si*(xx+dx/6-cx)+co*(yy+dy/6-cy))]);supported &= out.left<=dot[0]<=out.left+out.width-1 and out.top<=dot[1]<=out.top+out.height-1
 assert supported and max(errors)<=.1*p
 row.update(exact_symbols=True,window_supported=True,max_grid_error_px=max(errors))

# Own copy of the prior independent inverse rasterizer; no V3 generator import.
def render(fov,cx,cy):
 p=60/fov;cov=np.zeros((200,200));yy,xx=np.mgrid[:200,:200]
 for sy in range(4):
  for sx in range(4):
   u=(xx+(sx+.5)/4-100)/p+cx;v=(yy+(sy+.5)/4-100)/p+cy;x=np.rint(u).astype(int);y=np.rint(v).astype(int);d=D[y,x];dx=np.choose(d,[0,-1,1,0])/6;dy=np.choose(d,[-1,0,0,1])/6;cov+=(u-x-dx)**2+(v-y-dy)**2<=1/36
 return np.clip(np.rint(240-210*cov/16),0,255).astype(np.uint8)

legacy=[]
for item in json.loads((AUD/'regression_manifest.json').read_text())['fixtures']:
 im=read_pgm(AUD/item['fixture']);h,w=im.shape;arr=(C.c_uint8*im.size).from_buffer_copy(im.tobytes());cfg=Config(710,1000,10,2);new=OptResult();old=OptResult();C.memset(C.byref(new),165,C.sizeof(new));C.memset(C.byref(old),165,C.sizeof(old))
 rc=lib.pen_roi_decode_opt(arr,im.size,w,h,w,C.byref(cfg),ws,None,C.byref(new));rc2=oldlib.pen_roi_decode_opt(arr,im.size,w,h,w,C.byref(cfg),oldws,None,C.byref(old));assert rc==rc2==item['cold']['status'];assert bytes(new)==bytes(old)
 if not rc:
  p1=Prior(1,new.decoded.pitch_px,new.decoded.angle_deg,new.y_scale);p2=Prior.from_buffer_copy(bytes(p1))
  rc=lib.pen_roi_decode_opt(arr,im.size,w,h,w,C.byref(cfg),ws,C.byref(p1),C.byref(new));rc2=oldlib.pen_roi_decode_opt(arr,im.size,w,h,w,C.byref(cfg),oldws,C.byref(p2),C.byref(old));assert rc==rc2==0 and bytes(new)==bytes(old) and bytes(p1)==bytes(p2)
 legacy.append({'fixture':item['fixture'],'identical':True})
(P/'legacy44.json').write_text(json.dumps(legacy,indent=2))

replay=[];v2rows=json.loads((OLD/'v2/replay_v1.json').read_text());source=json.loads((OLD/'results.json').read_text())
for i,s in enumerate(source):
 config={'wrong_section':(710,1000,11,3),'excluded_x':(100,1000,10,2),'excluded_y':(710,100,10,2),'invalid_bounds':(5,1000,10,2)}.get(s['kind'],(710,1000,10,2))
 im=read_pgm(OLD/s['fixture']);row,out=call(im,config);assert row['pixel_sha256']==s['image_sha256'];row.update(fixture=s['fixture'],kind=s['kind'],v2_status=v2rows[i]['status'])
 if s['kind']=='positive':oracle(row,out,s['fov'],s['angle'],s['cx'],s['cy'])
 elif s['kind']=='edge_ink':oracle(row,out,6,0,320.317,550.681);row['depth']=s['depth']
 if s['kind']!='positive':assert row['status']==v2rows[i]['status'],'negative/boundary policy changed'
 if v2rows[i]['status']==0:assert row['status']==0,'V2 accepted case regressed'
 replay.append(row);print('replay',i,s['kind'],row['v2_status'],'->',row['status'],flush=True)
(P/'replay72.json').write_text(json.dumps(replay,indent=2))
phase=[]
for s in json.loads((OLD/'v2/phase.json').read_text()):
 im=render(s['fov'],330+s['fx'],560+s['fy']);assert hashlib.sha256(im.tobytes()).hexdigest()==s['image_sha256'];row,out=call(im);assert row['status']==0;oracle(row,out,s['fov'],0,330+s['fx'],560+s['fy']);row.update(fov=s['fov'],fx=s['fx'],fy=s['fy']);phase.append(row)
(P/'phase48.json').write_text(json.dumps(phase,indent=2))
fragments=[]
for s in json.loads((OLD/'v2/fragments.json').read_text())+[json.loads((OLD/'v2/corner_control.json').read_text())]:
 im=read_pgm(OLD/'v2'/s['fixture']);row,out=call(im);assert row['status']==s['status']
 cx,cy=(330.125,560.125) if s['kind']=='isolated_corner4x1' else (320.317,550.681);oracle(row,out,6,0,cx,cy);row.update(fixture=s['fixture'],kind=s['kind']);fragments.append(row)
(P/'fragments6.json').write_text(json.dumps(fragments,indent=2))
missing=[]
for s in json.loads((ROOT/'smart_pen_continuous_fit_diagnostic_20261029/results.json').read_text()):
 if s['status']!=0 and s['oracle_diagnosis_only']['complete_true_windows']==0:
  im=read_pgm(ROOT/'smart_pen_continuous_fit_diagnostic_20261029/pixels'/f'case_{s["index"]:03d}.pgm');row,out=call(im);assert row['status']==-3;row.update(index=s['index']);missing.append(row)
assert len(missing)==20
(P/'missing_window20.json').write_text(json.dumps(missing,indent=2))
summary={'legacy_api_identical':len(legacy),'replay72':dict(Counter(r['status'] for r in replay)),'positive54':dict(Counter(r['status'] for r in replay if r['kind']=='positive')),'v2_positive_ok':29,'new_positive_accepts':sum(r['kind']=='positive' and r['v2_status']!=0 and r['status']==0 for r in replay),'phase48_ok':len(phase),'fragment_probes':len(fragments),'missing20_rejected':len(missing),'workspace_bytes':lib.ws_size(),'max_grid_error_px':max(r.get('max_grid_error_px',0) for r in replay+phase+fragments)}
(P/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
