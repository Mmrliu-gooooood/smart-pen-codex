from pathlib import Path
import os,json,hashlib,shutil,subprocess,sys,re
os.environ['XDG_CONFIG_HOME']='/tmp/pen-mcuneg0109'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];N=D/'native';m=json.loads((R/'hardware/mcu_power_ground_candidate_0043/materialization.json').read_text());cm=json.loads((D/'materialization.json').read_text());rows=json.loads((R/'docs/electronics/aon_branch_reuse_plan_2318/evaluation.json').read_text())['geometrically_screened_groups'];uid=lambda t:t.m_Uuid.AsString();sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def req(x,msg):
 if not x:raise RuntimeError(msg)
name=sys.argv[1];cases={'remove_all_51':(set(m['AON_added']+m['EP_GND_added']+[cm['added_track_uuid']]),203),'remove_ep9_and_bridge':(set(m['EP_GND_added']+[cm['added_track_uuid']]),190),'remove_RTC_group0':(set(next(g['objects']for g in rows if g['id']==0)),183),'restore_rejected_C504_overlap':({cm['added_track_uuid']},180)};ids,want=cases[name]
out=D/'counterfactual_native'/name;shutil.copytree(N,out,dirs_exist_ok=True);f=out/'mainboard_revD.kicad_pcb';s=f.read_text();removed=[]
def filter_block(mm):
 q=mm.group(0);found=[u for u in ids if u in q]
 if found:removed.extend(found);return ''
 if name=='restore_rejected_C504_overlap' and cm['moved_via_uuid'] in q:
  if '(at 4.25 10.75)'not in q:raise RuntimeError('wrong moved via')
  return q.replace('(at 4.25 10.75)','(at 4.5 10)')
 return q
s=re.sub(r'\t\((?:segment|via|arc)\n.*?\n\t\)\n',filter_block,s,flags=re.S);f.write_text(s);b=p.LoadBoard(str(f))
req(set(removed)==ids,'removal');p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
cmd=['kicad-cli','pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','-o',str(out/'drc.json'),str(f)];rr=subprocess.run(cmd,capture_output=True,text=True);(out/'drc.log').write_text(rr.stdout+rr.stderr);z=json.loads((out/'drc.json').read_text());counts=[len(z[k])for k in['violations','unconnected_items','schematic_parity']];req(rr.returncode==5,'expected unconnected exit5');req(counts==[0,want,0],f'{name} counts {counts}')
if name=='remove_all_51':req(sha(f)==m['base_sha'],'exact rollback baseSHA')
if name=='restore_rejected_C504_overlap':req(sha(f)==cm['parent_sha'],'exact rejectedparentSHA')
(D/('counterfactual_'+name+'.json')).write_text(json.dumps({'case':name,'removed':sorted(ids),'pcb_sha':sha(f),'full_DRC':counts,'exit':rr.returncode,'exact_previous_board':name in['remove_all_51','restore_rejected_C504_overlap'],'note':'0 native violation count does not detect same-net C504 overlap; clearance.py independently rejects reverted parent.'},indent=2)+'\n')
