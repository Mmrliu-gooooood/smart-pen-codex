import numpy as np,ctypes as C,json,sys,subprocess,hashlib,math
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parent;ROOT=P.parent;SNAP=P/'snapshot';BASE=ROOT/'smart_pen_vision_opt_20261028';AUD=ROOT/'smart_pen_viewport_audit_20261028'
sys.path.insert(0,str(BASE/'tests'))
from test_roi_vision import Config
from test_roi_opt import OptResult,Prior
class Result(C.Structure):
 _fields_=[('roi',OptResult),('left',C.c_uint16),('top',C.c_uint16),('width',C.c_uint16),('height',C.c_uint16),('edge_components',C.c_uint16),('edge_pixels',C.c_uint16),('crop_attempts',C.c_uint8),('paper_to_frame',C.c_double*6),('frame_to_paper',C.c_double*6)]
(P/'bridge.c').write_text('#include "roi_continuous.h"\nsize_t ws_size(void){return sizeof(pen_continuous_workspace);}\n')
subprocess.run(['cc','-std=c11','-O2','-shared','-fPIC','-I'+str(SNAP/'firmware/vision'),str(P/'bridge.c'),str(SNAP/'firmware/vision/roi_continuous.c'),str(SNAP/'firmware/vision/roi_opt.c'),str(SNAP/'firmware/codec/anoto.c'),'-lm','-o',str(P/'review.so')],check=True)
lib=C.CDLL(str(P/'review.so'));lib.ws_size.restype=C.c_size_t;ws=(C.c_double*((lib.ws_size()+7)//8))();lib.pen_roi_decode_continuous.argtypes=[C.POINTER(C.c_uint8),C.c_size_t,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Config),C.c_void_p,C.POINTER(Result)]
lib.pen_roi_decode_opt.argtypes=[C.POINTER(C.c_uint8),C.c_size_t,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Config),C.c_void_p,C.POINTER(Prior),C.POINTER(OptResult)]
D=np.load(AUD/'upstream_directions.npy');rng=np.random.default_rng(29100351);records=[]
def call(im,config=(710,1000,10,2)):
 im=np.ascontiguousarray(im);before=im.tobytes();out=Result();C.memset(C.byref(out),165,C.sizeof(out));old=bytes(out);h,w=im.shape;cfg=Config(*config)
 status=lib.pen_roi_decode_continuous(im.ctypes.data_as(C.POINTER(C.c_uint8)),im.size,w,h,w,C.byref(cfg),ws,C.byref(out));assert before==im.tobytes();assert status==0 or bytes(out)==old
 r={'status':status,'image_sha256':hashlib.sha256(before).hexdigest()}
 if status==0:
  z=out.roi.decoded;r.update(x=z.x,y=z.y,dots=z.dots,windows=z.windows,roi=[out.left,out.top,out.width,out.height],edge_components=out.edge_components,edge_pixels=out.edge_pixels,used_warm=out.roi.used_warm_start)
  assert not out.roi.used_warm_start and 36<=z.dots<=100
 return r,out
# Independent inverse rasterizer, full continuous paper. No upstream existing renderer reuse.
def render(fov,angle,cx,cy,noise=0,blur=0):
 p=60/fov;t=math.radians(angle);co,si=math.cos(t),math.sin(t);cov=np.zeros((200,200));yy,xx=np.mgrid[:200,:200]
 for sy in range(4):
  for sx in range(4):
   ix=(xx+(sx+.5)/4-100)/p;iy=(yy+(sy+.5)/4-100)/p;u=co*ix+si*iy+cx;v=-si*ix+co*iy+cy;x=np.rint(u).astype(int);y=np.rint(v).astype(int);d=D[y,x];dx=np.choose(d,[0,-1,1,0])/6;dy=np.choose(d,[-1,0,0,1])/6;cov+=(u-x-dx)**2+(v-y-dy)**2 <=1/36
 im=240-210*cov/16
 for _ in range(blur):
  pad=np.pad(im,1,mode='edge');im=sum(pad[j:j+200,k:k+200] for j in range(3) for k in range(3))/9
 if noise:im+=rng.integers(-noise,noise+1,im.shape)
 return np.clip(np.rint(im),0,255).astype(np.uint8)
def check_truth(r,o,fov,angle,cx,cy):
 if r['status']:return
 x,y=r['x'],r['y'];r['symbols_correct']=list(o.roi.decoded.directions)==D[y:y+6,x:x+6].reshape(-1).tolist();assert r['symbols_correct']
 p=60/fov;t=math.radians(angle);co,si=math.cos(t),math.sin(t);a=np.array(o.paper_to_frame).reshape(2,3);b=np.array(o.frame_to_paper).reshape(2,3);errors=[];supported=True
 for yy in range(y,y+6):
  for xx in range(x,x+6):
   true=np.array([99.5+p*(co*(xx-cx)-si*(yy-cy)),99.5+p*(si*(xx-cx)+co*(yy-cy))]);fit=a@np.array([xx,yy,1]);errors.append(float(np.linalg.norm(true-fit)));back=b@np.r_[fit,1];assert np.max(np.abs(back-[xx,yy]))<1e-8
   supported &= o.left-p/3<=true[0]<=o.left+o.width+p/3 and o.top-p/3<=true[1]<=o.top+o.height+p/3
 r['max_grid_error_px']=max(errors);r['supported']=bool(supported);assert supported and max(errors)<.25*p
# Original API regression is independent of wrapper's >=96 frame contract.
reg=[]
for old in json.loads((AUD/'regression_manifest.json').read_text())['fixtures']:
 magic,dims,m,pix=(AUD/old['fixture']).read_bytes().split(b'\n',3);w,h=map(int,dims.split());im=(C.c_uint8*len(pix)).from_buffer_copy(pix);out=OptResult();C.memset(C.byref(out),165,C.sizeof(out));before=bytes(out);cfg=Config(710,1000,10,2)
 status=lib.pen_roi_decode_opt(im,len(pix),w,h,w,C.byref(cfg),ws,None,C.byref(out));assert status==old['cold']['status'];assert status==0 or bytes(out)==before
 if not status:assert (out.decoded.x,out.decoded.y)==(old['cold']['x'],old['cold']['y'])
 reg.append({'fixture':old['fixture'],'status':status,'passed':True})
(P/'old_api_regression.json').write_text(json.dumps(reg,indent=2))
def save(r,im):
 name=f'case_{len(records):03d}.pgm';(P/name).write_bytes(b'P5\n200 200\n255\n'+im.tobytes());r['fixture']=name;records.append(r);(P/'results.json').write_text(json.dumps(records,indent=2));print(r,flush=True)
for i in range(54):
 fov=(5,6,7)[i%3];angle=(0,7,-19,32,-46,58)[i%6] + float(rng.uniform(-.4,.4));cx=float(rng.uniform(275,365));cy=float(rng.uniform(470,620));noise=(0,5,12)[i//18];blur=1 if i%9==8 else 0
 im=render(fov,angle,cx,cy,noise,blur);r,o=call(im);r.update(kind='positive',fov=fov,angle=angle,cx=cx,cy=cy,noise=noise,blur=blur);check_truth(r,o,fov,angle,cx,cy);save(r,im)
# Independent negatives / conservative handling probes.
good=render(6,0,320.317,550.681)
for label,cfg in [('wrong_section',(710,1000,11,3)),('excluded_x',(100,1000,10,2)),('excluded_y',(710,100,10,2)),('invalid_bounds',(5,1000,10,2))]:
 r,o=call(good,cfg);r.update(kind=label);assert r['status']!=0;save(r,good)
for label,im in [('black',np.zeros((200,200),np.uint8)),('white',np.full((200,200),255,np.uint8)),('checker',((np.indices((200,200)).sum(axis=0)%2)*255).astype(np.uint8)),('noise',rng.integers(0,256,(200,200),dtype=np.uint8))]:
 r,o=call(im);r['kind']=label;assert r['status']!=0;save(r,im)
for depth in (4,8,11,12,13,20,50):
 im=good.copy();im[93:96,52:52+depth]=0;r,o=call(im);r.update(kind='edge_ink',depth=depth);check_truth(r,o,6,0,320.317,550.681);save(r,im)
for label,box in [('central_ink',(95,95,106,106)),('boundary_256plus',(52,80,70,99)),('diagonal',None)]:
 im=good.copy()
 if box:x0,y0,x1,y1=box;im[y0:y1,x0:x1]=0
 else:
  for k in range(52,148):im[k,k:k+3]=0
 r,o=call(im);r['kind']=label;assert r['status']!=0;save(r,im)
summary={'n':len(records),'old_api':len(reg),'positive_status':dict(Counter(r['status'] for r in records if r['kind']=='positive')),'negative_status':dict(Counter(r['status'] for r in records if r['kind']!='positive')),'max_accepted_grid_error_px':max(r.get('max_grid_error_px',0) for r in records),'workspace_bytes':lib.ws_size()};(P/'summary.json').write_text(json.dumps(summary,indent=2));print(summary)
