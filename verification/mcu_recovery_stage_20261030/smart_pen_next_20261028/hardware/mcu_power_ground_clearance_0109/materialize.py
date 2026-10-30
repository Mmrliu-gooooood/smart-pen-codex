from pathlib import Path
import os,json,hashlib,shutil,re
os.environ['XDG_CONFIG_HOME']='/tmp/pen-mcuclear0109'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];S=R/'hardware/mcu_power_ground_candidate_0043/native';N=Path(os.environ.get('MCU_NATIVE_OUTPUT',str(D/'native')));shutil.copytree(S,N,dirs_exist_ok=True);f=N/'mainboard_revD.kicad_pcb';u='07d7a27d-6787-47cd-ace9-bab77d4cc410';s=f.read_text();pattern=r'\t\(via\n.*?\n\t\)\n';found=[]
def edit(m):
 q=m.group(0)
 if u not in q:return q
 if '\t\t(at 4.5 10)'not in q:raise RuntimeError('wrong via position')
 found.append(u);return q.replace('\t\t(at 4.5 10)','\t\t(at 4.25 10.75)')
s=re.sub(pattern,edit,s,flags=re.S)
if found!=[u]:raise RuntimeError('unique via block')
b=p.LoadBoard(str(f));code=b.FindNet('GND').GetNetCode();tu='2a8245e5-1697-5ce2-9c4d-1ff934ed4eb2';block=f'\t(segment\n\t\t(start 4.5 10)\n\t\t(end 4.25 10.75)\n\t\t(width 0.5)\n\t\t(layer "F.Cu")\n\t\t(net {code})\n\t\t(uuid "{tu}")\n\t)\n';j=s.rfind(')');f.write_text(s[:j]+block+s[j:]);b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);first=f.read_bytes();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
if f.read_bytes()!=first:raise RuntimeError('refill differs')
out={'status':'NOFAB_RESEARCH_CLEARANCE_ONLY','parent_sha':hashlib.sha256((S/f.name).read_bytes()).hexdigest(),'pcb_sha':hashlib.sha256(f.read_bytes()).hexdigest(),'moved_via_uuid':u,'old_position_mm':[4.5,10],'new_position_mm':[4.25,10.75],'via_diameter_mm':.6,'drill_mm':.3,'added_track_uuid':tu,'track_width_mm':.5,'note':'Original diameter retained. Drill lies between top EP copper squares with nominal23.8um margin; assembly/thermal process not qualified.'};(N.parent/'materialization.json').write_text(json.dumps(out,indent=2)+'\n')
