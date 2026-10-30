"""Strict oracle validation of user serial; never substitute host timings."""
from pathlib import Path
import json,sys,statistics,collections

def integer(x,low=0,high=None):
 if type(x) is not int or x<low or (high is not None and x>high): raise ValueError('Invalid bounded integer')
 return x

def summarize(lines):
 records=[]
 for line in lines:
  line=line.strip()
  if line.startswith('{'): records.append(json.loads(line,parse_constant=lambda s: (_ for _ in ()).throw(ValueError('Nonfinite JSON'))))
 if any(r.get('type') not in {'header','runtime_config','decode','memory','warm_skip','skip','complete','fatal'} for r in records): raise ValueError('Unknown JSON record type')
 headers=[r for r in records if r.get('type')=='header']; configs=[r for r in records if r.get('type')=='runtime_config']
 if len(headers)!=1 or headers[0].get('schema')!=1: raise ValueError('Need exactly one schema1 benchmark boot')
 if len(configs)!=1: raise ValueError('Need exactly one runtime_config')
 repeats=integer(configs[0]['repeats'],1,10)
 if records[:2]!=[headers[0],configs[0]]: raise ValueError('Header/config must precede all benchmark records')
 if sum(r.get('type')=='complete' for r in records)!=1 or records[-1].get('type')!='complete': raise ValueError('Need complete at end')
 if any(r.get('type')=='fatal' for r in records): raise ValueError('Fatal fixture error')
 manifest={r['file']:r for r in json.loads((Path(__file__).resolve().parents[1]/'fixtures/manifest.json').read_text())}
 groups=collections.defaultdict(list);failures=[];seen=set();placements=set();cold_success=set()
 for r in records:
  if r.get('type')!='decode': continue
  place=r['placement'];name=r['fixture'];mode=r['mode'];repeat=integer(r['repeat'],0,repeats-1)
  if place not in ['internal','psram'] or name not in manifest or mode not in ['cold','warm']: raise ValueError('Unknown sample identity')
  f=manifest[name]; key=(place,name,repeat,mode)
  if key in seen: raise ValueError('Duplicate sample')
  if mode=='warm' and (place,name,repeat) not in cold_success: raise ValueError('Warm lacks preceding successful cold')
  seen.add(key);placements.add(place);elapsed=integer(r['decode_us']);status=r['status']
  if type(status) is not int or status not in range(-5,1): raise ValueError('Invalid status')
  if status==0:
   x=integer(r['x'],0,709);y=integer(r['y'],0,999);used=integer(r['used_warm'],0,1)
   verdict='correct_coordinate' if f['expected_status']==0 and (x,y)==(f['expected_x'],f['expected_y']) else 'unexpected_success'
   warm_ok=used==(mode=='warm')
   if mode=='cold': cold_success.add((place,name,repeat))
  else:
   verdict='expected_nofit' if status==f['expected_status'] else 'unexpected_reject';warm_ok=True
  if verdict!=r['verdict']: raise ValueError('Reported verdict disagrees with independent oracle')
  if verdict not in ['correct_coordinate','expected_nofit'] or not warm_ok or r['failure_output_preserved'] is not True or r['failure_prior_cleared'] is not True: failures.append(r)
  groups[(place,name,mode,verdict)].append(elapsed)
 if not groups or 'internal' not in placements: raise ValueError('Missing mandatory internal-RAM run')
 if 'psram' not in placements and not any(r.get('type')=='skip' and r.get('placement')=='psram' and r.get('reason') in {'not_opted_in','not_initialized_or_absent','allocation_failed'} for r in records): raise ValueError('Missing explicit PSRAM skip')
 expected={(place,f['file'],repeat,phase) for place in placements for f in manifest.values() for repeat in range(repeats) for phase in (['cold','warm'] if f['expected_status']==0 else ['cold'])}
 if seen!=expected: raise ValueError('Missing or extra sample; cannot claim complete benchmark')
 return {'scope':'unattested user-supplied serial; decode-only, not camera FPS','identity_verified':False,'overall_pass':None,'identity_note':'No trusted physical board/build identity in schema1. Functional parsing is not device acceptance or log authentication.','functional_failures':failures,'groups':[dict(placement=k[0],fixture=k[1],mode=k[2],verdict=k[3],n=len(v),min_us=min(v),median_us=statistics.median(v),max_us=max(v)) for k,v in sorted(groups.items())],'memory_records':[r for r in records if r.get('type')=='memory'],'skips':[r for r in records if r.get('type') in ['skip','warm_skip']]}
if __name__=='__main__':
 if len(sys.argv)!=2: raise SystemExit('usage: python tools/summarize_serial.py PRIVATE_SERIAL_LOG')
 result=summarize(Path(sys.argv[1]).read_text().splitlines());print(json.dumps(result,indent=2));raise SystemExit(1 if result['functional_failures'] else 2) # 2 = parsed but device identity unverified, never overall pass
