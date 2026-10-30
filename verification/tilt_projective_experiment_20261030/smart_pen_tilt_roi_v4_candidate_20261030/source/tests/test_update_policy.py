"""Host C policy tests; not a claim about physical rollback or signatures."""
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
class UpdatePolicyTests(unittest.TestCase):
 def test_portable_policy(self):
  with tempfile.TemporaryDirectory() as t:
   exe=Path(t)/'update-test'
   subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-pedantic','-I'+str(ROOT/'firmware/update'),str(ROOT/'firmware/update/update_policy.c'),str(ROOT/'tests/test_update_policy.c'),'-o',str(exe)],check=True)
   subprocess.run([str(exe)],check=True)
