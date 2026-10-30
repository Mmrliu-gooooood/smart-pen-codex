"""Independent exact-symbol, support, map and orientation check of original eight."""
import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
from heldout import oracle
P=Path(__file__).resolve().parent

def main():
    base=json.loads((P/'baseline_eight.json').read_text());cand=json.loads((P/'candidate_eight.json').read_text());assert len(base)==len(cand)==8;rows=[]
    for old,r in zip(base,cand):
        name=f"tilt{old['camera_tilt_deg']}_phase{old['phase']}.pgm";assert r['image']==name
        spec=dict(pitch=10.,center=(old['ox']+10,old['oy']+10),tilt=old['camera_tilt_deg'],roll=0,azimuth=0)
        checked=oracle(spec,r) if r['status']==0 else {}
        rows.append(dict(image=name,status=r['status'],**checked));print(rows[-1],flush=True)
    (P/'candidate_eight_oracle.json').write_text(json.dumps(rows,indent=2)+'\n')
    return int(any(r['status']==0 and not r['correct'] for r in rows))
if __name__=='__main__':sys.exit(main())
