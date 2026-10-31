from pathlib import Path
import subprocess,tempfile,os
r=Path(__file__).resolve().parent;p=r.parent;c=p/'capture_actor_adapter_20261031_0600';repo=p/'recovery_20261031';cap=repo/'verification/accepted_successors_stage_20261029/smart_pen_camera_capture_v2_candidate_20261029'
for mode in ['normal','ndebug','sanitizers']:
 with tempfile.TemporaryDirectory() as t:
  cmd=['gcc','-std=c11','-Wall','-Wextra','-Werror','-pedantic','-O1','-g','-DPEN_ADAPTER_HOST_TEST=1']
  if mode=='ndebug':cmd+=['-DNDEBUG']
  if mode=='sanitizers':cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
  cmd+=['-I'+str(i) for i in [c/'include',cap/'include']+[repo/'firmware'/x for x in ['application','runtime','vision','storage','codec','portable']]]
  cmd+=[str(r/'test_independent.c'),str(c/'src/adapter.c')]+[str(cap/'src'/x) for x in ['pen_capture.c','pen_capture_app.c','pen_capture_profiles.c']]+['-o',t+'/test']
  print('RUN independent',mode,flush=True);subprocess.run(cmd,check=True);subprocess.run([t+'/test'],check=True,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0'})
