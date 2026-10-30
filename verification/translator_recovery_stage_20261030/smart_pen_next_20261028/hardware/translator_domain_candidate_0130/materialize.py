from pathlib import Path
import os,json,hashlib,shutil,re,uuid
os.environ['XDG_CONFIG_HOME']='/tmp/translator-native0130'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];S=R/'hardware/mcu_power_ground_clearance_0109/native';N=Path(os.environ.get('TRANSLATOR_NATIVE_OUTPUT',str(D/'native')));shutil.copytree(S,N,dirs_exist_ok=True);f=N/'mainboard_revD.kicad_pcb';s=f.read_text();remove=['65eab90d-6060-4683-a290-98053d52e2b9','4840f47d-9bac-414c-95e5-5f939fd72d28'];found=[]
def cut(m):
 q=m.group(0)
 for u in remove:
  if u in q:found.append(u);return ''
 return q
s=re.sub(r'\t\((?:segment|via)\n.*?\n\t\)\n',cut,s,flags=re.S)
if sorted(found)!=sorted(remove):raise RuntimeError('exact two old C207 objects')
f.write_text(s);b=p.LoadBoard(str(f));poses={}
for q in b.GetFootprints():
 if q.GetReference()in['C207','C208']:
  old=[q.GetPosition().x/1e6,q.GetPosition().y/1e6];new=[10,65]if q.GetReference()=='C207'else[2,65];q.SetPosition(p.VECTOR2I(round(new[0]*1e6),round(new[1]*1e6)));poses[q.GetReference()]=dict(old=old,new=new,orientation=q.GetOrientationDegrees())
p.SaveBoard(str(f),b);s=f.read_text();plan=json.loads((D/'plan_v2.json').read_text());added=[];blocks=[]
for i,t in enumerate(plan['objects']):
 u=str(uuid.uuid5(uuid.NAMESPACE_URL,'smart-pen/translator-domain-0130/'+str(i)+'/'+json.dumps(t,sort_keys=True)));added.append(u);net=b.GetNetcodeFromNetname(t['net']);a=t['start'];c=t['end']
 if t['type']=='track':blocks.append(f'\t(segment\n\t\t(start {a[0]} {a[1]})\n\t\t(end {c[0]} {c[1]})\n\t\t(width {t["width"]})\n\t\t(layer "{t["layer"]}")\n\t\t(net {net})\n\t\t(uuid "{u}")\n\t)\n')
 else:blocks.append(f'\t(via\n\t\t(at {a[0]} {a[1]})\n\t\t(size {t["width"]})\n\t\t(drill {t["drill"]})\n\t\t(layers "F.Cu" "B.Cu")\n\t\t(net {net})\n\t\t(uuid "{u}")\n\t)\n')
j=s.rfind(')');f.write_text(s[:j]+''.join(blocks)+s[j:]);b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);first=f.read_bytes();b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
if f.read_bytes()!=first:raise RuntimeError('refill changed')
(N.parent/'materialization.json').write_text(json.dumps(dict(status='NOFAB_LOCAL_TRANSLATOR_DOMAINS_SENSOR_INPUT_STILL_UNCONNECTED',base_sha=hashlib.sha256((S/f.name).read_bytes()).hexdigest(),pcb_sha=hashlib.sha256(f.read_bytes()).hexdigest(),removed=remove,added=added,poses=poses,objects=len(list(b.GetTracks()))),indent=2)+'\n')
print('materialized',len(added),hashlib.sha256(f.read_bytes()).hexdigest())
