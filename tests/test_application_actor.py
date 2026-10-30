"""Compile the actual app_main actor with narrow IDF/board/storage test doubles."""
import os,pathlib,subprocess,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class ApplicationActor(unittest.TestCase):
 def test_actual_actor_fatal_paths_and_disabled_startup(self):
  with tempfile.TemporaryDirectory() as tmp:
   for disabled in (False,True):
    cmd=['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-pedantic']
    if disabled: cmd+=['-DTEST_APP_DISABLED=1']
    if os.environ.get('PEN_APP_TEST_NDEBUG')=='1': cmd+=['-DNDEBUG']
    if os.environ.get('PEN_APP_TEST_SANITIZERS')=='1': cmd+=['-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer']
    cmd+=['-I'+str(ROOT/'tests/test_application_stubs')]
    cmd+=['-I'+str(ROOT/'firmware'/d) for d in ('application_idf/main','application','runtime','storage','portable','vision')]
    sources=['application_idf/main/application_main.c','application/pipeline.c','runtime/recorder.c','runtime/contact_power.c','storage/store.c','portable/pen.c','vision/roi_opt.c','codec/anoto.c']
    exe=pathlib.Path(tmp)/('disabled' if disabled else 'enabled')
    cmd+=[str(ROOT/'firmware'/p) for p in sources]+[str(ROOT/'tests/test_application_actor.c'),'-lm','-o',str(exe)]
    subprocess.run(cmd,check=True);subprocess.run([str(exe)],check=True)
if __name__=='__main__':unittest.main()
