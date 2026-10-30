import pathlib,subprocess,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class StorageTests(unittest.TestCase):
 def test_actual_c_fault_injection(self):
  with tempfile.TemporaryDirectory() as t:
   binary=pathlib.Path(t)/'storage'
   subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-pedantic','-I'+str(ROOT/'firmware/portable'),'-I'+str(ROOT/'firmware/storage'),str(ROOT/'firmware/portable/pen.c'),str(ROOT/'firmware/storage/store.c'),str(ROOT/'tests/test_storage.c'),'-o',str(binary)],check=True)
   subprocess.run([str(binary)],check=True)
if __name__=='__main__':unittest.main()
