import pathlib,subprocess,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class RecorderTests(unittest.TestCase):
 def test_integrated_actual_c_modules(self):
  with tempfile.TemporaryDirectory() as t:
   command=['cc','-std=c11','-Wall','-Wextra','-Werror','-pedantic']
   command+=['-I'+str(ROOT/'firmware'/p) for p in ('portable','storage','runtime')]
   command+=[str(ROOT/p) for p in ('firmware/portable/pen.c','firmware/storage/store.c','firmware/runtime/contact_power.c','firmware/runtime/recorder.c','tests/test_recorder.c')]
   command+=['-o',str(pathlib.Path(t)/'test')];subprocess.run(command,check=True);subprocess.run([str(pathlib.Path(t)/'test')],check=True)
if __name__=='__main__':unittest.main()
