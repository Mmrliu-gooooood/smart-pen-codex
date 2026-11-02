from pathlib import Path
import json,sys,hashlib
import os,argparse
os.environ.setdefault('XDG_CONFIG_HOME','/tmp/pen19_aggregate/config');os.environ.setdefault('XDG_CACHE_HOME','/tmp/pen19_aggregate/cache');os.environ.setdefault('XDG_DATA_HOME','/tmp/pen19_aggregate/data')
D=Path(__file__).resolve().parent;R=D.parents[1];parser=argparse.ArgumentParser();parser.add_argument('--baseline',type=Path,default=R/'hardware/mainboard_wip_20261102/candidate/mainboard_revD.kicad_pcb');args=parser.parse_args();A=args.baseline;B=R/'hardware/mainboard_wip19_20261102/candidate/mainboard_revD.kicad_pcb';sys.path.insert(0,str(D/'source/review_dependencies'))
if hashlib.sha256(A.read_bytes()).hexdigest()!='617a991b39a05e53f6bbf55700d2aa84052a3b5140b947c2b66a503f9846d8b5':raise RuntimeError('historical native hash')
if hashlib.sha256(B.read_bytes()).hexdigest()!='f7632bf6296ba212ec59e54edb1dfdb91995f6f4f071a3d9505b6638f3fbf416':raise RuntimeError('current native hash')
import pcbnew
from native_blocks import blocks
from finite_copper import build,components
import re
def copper(p):return{re.search(r'\(uuid "([^"]+)"',v).group(1):v for _,_,v in blocks(p.read_text())if v.startswith(('(segment','(via'))}
def fps(p):return{re.search(r'\(property "Reference" "([^"]+)"',v).group(1):v for _,_,v in blocks(p.read_text())if v.startswith('(footprint')}
a,b=copper(A),copper(B);fa,fb=fps(A),fps(B);na={n:components(v)for n,v in build(pcbnew.LoadBoard(str(A))).items()};nb={n:components(v)for n,v in build(pcbnew.LoadBoard(str(B))).items()};out={'source_sha256':hashlib.sha256(A.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(B.read_bytes()).hexdigest(),'source_copper_count':len(a),'candidate_copper_count':len(b),'removed_ids':sorted(set(a)-set(b)),'added_ids':sorted(set(b)-set(a)),'modified_retained_ids':sorted(k for k in a.keys()&b.keys()if a[k]!=b[k]),'changed_footprints':sorted(k for k in fa if fa[k]!=fb[k]),'footprints_each':[len(fa),len(fb)],'partition_changes':{n:{'old':v,'new':nb[n]}for n,v in na.items()if v!=nb[n]},'scope':'Direct617a→f763 aggregate raw/finite-topology comparison only, not intermediate DRC/refill/assembly replay.'}
expected=json.loads((D/'recorded/cumulative_counts.json').read_text())
if out!=expected:raise RuntimeError('aggregate raw/finite topology mismatch')
print(json.dumps({'status':'PASS','removed':len(out['removed_ids']),'added':len(out['added_ids']),'retained_raw_changed':len(out['modified_retained_ids']),'changed_footprints':out['changed_footprints'],'merged_nets':list(out['partition_changes']),'scope':out['scope']},indent=2))
