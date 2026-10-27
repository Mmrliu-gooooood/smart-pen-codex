import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('evaluate_measurements',Path(__file__).parents[1]/'tools/evaluate_measurements.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def row(**kw):
    r=dict(condition='static',timestamp_us='1',reference_x_mm='0',reference_y_mm='0',
           x_mm='0.3',y_mm='0.4',valid='1',contact='1',reference_contact='1',latency_ms='30')
    r.update(kw);return r

class TestEvidence(unittest.TestCase):
    def test_empty_not_pass(self): self.assertEqual(m.evaluate([])['status'],'NO_DATA')
    def test_error(self): self.assertEqual(m.evaluate([row()])['conditions']['static']['error_p95_mm'],.5)
    def test_invalid_not_zero(self):
        r=m.evaluate([row(valid='0',x_mm='',y_mm='',latency_ms='')])['conditions']['static']
        self.assertIsNone(r['error_p95_mm']); self.assertEqual(r['missing_ratio'],1)
    def test_no_contact(self): self.assertIsNone(m.evaluate([row(reference_contact='0')])['conditions']['static']['missing_ratio'])
    def test_reject_nan(self):
        with self.assertRaises(ValueError): m.evaluate([row(x_mm='NaN')])
    def test_reject_reverse_time(self):
        with self.assertRaises(ValueError): m.evaluate([row(timestamp_us='2'),row(timestamp_us='1')])
    def test_false_contact(self): self.assertEqual(m.evaluate([row(reference_contact='0')])['conditions']['static']['false_contact_samples'],1)
    def test_invalid_bit(self):
        with self.assertRaises(ValueError): m.evaluate([row(valid='yes')])
if __name__=='__main__': unittest.main()
