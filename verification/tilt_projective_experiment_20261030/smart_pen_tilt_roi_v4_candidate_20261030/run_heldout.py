"""Reproducible V4 heldout gate; nonzero exit for any false acceptance."""
import sys
sys.dont_write_bytecode=True
import json,hashlib,time,argparse
from collections import Counter
from pathlib import Path
import numpy as np
from binding import Decoder
from heldout import cases,render,oracle,DIRECTIONS_PATH
P=Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);ap.add_argument('--out',default='heldout_results.json');args=ap.parse_args()
    dirs=np.load(DIRECTIONS_PATH);rows=[]
    with Decoder() as decoder:
        for spec in cases()[:args.limit]:
            im,_=render(spec,dirs);start=time.perf_counter();r=decoder.decode(im);r['host_seconds']=time.perf_counter()-start
            if r['status']==0:
                r.update(oracle(spec,r,dirs))
                if not r['correct']:
                    name=f"false_{spec['id']}.pgm"
                    (P/name).write_bytes(b'P5\n200 200\n255\n'+im.tobytes());r['false_fixture']=name
            r.update(spec);r['image_sha256']=hashlib.sha256(im.tobytes()).hexdigest();rows.append(r)
            payload=dict(synthetic_only=True,workspace_bytes=decoder.workspace_bytes,cases=rows)
            (P/args.out).write_text(json.dumps(payload,indent=2)+'\n')
            print(spec['id'],spec['group'],spec['tilt'],spec.get('kind','positive'),r['status'],r.get('correct'),r['diagnostics'],flush=True)
        groups={}
        for name in sorted(set(r['group'] for r in rows)):
            subset=[r for r in rows if r['group']==name];accepted=[r for r in subset if r['status']==0]
            groups[name]=dict(cases=len(subset),statuses=dict(Counter(r['status'] for r in subset)),accepted=len(accepted),false_accepts=sum(not r['correct'] for r in accepted),max_error_px=max((r['max_grid_error_px'] for r in accepted),default=None))
        payload['summary']=groups;(P/args.out).write_text(json.dumps(payload,indent=2)+'\n');print(json.dumps(groups,indent=2))
    return int(any(r['status']==0 and not r['correct'] for r in rows))
if __name__=='__main__':sys.exit(main())
