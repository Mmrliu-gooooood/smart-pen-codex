from pathlib import Path
import os,json,hashlib,shutil,uuid
os.environ['XDG_CONFIG_HOME']='/tmp/ground0818'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];BASE=R/'hardware/ground_pair_native_1007/native';MODEL=D/'selected_final.json';N=Path(os.environ.get('GROUND_NATIVE_OUTPUT',str(D/'native')))
def req(c,m):
 if not c:raise RuntimeError(m)
sha=lambda x:hashlib.sha256(x).hexdigest();raw=(BASE/'mainboard_revD.kicad_pcb').read_text();req(sha(raw.encode())=='6d05642f7d15ba10c22266e551d72b8457d703bd7328dca79ff5c1c50812b4d9','exact accepted ground-pair parent');req(sha(MODEL.read_bytes())=='cdd13c93b680bc2bb01d3378a307d1c5b10f0b37ddb3e62d2137620bf680e994','frozen route model');m=json.loads(MODEL.read_text());req(len(m['new'])==15 and sum(r['type']=='via'for r in m['new'])==1,'fourteen tracks and one via');req(all(r['net']in ['UNUSED_A_INPUT','UNUSED_B_INPUT']and 44<=r['a'][1]<=64 and 44<=r['b'][1]<=64 for r in m['new']),'bounded two-input group')
shutil.copytree(BASE,N,dirs_exist_ok=True);f=N/'mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f));blocks=[];mapping=[]
for r in m['new']:
 req(r['net']in ['UNUSED_A_INPUT','UNUSED_B_INPUT'],'selected two input nets');u=str(uuid.uuid5(uuid.NAMESPACE_URL,'unusedbias1017/'+json.dumps(r,sort_keys=True)));net=b.GetNetcodeFromNetname(r['net']);a=r['a'];z=r['b'];mapping.append(dict(uuid=u,**r))
 if r['type']=='track':block=f'(segment(start {a[0]} {a[1]})(end {z[0]} {z[1]})(width {r["width"]})(layer "{r["layer"]}")(net {net})(uuid "{u}"))\n'
 else:block=f'(via(at {a[0]} {a[1]})(size {r["width"]})(drill {r["drill"]})(layers "F.Cu" "B.Cu")(net {net})(uuid "{u}"))\n'
 blocks.append(block)
i=raw.rfind(')');text=raw[:i]+''.join(blocks)+raw[i:];req(text.replace(''.join(blocks),'')==raw,'inverse prefill exactbytes');f.write_text(text);b=p.LoadBoard(str(f));b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);filled=f.read_bytes();b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);req(f.read_bytes()==filled,'refill byte stable')
(N.parent/'materialization.json').write_text(json.dumps({'status':'UNUSED_BIAS2_EXPERIMENT_NOFAB_NOPOWER','base_sha256':sha(raw.encode()),'pcb_sha256':sha(f.read_bytes()),'source_model':str(MODEL.relative_to(R)),'model_sha256':sha(MODEL.read_bytes()),'removed':[],'added':sorted(r['uuid']for r in mapping),'mapping':mapping,'objects':len(list(b.GetTracks())),'inverse_prefill_parent_bytes_exact':True,'refill_byte_stable':True,'source_and_footprint_changes':[]},indent=2)+'\n');print('native',sha(f.read_bytes()),len(mapping))
