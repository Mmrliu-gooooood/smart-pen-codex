from pathlib import Path
import re,json,hashlib
D=Path(__file__).resolve().parent;R=D.parents[1];paths=[R/'hardware/gnd_conservative_recovery_2305/native/mainboard_revD.kicad_pcb',D/'native/mainboard_revD.kicad_pcb']
def strip(s):
 ranges=[]
 for m in re.finditer(r'(?m)^(?:\t\((?:segment|via|arc)\n|\t\t\(filled_polygon\n)',s):
  start=m.start();i=s.index('(',start);depth=0;quote=False;escape=False
  for j in range(i,len(s)):
   c=s[j]
   if quote:
    if escape:escape=False
    elif c=='\\':escape=True
    elif c=='"':quote=False
   elif c=='"':quote=True
   elif c=='(':depth+=1
   elif c==')':
    depth-=1
    if depth==0:ranges.append((start,j+2 if s[j+1:j+2]=='\n'else j+1));break
  else:raise RuntimeError('unbalanced native')
 for a,b in reversed(ranges):s=s[:a]+s[b:]
 return s
x,y=[strip(p.read_text())for p in paths]
if x!=y:
 import difflib
 (D/'REJECTED_noncopper_diff.txt').write_text(''.join(difflib.unified_diff(x.splitlines(True),y.splitlines(True))));raise RuntimeError('non-copper native text changed')
print(json.dumps({'noncopper_and_zone_definitions_exact_after_removing_only_top_copper_and_filled_polygons':True,'stripped_sha256':hashlib.sha256(x.encode()).hexdigest(),'includes':['footprints, pads and source property text','zone boundary/keepout/connection rules','board outline','layer/stackup and net identities','JP301 footprint OPEN state']},indent=2))
