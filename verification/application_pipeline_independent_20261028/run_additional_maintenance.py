from pathlib import Path
import os,subprocess
HERE=Path(__file__).resolve().parent
SRC=Path(os.environ.get('PEN_REVIEW_SOURCE',str(HERE.parent/'smart_pen_app_pipeline_20261028'))).resolve()
OUT=Path(os.environ.get('PEN_REVIEW_OUTPUT',str(HERE/'run_output'))).resolve();OUT.mkdir(parents=True,exist_ok=True)
s=(SRC/'tests/test_application_maintenance.c').read_text()
s=s.replace('static uint8_t bytes', 'static int review_sync_fail;static uint8_t bytes')
s=s.replace('static int sync_log(void*c){(void)c;return 0;}', 'static int sync_log(void*c){(void)c;return review_sync_fail?-1:0;}')
s=s.replace('int main(void){', '''int main(void){
 setup(1);bytes[56]=255;CHECK(pen_app_reclaim(&app,1,1,0,1)==-3);CHECK(!erases);
 setup(1);bytes[52]^=1;CHECK(pen_app_reclaim(&app,1,1,0,1)==-3);CHECK(!erases);
 setup(1);bytes[20]^=1;CHECK(pen_app_reclaim(&app,1,1,0,1)==-1);CHECK(!erases&&store.log.faulted);
 setup(1);CHECK(pen_app_reclaim(&app,1,1,-1,1)==-1);CHECK(!erases);
 setup(1);CHECK(pen_app_reclaim(&app,1,1,0,-1)==-1);CHECK(!erases);
 setup(1);CHECK(pen_app_reclaim(&app,2,1,0,1)==1);CHECK(!erases);
 setup(1);CHECK(pen_app_reclaim(&app,1,2,0,1)==1);CHECK(!erases);
 setup(1);store.log.faulted=1;CHECK(pen_app_reclaim(&app,1,1,0,1)==-1);CHECK(!erases);
 setup(1);app.last_contact_faults=1;CHECK(pen_app_reclaim(&app,1,1,0,1)==-1);CHECK(!erases);
 setup(1);store.recording=1;CHECK(pen_app_reclaim(&app,1,1,0,1)==-3);CHECK(!erases);
 setup(1);review_sync_fail=1;CHECK(pen_app_reclaim(&app,1,1,0,1)==-1);CHECK(!erases&&store.log.faulted);review_sync_fail=0;
 setup(0);review_sync_fail=1;CHECK(pen_app_prepare_replay_sleep(&app,1,1,0,1)==-1);CHECK(!erases&&store.log.faulted&&!app.sleep_prepared);review_sync_fail=0;
''')
(OUT/'additional_maintenance.c').write_text(s)
for variant,extra in [('normal',[]),('ndebug',['-DNDEBUG']),('asan',['-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
 cmd=['cc','-std=c11','-O1','-Wall','-Wextra','-Werror','-pedantic']+extra
 cmd+=['-I'+str(SRC/'firmware'/d) for d in ('application','runtime','storage','portable','vision')]
 files=['application/pipeline.c','runtime/recorder.c','runtime/contact_power.c','storage/store.c','portable/pen.c','vision/roi_opt.c','codec/anoto.c']
 exe=OUT/('maintenance_'+variant)
 cmd+=[str(SRC/'firmware'/p) for p in files]+[str(OUT/'additional_maintenance.c'),'-lm','-o',str(exe)]
 subprocess.run(cmd,check=True);subprocess.run([str(exe)],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:abort_on_error=1'))
 print(variant,'PASS')
