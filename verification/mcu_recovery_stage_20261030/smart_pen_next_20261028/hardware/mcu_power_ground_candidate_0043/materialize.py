from pathlib import Path
import os,json,hashlib,shutil
os.environ['XDG_CONFIG_HOME']='/tmp/pen-mcupower0043';os.environ['XDG_CACHE_HOME']='/tmp/pen-mcupower0043-cache'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];B=R/'hardware/gnd_conservative_recovery_2305/native';O=R/'hardware/j202_low_speed_reference_candidate/native';N=D/'native';P=R/'docs/electronics/aon_branch_reuse_plan_2318/evaluation.json'
uid=lambda t:t.m_Uuid.AsString();sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def require(c,m):
 if not c:raise RuntimeError(m)
old=p.LoadBoard(str(O/'mainboard_revD.kicad_pcb'));base=p.LoadBoard(str(B/'mainboard_revD.kicad_pcb'));rows=json.loads(P.read_text())['geometrically_screened_groups'];aon={x['uuid']for g in rows for x in g['geometry']};widen={x['uuid']for g in rows if g['id']in[0,5,6]for x in g['geometry']if x['type']=='track'}
ep=[q for f in base.GetFootprints()if f.GetReference()=='U101'for q in f.Pads()if q.GetNetname()=='GND'];require(len(ep)==9 and all(q.GetNumber()=='57'for q in ep),'EP scope')
gnd={uid(t)for t in old.GetTracks()if isinstance(t,p.PCB_VIA)and t.GetNetname()=='GND'and any(t.GetPosition()==q.GetPosition()for q in ep)};require(len(aon)==41 and len(widen)==10 and len(gnd)==9,'selection counts');ids=aon|gnd
require(not ids&{uid(t)for t in base.GetTracks()},'duplicate');shutil.copytree(B,N,dirs_exist_ok=True);f=N/'mainboard_revD.kicad_pcb';lines=(O/f.name).read_text().splitlines(keepends=True);blocks=[];i=0
while i<len(lines):
 if lines[i]in['\t(segment\n','\t(via\n','\t(arc\n']:
  z=[]
  while lines[i]!='\t)\n':z.append(lines[i]);i+=1
  z.append(lines[i]);s=''.join(z)
  if any(u in s for u in ids):blocks.append(s)
 i+=1
require(len(blocks)==50,'block extraction');s=f.read_text();j=s.rfind(')');f.write_text(s[:j]+''.join(blocks)+s[j:]);b=p.LoadBoard(str(f));changed=[]
for t in b.GetTracks():
 if uid(t)in widen:
  require(t.GetNetname()=='3V3_AON'and not isinstance(t,p.PCB_VIA)and t.GetWidth()==150000,'widen source');t.SetWidth(254000);changed.append(uid(t))
require(len(changed)==10,'widened count');p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);first=f.read_bytes();b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);require(first==f.read_bytes(),'refill nondeterministic')
print(json.dumps(dict(status='NOFAB_RESEARCH_ONLY',base_sha=sha(B/f.name),old_sha=sha(O/f.name),plan_sha=sha(P),pcb_sha=sha(f),AON_added=sorted(aon),EP_GND_added=sorted(gnd),widened_254um=sorted(widen),complete_AON_groups=[g['id']for g in rows],new_copper_count=len(list(b.GetTracks())),EP_process_gate='Original nine 0.60/0.30 through-vias in EP pads restored geometrically only. Hole treatment, solder voiding/wicking and assembly thermal qualification remain open.'),indent=2))
