"""Artificial parser unit tests; NOT device measurements."""
import json,unittest
from pathlib import Path
from summarize_serial import summarize
class Parser(unittest.TestCase):
 def rows(self,repeats=3):
  rows=[dict(type='header',schema=1),dict(type='runtime_config',repeats=repeats)]
  for f in json.loads((Path(__file__).resolve().parents[1]/'fixtures/manifest.json').read_text()):
   for r in range(repeats):
    for mode in (['cold','warm'] if f['expected_status']==0 else ['cold']):
     rows.append(dict(type='decode',placement='internal',fixture=f['file'],repeat=r,mode=mode,verdict='correct_coordinate' if f['expected_status']==0 else 'expected_nofit',status=f['expected_status'],x=f['expected_x'],y=f['expected_y'],used_warm=int(mode=='warm'),decode_us=123,failure_output_preserved=True,failure_prior_cleared=True))
  rows.extend([dict(type='skip',placement='psram',reason='not_opted_in'),dict(type='complete')]);return rows
 def parse(self,rows): return summarize(map(json.dumps,rows))
 def test_complete(self):
  for n in [1,2,3,10]: self.assertFalse(self.parse(self.rows(n))['functional_failures'])
 def test_missing_complete(self):
  with self.assertRaises(ValueError): self.parse(self.rows()[:-1])
 def test_missing_sample(self):
  rows=self.rows();del rows[2]
  with self.assertRaises(ValueError): self.parse(rows)
 def test_duplicate(self):
  rows=self.rows();rows.insert(2,rows[2])
  with self.assertRaises(ValueError): self.parse(rows)
 def test_bad_fields(self):
  for key,val in [('verdict','correct_coordinate'),('status',0),('fixture','bogus'),('mode','bogus'),('placement','bogus'),('repeat',99),('decode_us',-1),('decode_us',float('nan')),('decode_us',float('inf')),('decode_us',True),('decode_us',1.5)]:
   with self.subTest(key=key,val=val):
    rows=self.rows();rows[2][key]=val
    with self.assertRaises(ValueError): self.parse(rows)
 def test_wrong_coordinate(self):
  rows=self.rows();row=next(r for r in rows if r.get('status')==0);row['x']+=1
  with self.assertRaises(ValueError): self.parse(rows)
 def test_warm_before_cold(self):
  rows=self.rows();i=next(i for i,r in enumerate(rows) if r.get('mode')=='warm');rows[i-1],rows[i]=rows[i],rows[i-1]
  with self.assertRaises(ValueError): self.parse(rows)
 def test_internal_missing(self):
  rows=self.rows()
  for r in rows:
   if r.get('type')=='decode': r['placement']='psram'
  with self.assertRaises(ValueError): self.parse(rows)
 def test_skip_missing(self):
  rows=self.rows();del rows[-2]
  with self.assertRaises(ValueError): self.parse(rows)
 def test_header_out_of_order(self):
  rows=self.rows();rows[0],rows[2]=rows[2],rows[0]
  with self.assertRaises(ValueError): self.parse(rows)
 def test_known_failure(self):
  rows=self.rows();rows[2]['failure_output_preserved']=False;self.assertEqual(len(self.parse(rows)['functional_failures']),1)
if __name__=='__main__': unittest.main()
