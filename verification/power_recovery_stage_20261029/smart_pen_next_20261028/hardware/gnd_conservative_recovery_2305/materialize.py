from pathlib import Path
import os,json,shutil,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/pen-gndnative2305';os.environ['XDG_CACHE_HOME']='/tmp/pen-gndnative2305-cache'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];B=R/'hardware/aon_entry_bridge_candidate_2156/native';O=R/'hardware/j202_low_speed_reference_candidate/native';N=D/'native';plan=json.loads((D/'plan.json').read_text());ids=set(u for c in plan['components']if c['accepted_preflight']for u in c['objects']);shutil.copytree(B,N,dirs_exist_ok=True);f=N/'mainboard_revD.kicad_pcb'
a=p.LoadBoard(str(O/f.name));b=p.LoadBoard(str(f))
if a.FindNet('GND').GetNetCode()!=b.FindNet('GND').GetNetCode():raise RuntimeError('netcode')
if ids&{t.m_Uuid.AsString()for t in b.GetTracks()}:raise RuntimeError('duplicate UUID')
lines=(O/f.name).read_text().splitlines(keepends=True);blocks=[];i=0
while i<len(lines):
 if lines[i]in['\t(segment\n','\t(via\n','\t(arc\n']:
  z=[]
  while lines[i]!='\t)\n':z.append(lines[i]);i+=1
  z.append(lines[i]);s=''.join(z)
  if any(u in s for u in ids):blocks.append(s)
 i+=1
if len(blocks)!=len(ids):raise RuntimeError('missing UUID')
s=f.read_text();pos=s.rfind(')');f.write_text(s[:pos]+''.join(blocks)+s[pos:]);b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);first=f.read_bytes();b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
if first!=f.read_bytes():raise RuntimeError('refill')
print(json.dumps(dict(base_sha=hashlib.sha256((B/f.name).read_bytes()).hexdigest(),pcb_sha=hashlib.sha256(f.read_bytes()).hexdigest(),added_uuids=sorted(ids),old_complete_components=[x['id']for x in plan['components']if x['accepted_preflight']],rejected_whole_component=37,fresh_refill_deterministic=True),indent=2))
