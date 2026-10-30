from pathlib import Path
import os,shutil,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/pen-fill2150';os.environ['XDG_CACHE_HOME']='/tmp/pen-fill2150-cache'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];B=R/'hardware/head_power_joint_native_candidate_2141/native';O=R/'hardware/j202_low_speed_reference_candidate/native';N=D/'native';shutil.copytree(B,N,dirs_exist_ok=True)
def zones(f):
 lines=f.read_text().splitlines(keepends=True);out=[];i=0
 while i<len(lines):
  if lines[i]=='\t(zone\n':
   z=[]
   while lines[i]!='\t)\n':
    if lines[i].startswith('\t\t(filled_polygon'):
     i+=1
     while lines[i]!='\t\t)\n':i+=1
    else:z.append(lines[i])
    i+=1
   z.append(lines[i]);out.append(''.join(z).replace('(fill yes\n','(fill\n'))
  i+=1
 return out
z1=zones(B/'mainboard_revD.kicad_pcb');z2=zones(O/'mainboard_revD.kicad_pcb')
if z1!=z2:raise RuntimeError('Zone definitions differ')
f=N/'mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f))
for z in b.Zones():
 if not z.GetIsRuleArea():z.UnFill()
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
first=f.read_bytes();b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
if f.read_bytes()!=first:raise RuntimeError('Refill nondeterministic')
print(json.dumps(dict(source_sha=hashlib.sha256((B/f.name).read_bytes()).hexdigest(),output_sha=hashlib.sha256(f.read_bytes()).hexdigest(),all_9_board_zone_definitions_exact_old=True,old_filled_polygons_never_imported=True,fresh_refill_save_reload_identical=True,zone_count=len(z1)),indent=2))
