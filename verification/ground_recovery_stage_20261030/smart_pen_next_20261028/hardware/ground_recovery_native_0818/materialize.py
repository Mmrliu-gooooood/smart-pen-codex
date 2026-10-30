from pathlib import Path
import os,json,hashlib,shutil,uuid
os.environ['XDG_CONFIG_HOME']='/tmp/ground0818'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];BASE=R/'hardware/camera_schmitt_native_0745/native';MODEL=R/'docs/electronics/ground_recovery_plan_0807/selected20_final.json';N=Path(os.environ.get('GROUND_NATIVE_OUTPUT',str(D/'native')))
def req(c,m):
 if not c:raise RuntimeError(m)
sha=lambda x:hashlib.sha256(x).hexdigest();raw=(BASE/'mainboard_revD.kicad_pcb').read_text();req(sha(raw.encode())=='3276f04433c8ee3759f963fdc133200aee0b398ec6009e31a82fd595ab2f4328','exact0745 parent');m=json.loads(MODEL.read_text());req(len(m['new'])==28 and sum(r['type']=='via'for r in m['new'])==6,'selected28 copper6vias');req(all(r['target_pad']!='R104.2'and not r['target_pad'].startswith('J202.')for r in m['new']),'RF/head excluded')
shutil.copytree(BASE,N,dirs_exist_ok=True);f=N/'mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f));blocks=[];mapping=[]
for r in m['new']:
 req(r['net']=='GND','GND only');u=str(uuid.uuid5(uuid.NAMESPACE_URL,'ground-recovery0818/'+json.dumps(r,sort_keys=True)));net=b.GetNetcodeFromNetname('GND');a=r['a'];z=r['b'];mapping.append(dict(uuid=u,**r))
 if r['type']=='track':block=f'(segment(start {a[0]} {a[1]})(end {z[0]} {z[1]})(width {r["width"]})(layer "{r["layer"]}")(net {net})(uuid "{u}"))\n'
 else:block=f'(via(at {a[0]} {a[1]})(size {r["width"]})(drill {r["drill"]})(layers "F.Cu" "B.Cu")(net {net})(uuid "{u}"))\n'
 blocks.append(block)
i=raw.rfind(')');text=raw[:i]+''.join(blocks)+raw[i:];req(text.replace(''.join(blocks),'')==raw,'inverse prefill exactbytes');f.write_text(text);b=p.LoadBoard(str(f));b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);filled=f.read_bytes();b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);req(f.read_bytes()==filled,'refill byte stable')
(N.parent/'materialization.json').write_text(json.dumps({'status':'GND20_EXPERIMENT_NOFAB_NOPOWER','base_sha256':sha(raw.encode()),'pcb_sha256':sha(f.read_bytes()),'source_model':str(MODEL.relative_to(R)),'model_sha256':sha(MODEL.read_bytes()),'removed':[],'added':sorted(r['uuid']for r in mapping),'mapping':mapping,'objects':len(list(b.GetTracks())),'inverse_prefill_parent_bytes_exact':True,'refill_byte_stable':True,'source_and_footprint_changes':[]},indent=2)+'\n');print('native',sha(f.read_bytes()),len(mapping))
