"""Strict schema3 serial analysis, never authenticated device acceptance."""
from pathlib import Path
import hashlib,json,statistics,collections,sys
from oracle import integer,finite,validate
ROOT=Path(__file__).resolve().parents[1]

def summarize(lines):
 records=[]
 for line in lines:
  line=line.strip()
  if line.startswith('{'): records.append(json.loads(line,parse_constant=lambda s: (_ for _ in ()).throw(ValueError('Nonfinite JSON'))))
 def pop(kind):
  if not records or records[0].get('type')!=kind: raise ValueError('Unexpected/missing record; expected '+kind)
  return records.pop(0)
 raw=(ROOT/'fixtures/manifest.json').read_bytes();fixtures=json.loads(raw)['fixtures'];source=json.loads((ROOT/'verification/build-inputs.json').read_text())
 header=pop('header')
 if header.get('schema')!=3 or header.get('manifest_sha256')!=hashlib.sha256(raw).hexdigest() or header.get('source_bundle_sha256')!=source['source_bundle_sha256'] or header.get('synthetic_only') is not True: raise ValueError('Schema/source/fixture header mismatch')
 if header.get('timing_scope')!='full_decode_call_including_preprocessing_coarse_refit_and_trace' or header.get('cold_means')!='no_prior_not_flushed_cpu_cache' or header.get('hardware_providers') is not False: raise ValueError('Incorrect timing/cold/hardware scope')
 if header.get('instrumented') is not True or header.get('instrumentation_scope')!='continuous_v3_only_link_wrap':raise ValueError('Incorrect instrumentation scope')
 cfg=pop('runtime_config');repeats=integer(cfg['repeats'],1,10)
 for key,value in [('workspace_bytes',32640),('pixel_bytes',40000),('configured_cpu_mhz',240),('configured_main_stack_bytes',16384)]:
  if integer(cfg[key])!=value: raise ValueError('Unexpected benchmark configuration')
 if cfg.get('nano_format') is not False or cfg.get('configured_target')!='esp32s3' or not str(cfg.get('idf_version','')).startswith('v5.4'): raise ValueError('Unexpected libc/target/SDK config')
 probe=pop('format_probe')
 if integer(probe['int64'])!=4294967297 or abs(finite(probe['double'])-1.23456789012345)>1e-14: raise ValueError('Target libc format probe failed')
 memories=[]
 def memory(stage):
  r=pop('memory')
  if r.get('stage')!=stage or r.get('placement')!='internal': raise ValueError('Memory record order/placement')
  for key in ['internal_free_bytes','internal_min_free_bytes','internal_largest_bytes','stack_min_free_bytes']: integer(r[key],0,2**32-1)
  if r['internal_largest_bytes']>r['internal_free_bytes'] or r['stack_min_free_bytes']>16384: raise ValueError('Inconsistent memory metrics')
  memories.append(r)
 memory('before_alloc');memory('allocated');groups=collections.defaultdict(list);failures=[]
 for f in fixtures:
  for repeat in range(repeats):
   for decoder in ['frozen_opt','continuous_v3']:
    r=pop('decode')
    if (r.get('fixture'),r.get('placement'),integer(r['repeat'],0,repeats-1),r.get('decoder'),r.get('mode'))!=(f['file'],'internal',repeat,decoder,'cold'): raise ValueError('Extra/missing/out-of-order/unknown decode sample')
    elapsed=integer(r['decode_us']);verdict,errors=validate(r,f)
    if errors: failures.append(dict(fixture=f['file'],decoder=decoder,repeat=repeat,errors=errors))
    groups[(f['file'],decoder,verdict)].append(elapsed);memory('after_decode')
 memory('after_free');skip=pop('skip')
 if skip.get('placement')!='psram' or skip.get('reason')!='pure_ram_profile': raise ValueError('Missing explicit PSRAM skip')
 pop('complete')
 if records: raise ValueError('Extra JSON after complete')
 return dict(scope='Unattested user-supplied serial; cold decode-only, not camera FPS',identity_verified=False,overall_pass=None,identity_note='Header binds expected source/fixture but is not physical board identity or log authentication.',functional_failures=failures,groups=[dict(fixture=k[0],decoder=k[1],verdict=k[2],n=len(v),min_us=min(v),median_us=statistics.median(v),max_us=max(v)) for k,v in sorted(groups.items())],memory_records=memories,psram='not_tested')
if __name__=='__main__':
 if len(sys.argv)!=2: raise SystemExit('usage: python tools/summarize_serial.py PRIVATE_SERIAL_LOG')
 result=summarize(Path(sys.argv[1]).read_text().splitlines());print(json.dumps(result,indent=2));raise SystemExit(1 if result['functional_failures'] else 2)
