from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;A=D.parent/'tail_courtyard_native_0949/native/mainboard_revD.kicad_pcb';B=D/'native/mainboard_revD.kicad_pcb'
def blocks(s):
 depth=0;quote=False;esc=False;start=0
 for i,c in enumerate(s):
  if quote:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':quote=False
  elif c=='"':quote=True
  elif c=='(':
   depth+=1
   if depth==2:start=i
  elif c==')':
   if depth==2:yield s[start:i+1]
   depth-=1
get=lambda f:[s for s in blocks(f.read_text())if s.startswith('(zone')]
x,y=get(A),get(B)
if x!=y:raise RuntimeError('refilled native zone raw blocks changed')
print(json.dumps({'all_native_filled_and_rule_zone_blocks_byte_identical':True,'zone_count':len(x),'zone_block_sha256':[hashlib.sha256(s.encode()).hexdigest()for s in x],'scope':'Together with unchanged old copper/footprints proves old all-net plane projections unchanged; does not erase inherited own-antipad/clock/DFM limits'},indent=2))
