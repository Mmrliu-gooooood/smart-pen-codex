"""Host C execution of the actual contact/prewake core; not hardware timing."""
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
class ContactPower(unittest.TestCase):
 def test_c_state_machine(self):
  with tempfile.TemporaryDirectory() as t:
   binary=Path(t)/'contact_power'
   subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-pedantic',
    '-I'+str(ROOT/'firmware/runtime'),'-I'+str(ROOT/'firmware/portable'),
    str(ROOT/'firmware/runtime/contact_power.c'),str(ROOT/'tests/test_contact_power.c'),'-o',str(binary)],check=True)
   subprocess.run([str(binary)],check=True)
if __name__=='__main__':unittest.main()
