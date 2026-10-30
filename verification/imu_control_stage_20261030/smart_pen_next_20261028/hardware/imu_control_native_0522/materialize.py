from pathlib import Path
import os,json,hashlib,shutil,uuid,sys
os.environ['XDG_CONFIG_HOME']='/tmp/imu-control0522'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];S=R/'hardware/pressure_joint_native_0433/native';P=R/'docs/electronics/imu_visibility_variant_0515';N=Path(os.environ.get('IMU_NATIVE_OUTPUT',str(D/'native')))
sys.path.insert(0,str(R/'hardware/pressure_pullup_revision_0318'));from materialize import children
sha=lambda x:hashlib.sha256(x).hexdigest()
def req(c,m):
 if not c:raise RuntimeError(m)
req(sha((S/'mainboard_revD.kicad_pcb').read_bytes())=='69d93e9dfa7afd427110a271d7fbdcdcd3a0841d79b502c436a50572849c08cc','parent')
req(sha((P/'manifest.json').read_bytes())=='9283c89b82521e7076ae2c5a29359b57ddad8105995380410e1c969d25735395','manifest')
req(sha((P/'strategy1.json').read_bytes())=='25f8a55621a03cc5201c2186c7e29a8769c967a98886d16960825645fca34137','model')
m=json.loads((P/'strategy1.json').read_text());remove=m['removed'];req(len(remove)==3,'three exact AON removals');flat=[dict(tag=tag,index=i,**t)for tag,ts in m['parts'].items()for i,t in enumerate(ts)];req(len(flat)==137,'137 exact additions');req(sum(t['type']=='via'for t in flat)==13,'13 vias')
shutil.copytree(S,N,dirs_exist_ok=True);f=N/'mainboard_revD.kicad_pcb';original=f.read_text();s=original;edits=[]
for a,b,block in children(s):
 if block.startswith(('(segment','(via'))and any(u in block for u in remove):edits.append((a,b,block))
req(len(edits)==3,'actual removals')
for a,b,block in reversed(edits):s=s[:a]+s[b:]
f.write_text(s);board=p.LoadBoard(str(f));blocks=[];added=[];mapping=[]
for t in flat:
 u=str(uuid.uuid5(uuid.NAMESPACE_URL,'smart-pen/imu-control-0522/'+json.dumps(t,sort_keys=True)));added.append(u);mapping.append({'uuid':u,**t});net=board.GetNetcodeFromNetname(t['net']);a=t['a'];b=t['b']
 if t['type']=='track':block=f'\t(segment\n\t\t(start {a[0]} {a[1]})\n\t\t(end {b[0]} {b[1]})\n\t\t(width {t["width"]})\n\t\t(layer "{t["layer"]}")\n\t\t(net {net})\n\t\t(uuid "{u}")\n\t)\n'
 else:block=f'\t(via\n\t\t(at {a[0]} {a[1]})\n\t\t(size {t["width"]})\n\t\t(drill {t["drill"]})\n\t\t(layers "F.Cu" "B.Cu")\n\t\t(net {net})\n\t\t(uuid "{u}")\n\t)\n'
 blocks.append(block)
j=s.rfind(')');s=s[:j]+''.join(blocks)+s[j:];f.write_text(s);back=s.replace(''.join(blocks),'')
for a,b,block in edits:back=back[:a]+block+back[a:]
req(back==original,'inverse prefill exact raw')
board=p.LoadBoard(str(f));board.BuildConnectivity();p.ZONE_FILLER(board).Fill(board.Zones());p.SaveBoard(str(f),board);first=f.read_bytes();board=p.LoadBoard(str(f));p.ZONE_FILLER(board).Fill(board.Zones());p.SaveBoard(str(f),board);req(f.read_bytes()==first,'refill stable')
(N.parent/'materialization.json').write_text(json.dumps({'base_sha':sha(original.encode()),'pcb_sha':sha(f.read_bytes()),'model_sha':sha((P/'strategy1.json').read_bytes()),'removed':remove,'added':added,'mapping':mapping,'objects':len(list(board.GetTracks())),'inverse_prefill_parent_bytes_exact':True,'refill_byte_stable':True},indent=2)+'\n');print('native',len(list(board.GetTracks())),sha(f.read_bytes()))
