import csv,json
from pathlib import Path
from collections import Counter
from model import screen
O=Path(__file__).resolve().parent
rows=[];counts={}
for crop in [256,96,80]:
 count=Counter()
 for r in csv.DictReader((O/'sweep.csv').open()):
  args={k:float(r[k]) for k in ['pitch_mm','dot_ratio','offset_ratio','distance_mm','focal_px','tilt_deg']}
  try:s=screen(**args,roi_px=crop);count[s['status']]+=1
  except ValueError:count['INVALID_DEPTH']+=1
 counts[crop]=dict(count)
(O/'crop_comparison.json').write_text(json.dumps({'warning':'96/80 are archivedV3 crop envelopes, not running V3 or its conditional crop selection; cold constraints same orthogonal family. 80 only selected at >100 components in V3.','counts':counts},indent=2)+'\n')
print(json.dumps(counts,indent=2))
