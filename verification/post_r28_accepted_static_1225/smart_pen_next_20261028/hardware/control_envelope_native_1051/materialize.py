from pathlib import Path
import os,json,hashlib,shutil,uuid
os.environ['XDG_CONFIG_HOME']='/tmp/ground0818'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];BASE=R/'hardware/unused_bias_native_1017/native';MODEL=D/'selected_final.json';N=Path(os.environ.get('GROUND_NATIVE_OUTPUT',str(D/'native')))
def req(c,m):
 if not c:raise RuntimeError(m)
sha=lambda x:hashlib.sha256(x).hexdigest();raw=(BASE/'mainboard_revD.kicad_pcb').read_text();req(sha(raw.encode())=='2a5400724239f11fe6f589c4f954441deea3c89b0659d1a6292062c99e3e0866','exact accepted unused-bias parent');req(sha(MODEL.read_bytes())=='844986ffdfe2b4c63ed63f6c7a8a7130bfd1a4cbbddf6efbfa79f5cfcc1e89bb','frozen route model');m=json.loads(MODEL.read_text());req(len(m['new'])==20 and sum(r['type']=='via'for r in m['new'])==2,'eighteen tracks and two vias');req(all(r['net']in ['CAM_PWDN_UART_RX','CAM_RESET_UART_TX']and 49<=r['a'][1]<=64 and 49<=r['b'][1]<=64 for r in m['new']),'bounded two-input group')
shutil.copytree(BASE,N,dirs_exist_ok=True);f=N/'mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f));blocks=[];mapping=[]
for r in m['new']:
 req(r['net']in ['CAM_PWDN_UART_RX','CAM_RESET_UART_TX'],'selected two input nets');u=str(uuid.uuid5(uuid.NAMESPACE_URL,'controlenvelope1051/'+json.dumps(r,sort_keys=True)));net=b.GetNetcodeFromNetname(r['net']);a=r['a'];z=r['b'];mapping.append(dict(uuid=u,**r))
 if r['type']=='track':block=f'(segment(start {a[0]} {a[1]})(end {z[0]} {z[1]})(width {r["width"]})(layer "{r["layer"]}")(net {net})(uuid "{u}"))\n'
 else:block=f'(via(at {a[0]} {a[1]})(size {r["width"]})(drill {r["drill"]})(layers "F.Cu" "B.Cu")(net {net})(uuid "{u}"))\n'
 blocks.append(block)
i=raw.rfind(')');text=raw[:i]+''.join(blocks)+raw[i:];req(text.replace(''.join(blocks),'')==raw,'inverse prefill exactbytes');f.write_text(text);b=p.LoadBoard(str(f));b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);filled=f.read_bytes();b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);req(f.read_bytes()==filled,'refill byte stable')
(N.parent/'materialization.json').write_text(json.dumps({'status':'CONTROL_BIAS2_EXPERIMENT_NOFAB_NOPOWER','base_sha256':sha(raw.encode()),'pcb_sha256':sha(f.read_bytes()),'source_model':str(MODEL.relative_to(R)),'model_sha256':sha(MODEL.read_bytes()),'removed':[],'added':sorted(r['uuid']for r in mapping),'mapping':mapping,'objects':len(list(b.GetTracks())),'inverse_prefill_parent_bytes_exact':True,'refill_byte_stable':True,'source_and_footprint_changes':[]},indent=2)+'\n');print('native',sha(f.read_bytes()),len(mapping))
