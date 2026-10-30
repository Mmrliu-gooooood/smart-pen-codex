from pathlib import Path
import os,json,hashlib,uuid,shutil,sys
os.environ['XDG_CONFIG_HOME']='/tmp/pen-joint2141'
os.environ['XDG_CACHE_HOME']='/tmp/pen-joint2141-cache'
os.environ['XDG_DATA_HOME']='/tmp/pen-joint2141-data'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];BASE=R/'hardware/complete_net_restore_candidate_2014/native';PLAN=R/'docs/electronics/head_power_joint_plan_2129/result.json';N=Path(sys.argv[2]).resolve()if len(sys.argv)==3 and sys.argv[1]=='--replay-dir'else D/'native'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
if sha(BASE/'mainboard_revD.kicad_pcb')!='4d7bd85ae460928a48967c00adae133c05df5ef259a6789470c04e986b856f8a':raise RuntimeError('base drift')
plan=json.loads(PLAN.read_text());spec=plan['objects'];dvps={o['net']for o in spec if o['net'].startswith('SENS_')}
if len(spec)!=141 or len(dvps)!=12 or any(plan[k]for k in ['copper_conflicts','drill_conflicts','annulus_pad_overlap','edge_conflicts','rule_conflicts']):raise RuntimeError('plan not applicable')
if N.exists():raise RuntimeError('REFUSE OVERWRITE')
shutil.copytree(BASE,N,ignore=shutil.ignore_patterns('*.kicad_prl'));source_board=p.LoadBoard(str(BASE/'mainboard_revD.kicad_pcb'));removed=[t.m_Uuid.AsString()for t in source_board.GetTracks()if t.GetNetname()in dvps]
if len(removed)!=76:raise RuntimeError('wrong removal ids')
f=N/'mainboard_revD.kicad_pcb';lines=f.read_text().splitlines(keepends=True);blocks=[];i=0;actual=[]
while i<len(lines):
 if lines[i].startswith('\t(segment\n')or lines[i].startswith('\t(via\n')or lines[i].startswith('\t(arc\n'):
  j=i+1
  while j<len(lines)and lines[j]!='\t)\n':j+=1
  block=''.join(lines[i:j+1]);hits=[u for u in removed if u in block]
  if hits:
   if len(hits)!=1:raise RuntimeError('ambiguous block')
   actual.extend(hits)
  else:blocks.append(block)
  i=j+1
 else:blocks.append(lines[i]);i+=1
if set(actual)!=set(removed)or len(actual)!=76:raise RuntimeError('missing serialized object')
f.write_text(''.join(blocks));b=p.LoadBoard(str(f))
if len(list(b.GetTracks()))!=392:raise RuntimeError('remaining count')
V=lambda xy:p.VECTOR2I(round(xy[0]*1e6),round(xy[1]*1e6));oldids={t.m_Uuid.AsString()for t in b.GetTracks()};added=[]
for i,o in enumerate(spec):
 if o['type']=='via':
  t=p.PCB_VIA(b);t.SetPosition(V(o['start']));t.SetWidth(p.F_Cu,round(o['width']*1e6));t.SetDrill(round(o['drill']*1e6));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu)
 else:
  t=p.PCB_TRACK(b);t.SetStart(V(o['start']));t.SetEnd(V(o['end']));t.SetWidth(round(o['width']*1e6));t.SetLayer(b.GetLayerID(o['layer']))
 u=o.get('old_uuid')or str(uuid.uuid5(uuid.NAMESPACE_URL,'smart-pen/head-power-joint-2141/'+str(i)))
 if u in oldids:raise RuntimeError('UUID duplicate')
 random_uuid=t.m_Uuid.AsString();t.SetNetCode(b.GetNetcodeFromNetname(o['net']));b.Add(t);oldids.add(u);added.append(dict(index=i,uuid=u,old=bool(o.get('old_uuid')),net=o['net'],temporary_uuid=random_uuid))
b.BuildConnectivity();p.SaveBoard(str(N/'mainboard_revD.kicad_pcb'),b)
f=N/'mainboard_revD.kicad_pcb';text=f.read_text()
for x in added:
 temp=x.pop('temporary_uuid')
 if text.count(temp)!=1:raise RuntimeError('UUID normalization match')
 text=text.replace(temp,x['uuid'])
f.write_text(text);canonical=p.LoadBoard(str(f));p.SaveBoard(str(f),canonical)

out=dict(status='NOFAB_PARTIAL_HEAD_POWER_NO_FILL',base_sha=sha(BASE/'mainboard_revD.kicad_pcb'),plan_sha=sha(PLAN),pcb_sha=sha(N/'mainboard_revD.kicad_pcb'),removed_dvp_uuids=removed,added=added)
if N==D/'native':(D/'materialization.json').write_text(json.dumps(out,indent=2)+'\n')
else:
 if out['pcb_sha']!=sha(D/'native/mainboard_revD.kicad_pcb'):raise RuntimeError('REPLAY HASH MISMATCH')
print(json.dumps({'pcb_sha':out['pcb_sha'],'removed':len(removed),'added':len(added),'total_copper':len(list(b.GetTracks()))},indent=2))
