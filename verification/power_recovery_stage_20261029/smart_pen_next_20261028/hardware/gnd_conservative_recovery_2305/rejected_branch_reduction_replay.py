from pathlib import Path
import os,json,shutil,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/pen-gnd-recovery2305'
import pcbnew as p
D=Path(__file__).resolve().parent;S=D.parent/'gnd_fixed_branch_candidate_2159';B=D.parent/'aon_entry_bridge_candidate_2156';N=D/'native';shutil.copytree(S/'native',N,dirs_exist_ok=True)
# Import parser without executing prior comparison loop.
s=(D/'compare_removals.py').read_text();scope={'__file__':str(D/'compare_removals.py')};exec(s[:s.index('N=Path("/tmp/')],scope);remove=scope['remove']
plan=json.loads((S/'plan.json').read_text());g=next(x for x in plan['components']if x['id']==37);ids=set(g['objects']);g['accepted_preflight']=False;g['rejection'].append('additional_AON_025_erosion_split_whole_component_rejected');plan['accepted_components']=sum(x['accepted_preflight']for x in plan['components']);plan['accepted_objects']=sum(len(x['objects'])for x in plan['components']if x['accepted_preflight']);(D/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');(D/'plan_optimized.json').write_bytes((D/'plan.json').read_bytes())
f=N/'mainboard_revD.kicad_pcb';f.write_text(remove(f.read_text(),ids));b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);before=f.read_bytes();b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
if before!=f.read_bytes():raise RuntimeError('refill nondeterministic')
oldmat=json.loads((S/'materialization.json').read_text());added=sorted(set(oldmat['added_uuids'])-ids)
print(json.dumps(dict(base_sha=hashlib.sha256((B/'native'/f.name).read_bytes()).hexdigest(),pcb_sha=hashlib.sha256(f.read_bytes()).hexdigest(),added_uuids=added,old_complete_components=[x['id']for x in plan['components']if x['accepted_preflight']],rejected_whole_component=37,rejected_objects=sorted(ids),rejected_pads=g['pads'],fresh_refill_deterministic=True),indent=2))
