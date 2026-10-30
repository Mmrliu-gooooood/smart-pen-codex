import importlib.util,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class PartitionProfile8Tests(unittest.TestCase):
 def test_actual_pure_and_idf_guards_normal_ndebug_sanitized(self):
  spec=importlib.util.spec_from_file_location('profile8_verify',ROOT/'tools/validate_flash8_profile.py')
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  self.assertEqual(len(module.run_host()),6)
if __name__=='__main__':unittest.main()
