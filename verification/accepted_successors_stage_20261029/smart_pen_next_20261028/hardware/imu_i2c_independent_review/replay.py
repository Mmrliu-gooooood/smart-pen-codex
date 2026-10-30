from pathlib import Path
import argparse,hashlib,json,re,shutil,os
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache';os.environ['XDG_DATA_HOME']='/tmp/rf-independent/data'
import pcbnew as p
D=Path(__file__).resolve().parent;B=D.parent/'imu_irq_layered_candidate';ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args();O=Path(args.output).resolve()
if O.exists():raise RuntimeError('OUTPUT_MUST_NOT_EXIST')
d=json.loads((D/'serialized_delta.json').read_text());base=B/'native/mainboard_revD.kicad_pcb';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
if sha(base)!=d['base_sha']:raise RuntimeError('BASE_HASH_CHANGED')
shutil.copytree(B/'native',O);f=O/'mainboard_revD.kicad_pcb';seen=set()
def replace(m):
 q=m[0];u=re.search(r'\(uuid "([^"\n]+)"\)',q)[1]
 if u in d['removed']:
  if q!=d['removed'][u]:raise RuntimeError('REMOVE_BLOCK_MISMATCH '+u)
  seen.add(u);return ''
 if u in d['modified']:
  if q!=d['modified'][u]['old']:raise RuntimeError('MODIFY_BLOCK_MISMATCH '+u)
  seen.add(u);return d['modified'][u]['new']
 return q
raw=re.sub(r'\n\t\((?:segment|via)\n.*?\n\t\)',replace,f.read_text(),flags=re.S)
if seen!=set(d['removed'])|set(d['modified']):raise RuntimeError('MISSING_DELTA_TARGET')
i=raw.rfind(')');raw=raw[:i]+''.join(d['added'][u]for u in sorted(d['added']))+'\n'+raw[i:];f.write_text(raw);b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
if sha(f)!=d['final_sha']:raise RuntimeError('REPLAY_HASH_MISMATCH '+sha(f))
print(json.dumps({'status':'EXACT_SERIALIZED_REPLAY_AND_FRESH_FILL','pcb_sha256':sha(f),'output':str(f),'removed':len(d['removed']),'added':len(d['added'])},indent=2))
