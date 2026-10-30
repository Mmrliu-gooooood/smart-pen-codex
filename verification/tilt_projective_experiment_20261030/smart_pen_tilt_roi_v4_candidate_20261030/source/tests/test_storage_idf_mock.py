import pathlib,subprocess,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class StorageIdfTests(unittest.TestCase):
 def test_actual_adapter_disabled_and_enabled(self):
  for enabled in (False,True):
   with self.subTest(enabled=enabled),tempfile.TemporaryDirectory() as t:
    d=pathlib.Path(t);(d/'sdkconfig.h').write_text('#define CONFIG_PEN_FLASH_RECORDING 1\n' if enabled else '')
    command=['cc','-std=c11','-Wall','-Wextra','-Werror','-Wno-unused-function','-pedantic','-I'+str(d)]
    command+=['-I'+str(ROOT/p) for p in ('tests/test_storage_stubs','firmware/storage','firmware/portable')]
    command += [str(ROOT/p) for p in ('firmware/storage/storage_idf.c','firmware/storage/store.c','firmware/portable/pen.c','tests/test_storage_idf_mock.c')]
    command+=['-o',str(d/'mock')];subprocess.run(command,check=True);subprocess.run([str(d/'mock')],check=True)
if __name__=='__main__':unittest.main()
