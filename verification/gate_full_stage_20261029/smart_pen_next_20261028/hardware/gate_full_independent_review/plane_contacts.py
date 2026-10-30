from pathlib import Path
import json
D=Path(__file__).resolve().parent;s=(D/'audit.py').read_text();exec(compile(s[:s.index('na,nb=build')],__file__,'exec'))
out={}
for key,board in [('before',old),('after',b)]:
 nets=build(board);out[key]={}
 for net,anchor in [('3V3_AON','C104.1'),('GND','C104.2')]:
  ns=nets[net];marked=[(name,ispad or '/' in name,ss) for name,ispad,ss in ns];cc=components(marked);core=next(c for c in cc if anchor in c);zones=[n for n,_,_ in ns if '/' in n];out[key][net]={'zone_islands':len(zones),'in_core':[n for n in zones if n in core],'outside_core':[n for n in zones if n not in core]}
print(json.dumps(out,indent=2))
