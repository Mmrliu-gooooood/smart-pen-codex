import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'software'))
from page_registry import Page, Registry
class RegistryTests(unittest.TestCase):
 def test_unique_and_unknown(self):
  p=Page(1,0,0,710,1000,300);r=Registry([p]);self.assertEqual(r.resolve(0,0),p)
  for s in [(1,1),(63,0),(-1,0),(True,0)]:
   with self.assertRaises(ValueError):r.resolve(*s)
 def test_duplicate_alias_invalid(self):
  p=Page(1,0,0,710,1000,300)
  for q in [Page(2,0,0,710,1000,300),Page(1,1,0,710,1000,300),Page(2,63,0,710,1000,300),Page(2,1,0,710,1000,float('nan')),Page(2,1,0,710,1000,True),Page(2,1,0,710,1000,'300')]:
   with self.assertRaises(ValueError):Registry([p,q])
 def test_capacity(self):
  pages=[Page(u*63+v+1,u,v,710,1000,300) for u in range(63) for v in range(63)]
  r=Registry(pages);self.assertEqual(len(r.by_section),3969)
if __name__=='__main__':unittest.main()
