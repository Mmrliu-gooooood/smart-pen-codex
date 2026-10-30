from pathlib import Path
import json,shutil,os,subprocess
os.environ['XDG_CONFIG_HOME']='/tmp/gnd-independent-negative2317'
import pcbnew as p
D=Path(__file__).resolve().parent;S=D.parent/'gnd_conservative_recovery_2305';groups=[x for x in json.loads((S/'plan.json').read_text())['components'] if x['accepted_preflight']];chosen=[groups[0],groups[len(groups)//2],groups[-1]];results=[]
for c in chosen:
 n=D/('negative_native_group_'+str(c['id']));shutil.copytree(S/'native',n,dirs_exist_ok=True);f=n/'mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f));ids=set(c['objects']);ct=0
 for t in list(b.GetTracks()):
  if t.m_Uuid.AsString() in ids:b.Remove(t);ct+=1
 if ct!=len(ids):raise RuntimeError('missing removal')
 p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
 out=D/('negative_group_'+str(c['id'])+'.json');q=subprocess.run(['kicad-cli','pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','-o',str(out),str(f)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(D/('negative_group_'+str(c['id'])+'.log')).write_text(q.stdout);j=json.loads(out.read_text());counts=[len(j[k])for k in ['violations','unconnected_items','schematic_parity']]
 if counts[0]!=0 or counts[1]<=203 or counts[2]!=0 or q.returncode!=5:raise RuntimeError((c['id'],counts,q.returncode))
 # Confirm physically removed terminals appear in actual resulting unconnected reports.
 text=json.dumps(j['unconnected_items']); refs={x.split('.')[0] for x in c['pads']}
 if not all(ref in text for ref in refs):raise RuntimeError('target terminals absent')
 results.append({'group':c['id'],'pads':c['pads'],'objects_removed':ct,'counts':counts,'exit_code':q.returncode})
(D/'native_negatives.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
