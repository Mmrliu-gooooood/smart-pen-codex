from pathlib import Path
import os,json,hashlib,shutil,re,uuid,sys
os.environ['XDG_CONFIG_HOME']='/tmp/imu-native0405'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];S=R/'hardware/pressure_pullup_revision_0318/native';N=Path(os.environ.get('IMU_NATIVE_OUTPUT',str(D/'native')))
sys.path.insert(0,str(R/'hardware/pressure_pullup_revision_0318'));from materialize import children
def req(c,m):
 if not c:raise RuntimeError(m)
sha=lambda x:hashlib.sha256(x).hexdigest()
req(sha((S/'mainboard_revD.kicad_pcb').read_bytes())=='6902c742f9e3995e20cffd1946a8e2c47197cdffe7b4d6357b14a2c0b3857d0c','sourcehash')
P=R/'docs/electronics/imu_j107_clock_joint_0357';req(sha((P/'manifest.json').read_bytes())=='53fdac310f1b3ed4b8279e8ba04f402d99f13e60aabcd661fdf24897ba2e18e8','planmanifest')
plan=json.loads((P/'normal.json').read_text());shutil.copytree(S,N,dirs_exist_ok=True);f=N/'mainboard_revD.kicad_pcb';original=f.read_text();s=original;removed='2010858e-8edf-52c4-a3a5-f423a79bbfc8';edits=[]
for a,b,block in children(s):
 if block.startswith('(footprint ')and '(property "Reference" "J107"'in block:
  req('(at 3.2 84 180)'in block,'oldpose');edits.append((a,b,block.replace('(at 3.2 84 180)','(at 5.2 84 180)',1),block,'pose'))
 if block.startswith('(segment')and removed in block:edits.append((a,b,'',block,'segment'))
req(len(edits)==2,'two edits')
for a,b,new,old,kind in sorted(edits,reverse=True):s=s[:a]+new+s[b:]
f.write_text(s);board=p.LoadBoard(str(f));added=[];blocks=[]
for i,t in enumerate(plan['objects']):
 u=str(uuid.uuid5(uuid.NAMESPACE_URL,'smart-pen/imu-j107-clock-0405/'+str(i)+'/'+json.dumps(t,sort_keys=True)));added.append(u);net=board.GetNetcodeFromNetname(t['net']);a=t['start'];c=t['end']
 if t['type']=='track':blocks.append(f'\t(segment\n\t\t(start {a[0]} {a[1]})\n\t\t(end {c[0]} {c[1]})\n\t\t(width {t["width"]})\n\t\t(layer "{t["layer"]}")\n\t\t(net {net})\n\t\t(uuid "{u}")\n\t)\n')
 else:blocks.append(f'\t(via\n\t\t(at {a[0]} {a[1]})\n\t\t(size {t["width"]})\n\t\t(drill {t["drill"]})\n\t\t(layers "F.Cu" "B.Cu")\n\t\t(net {net})\n\t\t(uuid "{u}")\n\t)\n')
j=s.rfind(')');s=s[:j]+''.join(blocks)+s[j:];f.write_text(s)
# Exact inverse text operation before filler normalization; no source changed.
r=s.replace(''.join(blocks),'');
for a,b,new,old,kind in sorted(edits):
 if kind=='pose':r=r.replace(new,old,1)
 else:r=r[:a]+old+r[a:]
req(r==original,'inverse prefill exact parent bytes')
board=p.LoadBoard(str(f));p.ZONE_FILLER(board).Fill(board.Zones());p.SaveBoard(str(f),board);first=f.read_bytes();board=p.LoadBoard(str(f));p.ZONE_FILLER(board).Fill(board.Zones());p.SaveBoard(str(f),board);req(f.read_bytes()==first,'refill stable')
(N.parent/'materialization.json').write_text(json.dumps({'base_sha':sha(original.encode()),'pcb_sha':sha(f.read_bytes()),'removed':[removed],'added':added,'objects':len(list(board.GetTracks())),'inverse_prefill_parent_bytes_exact':True,'pose':{'J107':{'old':[3.2,84,180,'B.Cu'],'new':[5.2,84,180,'B.Cu']}}},indent=2)+'\n');print('native',len(list(board.GetTracks())),sha(f.read_bytes()))
