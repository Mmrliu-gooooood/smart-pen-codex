from pathlib import Path
import sys,subprocess,json,os
HERE=Path(__file__).resolve().parent
DEFAULT=HERE.parent/'smart_pen_app_pipeline_20261028'
SRC=Path(os.environ.get('PEN_REVIEW_SOURCE',str(DEFAULT))).resolve()
OUT=Path(os.environ.get('PEN_REVIEW_OUTPUT',str(HERE/'run_output'))).resolve();OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(SRC/'tests'))
from roi_opt_fixture import Render,render,vectors
v=vectors()[0]
(OUT/'frame.gray').write_bytes(render(v['directions'],Render(pitch=20,angle=0,scale_y=1)))
s=(SRC/'tests/test_application_pipeline.c').read_text()
s=s.replace('pen_link_security security={1,1,1,1,5},bad={1,1,0,1,5};','pen_link_security security={1,1,1,1,5},bad={1,1,0,1,5};\n pen_store before_peek=store; pen_sample peek; CHECK(pen_store_offer(&store,&peek)==0); CHECK(pen_app_ack(&app,&security,&security,123,0)==-3); store=before_peek;')
s=s.replace('case 10:t->confidence=1;break;default:break;', 'case 10:t->confidence=1;break;case 11:t->y_um=1000001;break;case 12:t->y_um=-1000001;break;case 13:t->x_um=-1000001;break;case 14:t->pose_valid=2;break;default:break;')
s=s.replace('mode<=10','mode<=14')
assert 'pen_store before_peek=' in s and 'case 14:t->pose_valid=2;' in s and 'mode<=14' in s
(OUT/'additional_pipeline.c').write_text(s)
sources=['application/pipeline.c','runtime/recorder.c','runtime/contact_power.c','storage/store.c','portable/pen.c','vision/roi_opt.c','codec/anoto.c']
for name,flags in [('normal',[]),('ndebug',['-DNDEBUG']),('asan',['-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
 cmd=['cc','-std=c11','-O1','-Wall','-Wextra','-Werror','-pedantic']+flags
 cmd+=['-I'+str(SRC/'firmware'/p) for p in ['application','runtime','storage','portable','vision']]
 cmd += [str(SRC/'firmware'/p) for p in sources]+[str(OUT/'additional_pipeline.c'),'-lm','-o',str(OUT/('pipeline_'+name))]
 subprocess.run(cmd,check=True)
 env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:abort_on_error=1')
 subprocess.run([str(OUT/('pipeline_'+name)),str(OUT/'frame.gray'),*map(str,v['section']),*map(str,v['xy'])],check=True,env=env)
 print(name,'PASS')
