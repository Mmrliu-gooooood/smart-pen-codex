from pathlib import Path
import subprocess,tempfile,os
r=Path(__file__).resolve().parent
subprocess.run([os.environ.get('PYTHON','python'),str(r/'verify_dependencies.py')],check=True)
repo=r.parent/'recovery_20261031'
cap=repo/'verification/accepted_successors_stage_20261029/smart_pen_camera_capture_v2_candidate_20261029'
incs=[r/'include',cap/'include',repo/'firmware/application_idf/main']+[repo/'firmware'/p for p in ['application','runtime','vision','storage','codec','portable']]
for mode in ['normal','ndebug','sanitizers']:
 for test in ['test_adapter','test_failures','test_pipeline','test_default']:
  with tempfile.TemporaryDirectory(prefix='pen-adapter-host-') as t:
   cmd=['gcc','-std=c11','-Wall','-Wextra','-Werror','-pedantic','-g','-O1']
   if test not in ['test_pipeline']:cmd += ['-Wconversion','-Wshadow']
   if test!='test_default':cmd+=['-DPEN_ADAPTER_HOST_TEST=1']
   if mode=='ndebug':cmd+=['-DNDEBUG','-O2']
   if mode=='sanitizers':cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
   cmd += ['-I'+str(p) for p in incs]
   cmd += [str(r/'src/adapter.c'),str(r/'tests'/f'{test}.c')] + [str(cap/'src'/p) for p in ['pen_capture.c','pen_capture_app.c','pen_capture_profiles.c']]
   if test in ['test_default','test_pipeline']:cmd += [str(repo/'firmware/application_idf/main/board_provider_absent.c')]
   if test=='test_pipeline':cmd += [str(repo/'firmware'/p) for p in ['application/pipeline.c','runtime/recorder.c','runtime/contact_power.c','storage/store.c','portable/pen.c','vision/roi_opt.c','codec/anoto.c']]+['-lm']
   cmd += ['-o',t+'/test']
   print(f'RUN {mode} {test}',flush=True)
   subprocess.run(cmd,check=True)
   subprocess.run([t+'/test'],check=True,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0'})
