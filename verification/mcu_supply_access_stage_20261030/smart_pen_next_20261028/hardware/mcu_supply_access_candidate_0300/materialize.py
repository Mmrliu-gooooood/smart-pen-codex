from pathlib import Path
import os,json,hashlib,shutil,uuid
os.environ['XDG_CONFIG_HOME']='/tmp/sens-native0158'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];S=R/'hardware/gate_power_candidate_0228/native';N=Path(os.environ.get('MCU_ACCESS_NATIVE_OUTPUT',str(D/'native')));plan=R/'docs/electronics/mcu_supply_access_study_0242/two_vias.json';shutil.copytree(S,N,dirs_exist_ok=True);f=N/'mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f));s=f.read_text();blocks=[];added=[]
for i,t in enumerate(json.loads(plan.read_text())[0]['objects']):
 u=str(uuid.uuid5(uuid.NAMESPACE_URL,'smart-pen/mcu-access-0300/'+str(i)+'/'+json.dumps(t,sort_keys=True)));added.append(u);n=b.GetNetcodeFromNetname(t['net']);a=t['start'];c=t['end']
 if t['type']=='track':blocks.append(f'\t(segment\n\t\t(start {a[0]} {a[1]})\n\t\t(end {c[0]} {c[1]})\n\t\t(width {t["width"]})\n\t\t(layer "{t["layer"]}")\n\t\t(net {n})\n\t\t(uuid "{u}")\n\t)\n')
 else:blocks.append(f'\t(via\n\t\t(at {a[0]} {a[1]})\n\t\t(size {t["width"]})\n\t\t(drill {t["drill"]})\n\t\t(layers "F.Cu" "B.Cu")\n\t\t(net {n})\n\t\t(uuid "{u}")\n\t)\n')
j=s.rfind(')');f.write_text(s[:j]+''.join(blocks)+s[j:]);b=p.LoadBoard(str(f));fps={x.GetReference():x for x in b.GetFootprints()};poses=json.loads(plan.read_text())[0]['poses'];[(fps[ref].SetPosition(p.VECTOR2I(round(v[0]*1e6),round(v[1]*1e6)))) for ref,v in poses.items()];b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);first=f.read_bytes();b=p.LoadBoard(str(f));b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
if f.read_bytes()!=first:raise RuntimeError('fill non-idempotent')
r=dict(base_sha=hashlib.sha256((S/f.name).read_bytes()).hexdigest(),pcb_sha=hashlib.sha256(f.read_bytes()).hexdigest(),plan_sha=hashlib.sha256(plan.read_bytes()).hexdigest(),added=added,removed=[],objects=len(list(b.GetTracks())),status='NOFAB_NOPOWER_RESEARCH_MCU_ACCESS_COURTYARD_AND_SHORT_ESCAPE_UNQUALIFIED');(N.parent/'materialization.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
