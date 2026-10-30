"""Invented parser unit data only; NEVER target-performance evidence."""
import json,hashlib,unittest,copy
from summarize_serial import ROOT,summarize
class Parser(unittest.TestCase):
 def rows(self,repeats=3):
  raw=(ROOT/'fixtures/manifest.json').read_bytes();fixtures=json.loads(raw)['fixtures'];source=json.loads((ROOT/'verification/build-inputs.json').read_text())
  rows=[dict(type='header',schema=2,manifest_sha256=hashlib.sha256(raw).hexdigest(),source_bundle_sha256=source['source_bundle_sha256'],synthetic_only=True,timing_scope='full_decode_call_including_wrapper_preprocessing',cold_means='no_prior_not_flushed_cpu_cache',hardware_providers=False),dict(type='runtime_config',repeats=repeats,workspace_bytes=31104,pixel_bytes=40000,configured_cpu_mhz=240,configured_main_stack_bytes=16384,nano_format=False,configured_target='esp32s3',idf_version='v5.4'),dict(type='format_probe',int64=4294967297,double=1.23456789012345)]
  def mem(stage): return dict(type='memory',stage=stage,placement='internal',internal_free_bytes=100000,internal_min_free_bytes=90000,internal_largest_bytes=80000,stack_min_free_bytes=8000)
  rows.extend([mem('before_alloc'),mem('allocated')])
  for f in fixtures:
   for repeat in range(repeats):
    for decoder in ['frozen_opt','continuous_v2']:
     status=f['legacy_expected_status'] if decoder=='frozen_opt' else f['expected_status']
     r=dict(type='decode',fixture=f['file'],placement='internal',repeat=repeat,decoder=decoder,mode='cold',status=status,decode_us=123,failure_output_preserved=True)
     if not status:
      for key in ['x','y','directions','crop','dots','windows','edge_components','edge_pixels','paper_to_frame','frame_to_paper']:r[key]=copy.deepcopy(f[key])
      r.update(crop_attempts=f['attempts'],used_warm=0,candidates=26901)
     rows.extend([r,mem('after_decode')])
  rows.extend([mem('after_free'),dict(type='skip',placement='psram',reason='pure_ram_profile'),dict(type='complete')]);return rows
 def parse(self,rows): return summarize(map(json.dumps,rows))
 def success(self,rows):return next(r for r in rows if r.get('type')=='decode' and r['status']==0)
 def test_complete(self):
  for n in [1,2,3,10]:
   r=self.parse(self.rows(n));self.assertFalse(r['functional_failures']);self.assertFalse(r['identity_verified']);self.assertIsNone(r['overall_pass'])
 def test_bad_latency(self):
  for value in [-1,True,1.5,float('nan'),float('inf')]:
   rows=self.rows();rows[5]['decode_us']=value
   with self.assertRaises(ValueError):self.parse(rows)
 def test_bad_identity(self):
  for key in ['manifest_sha256','source_bundle_sha256']:
   rows=self.rows();rows[0][key]='bad'
   with self.assertRaises(ValueError):self.parse(rows)
 def test_scope(self):
  for key,value in [('timing_scope','core_only'),('cold_means','flushed_cache'),('hardware_providers',True)]:
   rows=self.rows();rows[0][key]=value
   with self.assertRaises(ValueError):self.parse(rows)
 def test_unknown_sample(self):
  for key,value in [('fixture','bad'),('placement','psram'),('decoder','bad'),('mode','warm'),('repeat',4)]:
   rows=self.rows();rows[5][key]=value
   with self.assertRaises(ValueError):self.parse(rows)
 def test_missing_extra_reorder(self):
  for action in ['missing','extra','reorder','no_complete','no_probe']:
   rows=self.rows()
   if action=='missing':del rows[5]
   if action=='extra':rows.insert(5,rows[5])
   if action=='reorder':rows[5],rows[7]=rows[7],rows[5]
   if action=='no_complete':rows.pop()
   if action=='no_probe':del rows[2]
   with self.assertRaises(ValueError):self.parse(rows)
 def test_bad_format_probe(self):
  for key,value in [('int64',1),('double',1.2)]:
   rows=self.rows();rows[2][key]=value
   with self.assertRaises(ValueError):self.parse(rows)
 def test_geometry_mismatch(self):
  for key in ['x','crop','directions','paper_to_frame','frame_to_paper','crop_attempts','edge_components']:
   rows=self.rows();r=self.success(rows)
   if type(r[key]) is list:r[key][0]+=1
   else:r[key]+=1
   self.assertTrue(self.parse(rows)['functional_failures'],key)
 def test_nonfinite_transform(self):
  rows=self.rows();self.success(rows)['paper_to_frame'][0]=float('nan')
  with self.assertRaises(ValueError):self.parse(rows)
 def test_bad_status(self):
  rows=self.rows();rows[5]['status']=-3;self.assertTrue(self.parse(rows)['functional_failures'])
 def test_failure_contract(self):
  rows=self.rows();rows[5]['failure_output_preserved']=False;self.assertTrue(self.parse(rows)['functional_failures'])
 def test_stale_geometry_on_reject(self):
  rows=self.rows();rows[5]['x']=10
  with self.assertRaises(ValueError):self.parse(rows)
 def test_memory_missing(self):
  rows=self.rows();del rows[6]
  with self.assertRaises(ValueError):self.parse(rows)
if __name__=='__main__':unittest.main()
