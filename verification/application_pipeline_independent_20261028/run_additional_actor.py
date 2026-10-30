from pathlib import Path
import subprocess,os,re
HERE=Path(__file__).resolve().parent
DEFAULT=HERE.parent/'smart_pen_app_pipeline_20261028'
SRC=Path(os.environ.get('PEN_REVIEW_SOURCE',str(DEFAULT))).resolve()
OUT=Path(os.environ.get('PEN_REVIEW_OUTPUT',str(HERE/'run_output'))).resolve();OUT.mkdir(parents=True,exist_ok=True)
s=(SRC/'tests/test_application_actor.c').read_text()
s=s.replace('static int scenario,', 'static int review_mode;static int scenario,')
s=s.replace('opened++;CHECK(enabled==1', 'opened++;if(review_mode==102)return -1;CHECK(enabled==1')
s=s.replace('begin_count++;*epoch=', 'begin_count++;if(review_mode==103)return -1;*epoch=')
s=s.replace('(void)c;polls++;CHECK(polls<=36);', '(void)c;polls++;if(review_mode==100)return -1;CHECK(polls<=36);')
s=s.replace('CHECK(a&PEN_CP_WAKE_CAMERA);return 0;', 'CHECK(a&PEN_CP_WAKE_CAMERA);return review_mode==101?-1:0;')
s=s.replace('(void)c;quiesces++;', '(void)c;quiesces++;if(review_mode==104){clock_us+=1000;return 0;}')
s=s.replace('static int maintenance_guard(void*c){(void)c;', 'static int maintenance_guard(void*c){(void)c;if(review_mode==105){clock_us+=1000;return 1;}')
s=s.replace('static int erase_log(void*c){(void)c;erase_count++;', 'static int erase_log(void*c){(void)c;erase_count++;if(review_mode==106)clock_us+=1000;')
m=re.search(r'for\(volatile int mode=0;mode<(\d+);mode\+\+\)\{',s)
assert m
old=int(m[1]);assert old<=100
s=s[:m.start()]+f'for(volatile int mode=0;mode<107;mode++){{ if(mode>={old}&&mode<100)continue;'+s[m.end():]
s=s.replace('reset_case(mode);if(!setjmp(stopped))app_main();', 'review_mode=mode;reset_case((mode==105||mode==106)?13:mode>=100?5:mode);if(!setjmp(stopped))app_main();\n  if(mode>=100){CHECK(opened==1&&closed==(mode==102?0:1)&&stops==1&&!sends&&!sleeps); if(mode==106)CHECK(polls==1&&erase_count==1&&!begin_count&&!resumes);else if(mode==105)CHECK(polls==1&&quiesces==1&&!erase_count);else if(mode==104)CHECK(polls==3&&quiesces==1);else if(mode>=102)CHECK(polls==0);else CHECK(polls==1);continue;}')
for expected in ('if(review_mode==102)return -1;', 'if(review_mode==103)return -1;', 'if(review_mode==100)return -1;', 'review_mode==101?-1:0;', 'if(review_mode==104){clock_us+=1000;return 0;}', 'if(review_mode==105){clock_us+=1000;return 1;}'):
 assert expected in s,expected
(OUT/'additional_actor.c').write_text(s)
for variant,extra in [('normal',[]),('ndebug',['-DNDEBUG']),('asan',['-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
 for disabled in (False,True):
  cmd=['cc','-std=c11','-O1','-Wall','-Wextra','-Werror','-pedantic']+extra
  if disabled:cmd+=['-DTEST_APP_DISABLED=1']
  cmd+=['-I'+str(SRC/'tests/test_application_stubs')]
  cmd+=['-I'+str(SRC/'firmware'/d) for d in ('application_idf/main','application','runtime','storage','portable','vision')]
  sources=['application_idf/main/application_main.c','application/pipeline.c','runtime/recorder.c','runtime/contact_power.c','storage/store.c','portable/pen.c','vision/roi_opt.c','codec/anoto.c']
  exe=OUT/('actor_'+variant+('_disabled' if disabled else '_enabled'))
  cmd+=[str(SRC/'firmware'/p) for p in sources]+[str(OUT/'additional_actor.c'),'-lm','-o',str(exe)]
  subprocess.run(cmd,check=True);subprocess.run([str(exe)],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:abort_on_error=1'))
 print(variant,'PASS')
