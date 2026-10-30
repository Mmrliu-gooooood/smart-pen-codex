"""Compare actual target-candidate C outputs against generator geometry, not fitted matrices."""
from pathlib import Path
import os,sys,json,hashlib,tempfile
HERE=Path(__file__).resolve().parent
ROOT=Path(os.environ.get('PEN_BENCH_SOURCE',str(HERE.parent/'smart_pen_continuous_target_benchmark_20261029'))).resolve()
ORACLES=Path(os.environ.get('PEN_GEOMETRY_ORACLE',str(HERE/'generator_oracles.json')))
sys.path.insert(0,str(ROOT/'tools'))
from host_api import C,Config,Frame,build
oracles=json.loads(ORACLES.read_text())['fixtures'];results=[]
with tempfile.TemporaryDirectory() as tmp:
 lib=build(tmp);ws=(C.c_double*((lib.ws_size()+7)//8))();cfg=Config(710,1000,10,2)
 for fov in (5,6,7):
  name=f'fov{fov}_roi200_phase0.pgm';raw=(ROOT/'fixtures'/name).read_bytes().split(b'\n255\n',1)[1]
  o=next(r for r in oracles if r['fov_mm']==fov and r['phase']==0)
  assert hashlib.sha256(raw).hexdigest()==o['image_sha256']
  pixels=(C.c_uint8*len(raw)).from_buffer_copy(raw);out=Frame();rc=lib.pen_roi_decode_continuous(pixels,len(raw),200,200,200,C.byref(cfg),ws,C.byref(out));assert rc==0
  x,y=out.roi.decoded.x,out.roi.decoded.y;a=out.paper_to_frame;b=out.frame_to_paper;p=60/fov
  errors=[]
  for k in range(36):
   xx=x+k%6;yy=y+k//6
   expected=o['directions'][yy-o['cell_top']][xx-o['cell_left']];assert out.roi.decoded.directions[k]==expected
   u=a[0]*xx+a[1]*yy+a[2];v=a[3]*xx+a[4]*yy+a[5]
   error=max(abs(u-(p*(xx-o['ox_cells'])-.5)),abs(v-(p*(yy-o['oy_cells'])-.5)));assert error<=.1*p
   errors.append(error)
   assert max(abs(b[0]*u+b[1]*v+b[2]-xx),abs(b[3]*u+b[4]*v+b[5]-yy))<1e-7
  results.append({'fixture':name,'points_checked':36,'max_frame_error_pixels':max(errors),'tolerance_pixels':.1*p,'synthetic_only':True})
print(json.dumps({'oracle_file_sha256':hashlib.sha256(ORACLES.read_bytes()).hexdigest(),'points':108,'results':results,'not_physical_accuracy':True},indent=2))
