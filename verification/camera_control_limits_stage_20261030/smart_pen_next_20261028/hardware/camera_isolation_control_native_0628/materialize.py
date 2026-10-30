from pathlib import Path
import os,json,hashlib,shutil,uuid,sys
os.environ['XDG_CONFIG_HOME']='/tmp/imu-control0522'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];S=R/'hardware/imu_control_native_0522/native';P=R/'docs/electronics/camera_isolation_control_0622';N=Path(os.environ.get('IMU_NATIVE_OUTPUT',str(D/'native')))
sys.path.insert(0,str(R/'hardware/pressure_pullup_revision_0318'));from materialize import children
sha=lambda x:hashlib.sha256(x).hexdigest()
def req(c,m):
 if not c:raise RuntimeError(m)
req(sha((S/'mainboard_revD.kicad_pcb').read_bytes())=='5ed5f0ad90f5f15830f50479e0ecc48fe0685ffaff1819ff642a300f9550a1e9','parent')
req(sha((P/'model.json').read_bytes())=='32108a3e4da8d9be54d7bdc5de35da961c07a53013d05a65eefe79d0c3503bd1','exact model SHA')
m=json.loads((P/'model.json').read_text());remove=m['removed'];req(len(remove)==0,'three exact AON removals');flat=[dict(tag=tag,index=i,**t)for tag,ts in m['parts'].items()for i,t in enumerate(ts)];req(len(flat)==209,'137 exact additions');req(sum(t['type']=='via'for t in flat)==16,'16 vias')
shutil.copytree(S,N,dirs_exist_ok=True);f=N/'mainboard_revD.kicad_pcb';original=f.read_text();s=original;edits=[]
for a,b,block in children(s):
 if block.startswith(('(segment','(via'))and any(u in block for u in remove):edits.append((a,b,block))
req(len(edits)==0,'actual removals')
for a,b,block in reversed(edits):s=s[:a]+s[b:]
f.write_text(s);board=p.LoadBoard(str(f));blocks=[];added=[];mapping=[]
for t in flat:
 u=str(uuid.uuid5(uuid.NAMESPACE_URL,'smart-pen/camera-isolation-control-0628/'+json.dumps(t,sort_keys=True)));added.append(u);mapping.append({'uuid':u,**t});net=board.GetNetcodeFromNetname(t['net']);a=t['a'];b=t['b']
 if t['type']=='track':block=f'\t(segment\n\t\t(start {a[0]} {a[1]})\n\t\t(end {b[0]} {b[1]})\n\t\t(width {t["width"]})\n\t\t(layer "{t["layer"]}")\n\t\t(net {net})\n\t\t(uuid "{u}")\n\t)\n'
 else:block=f'\t(via\n\t\t(at {a[0]} {a[1]})\n\t\t(size {t["width"]})\n\t\t(drill {t["drill"]})\n\t\t(layers "F.Cu" "B.Cu")\n\t\t(net {net})\n\t\t(uuid "{u}")\n\t)\n'
 blocks.append(block)
j=s.rfind(')');s=s[:j]+''.join(blocks)+s[j:];f.write_text(s);back=s.replace(''.join(blocks),'')
for a,b,block in edits:back=back[:a]+block+back[a:]
req(back==original,'inverse prefill exact raw')
board=p.LoadBoard(str(f));board.BuildConnectivity();p.ZONE_FILLER(board).Fill(board.Zones());p.SaveBoard(str(f),board);first=f.read_bytes();board=p.LoadBoard(str(f));p.ZONE_FILLER(board).Fill(board.Zones());p.SaveBoard(str(f),board);req(f.read_bytes()==first,'refill stable')
(N.parent/'materialization.json').write_text(json.dumps({'base_sha':sha(original.encode()),'pcb_sha':sha(f.read_bytes()),'model_sha':sha((P/'model.json').read_bytes()),'removed':remove,'added':added,'mapping':mapping,'objects':len(list(board.GetTracks())),'inverse_prefill_parent_bytes_exact':True,'refill_byte_stable':True},indent=2)+'\n');print('native',len(list(board.GetTracks())),sha(f.read_bytes()))
