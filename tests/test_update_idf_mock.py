from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
class UpdateAdapterTests(unittest.TestCase):
 def test_sdk_fault_call_order(self):
  with tempfile.TemporaryDirectory() as t:
   exe=Path(t)/'update-idf-test'
   subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-pedantic','-I'+str(ROOT/'tests/test_update_stubs'),'-I'+str(ROOT/'firmware/update'),str(ROOT/'firmware/update/update_policy.c'),str(ROOT/'firmware/update/update_idf.c'),str(ROOT/'tests/test_update_idf_mock.c'),'-o',str(exe)],check=True)
   subprocess.run([str(exe)],check=True)

 def test_configuration_never_silently_downgrades_security(self):
  for flag in ['CONFIG_PEN_OTA_ALLOW_INSTALL=0','CONFIG_SECURE_SIGNED_ON_UPDATE=0','CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE=0','CONFIG_BOOTLOADER_APP_ANTI_ROLLBACK=1','CONFIG_PEN_OTA_HARDWARE="other-profile"']:
   with self.subTest(flag=flag),tempfile.TemporaryDirectory() as t:
    exe=Path(t)/'disabled'
    subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-pedantic','-D'+flag,'-I'+str(ROOT/'tests/test_update_stubs'),'-I'+str(ROOT/'firmware/update'),str(ROOT/'firmware/update/update_policy.c'),str(ROOT/'firmware/update/update_idf.c'),str(ROOT/'tests/test_update_disabled.c'),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
