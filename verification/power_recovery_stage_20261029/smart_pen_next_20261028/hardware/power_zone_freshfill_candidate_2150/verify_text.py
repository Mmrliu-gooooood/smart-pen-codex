from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;R=D.parents[1]
def norm(f):
 lines=f.read_text().splitlines(keepends=True);out=[];i=0
 while i<len(lines):
  if lines[i].startswith('\t\t(filled_polygon'):
   i+=1
   while lines[i]!='\t\t)\n':i+=1
  else:out.append(lines[i].replace('(fill yes\n','(fill\n'))
  i+=1
 return ''.join(out)
a=D/'native/mainboard_revD.kicad_pcb';b=R/'hardware/head_power_joint_native_candidate_2141/native/mainboard_revD.kicad_pcb'
if norm(a)!=norm(b):raise RuntimeError('non-fill native text changed')
print(json.dumps(dict(all_native_text_except_fill_flag_and_filled_polygons_exactly_unchanged=True,base_sha=hashlib.sha256(b.read_bytes()).hexdigest(),candidate_sha=hashlib.sha256(a.read_bytes()).hexdigest()),indent=2))
