from pathlib import Path
import os,json,hashlib,shutil,uuid,re
os.environ['XDG_CONFIG_HOME']='/tmp/sccb1111material'
import pcbnew as p
D=Path(__file__).resolve().parent;A=D.parent/'sccb_local_reference_1216/native';N=Path(os.environ.get('GROUND_NATIVE_OUTPUT',str(D/'native')));MODEL=D/'selected_final.json';sha=lambda x:hashlib.sha256(x).hexdigest()
def req(c,m):
 if not c:raise RuntimeError(m)
def blocks(s):
 depth=0;quote=False;esc=False;start=0
 for i,c in enumerate(s):
  if quote:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':quote=False
  elif c=='"':quote=True
  elif c=='(':
   depth+=1
   if depth==2:start=i
  elif c==')':
   if depth==2:yield s[start:i+1]
   depth-=1
raw=(A/'mainboard_revD.kicad_pcb').read_text();req(sha(raw.encode())=='dcbd2e6501c8294ece5ecf7b41ffcc86ccc7f58f7cb54ececfdf24962a50f697','accepted parent');m=json.loads(MODEL.read_text())
# Final model hash is pinned before freeze; exploratory runner cannot be mistaken for release.
EXPECTED_MODEL='d87fd2c831cc37500c9ec7670707ec1feb1d4f220164f0ad90faf230cef464dd'
req(sha(MODEL.read_bytes())==EXPECTED_MODEL,'exact final route model')
req(set(r['net']for r in m['new'])<= ({'CAM_D'+str(i)for i in range(8)}|{'GND'}),'bounded nets')
removed=m['removed'];req(len(removed)==9,'nine exact obsolete GND tracks')
found={}
for block in blocks(raw):
 match=re.search(r'\(uuid "([^"]+)"\)',block)
 if match and match.group(1)in removed:found[match.group(1)]=block
req(set(found)==set(removed)and all(x.startswith(('(segment','(via'))for x in found.values()),'exact removal blocks')
for block in found.values():raw=raw.replace(block,'',1)
shutil.copytree(A,N,dirs_exist_ok=True);f=N/'mainboard_revD.kicad_pcb';f.write_text(raw);boards=[];b=p.LoadBoard(str(f));boards.append(b);fps={x.GetReference():x for x in b.GetFootprints()}
for ref,pose in m['poses'].items():
 req(ref in ['R210','R217'],'only authorized moves');fps[ref].SetPosition(p.VECTOR2I(round(pose[0]*1e6),round(pose[1]*1e6)));fps[ref].SetOrientationDegrees(pose[2])
p.SaveBoard(str(f),b);raw=f.read_text();add=[];mapping=[]
for r in m['new']:
 u=str(uuid.uuid5(uuid.NAMESPACE_URL,'data1242/'+json.dumps(r,sort_keys=True)));net=b.GetNetcodeFromNetname(r['net']);a=r['a'];z=r['b'];mapping.append(dict(uuid=u,**r))
 if r['type']=='track':block=f'(segment(start {a[0]} {a[1]})(end {z[0]} {z[1]})(width {r["width"]})(layer "{r["layer"]}")(net {net})(uuid "{u}"))\n'
 else:block=f'(via(at {a[0]} {a[1]})(size {r["width"]})(drill {r["drill"]})(layers "F.Cu" "B.Cu")(net {net})(uuid "{u}"))\n'
 add.append(block)
i=raw.rfind(')');f.write_text(raw[:i]+''.join(add)+raw[i:]);b=p.LoadBoard(str(f));boards.append(b);fillers=[p.ZONE_FILLER(b)];fillers[-1].Fill(b.Zones());p.SaveBoard(str(f),b);filled=f.read_bytes();b=p.LoadBoard(str(f));boards.append(b);fillers.append(p.ZONE_FILLER(b));fillers[-1].Fill(b.Zones());p.SaveBoard(str(f),b);req(f.read_bytes()==filled,'fill reload byte stable')
(N.parent/'materialization.json').write_text(json.dumps({'status':'DATA8_BIAS_RELOCATION_CANDIDATE_NOFAB_NOPOWER','base_sha256':sha((A/'mainboard_revD.kicad_pcb').read_bytes()),'pcb_sha256':sha(f.read_bytes()),'model_sha256':sha(MODEL.read_bytes()),'removed':removed,'removed_raw_sha256':{u:sha(s.encode())for u,s in found.items()},'added':sorted(r['uuid']for r in mapping),'mapping':mapping,'poses':m['poses'],'plane_patch':None,'refill_byte_stable':True,'source_net_value_changes':[]},indent=2)+'\n');print('native',sha(f.read_bytes()))
