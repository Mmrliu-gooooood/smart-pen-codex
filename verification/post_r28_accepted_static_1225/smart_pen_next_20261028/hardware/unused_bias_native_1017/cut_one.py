from pathlib import Path
import os,sys,json,shutil,subprocess,hashlib
os.environ.update(XDG_CONFIG_HOME='/tmp/unused1017neg/config',XDG_CACHE_HOME='/tmp/unused1017neg/cache',XDG_DATA_HOME='/tmp/unused1017neg/data')
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));from finite_copper import build,components
m=json.loads((D/'materialization.json').read_text());model=json.loads((D/'selected_final.json').read_text());a=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));before={n:components(v)for n,v in build(a).items()};target=sys.argv[1];nets=list(model['targets'])if target=='BOTH'else['UNUSED_B_INPUT']if target=='VIA_ONLY'else[target];ids=[r['uuid']for r in m['mapping']if r['net']in nets and(target!='VIA_ONLY'or r['type']=='via')];N=D/'negative_cuts'/target;shutil.copytree(D/'native',N,dirs_exist_ok=True);f=N/'mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f));ts={t.m_Uuid.AsString():t for t in b.GetTracks()};expected_violation=[]
def req(c,s):
 if not c:raise RuntimeError(s)
if target=='VIA_ONLY':
 req(len(ids)==1,'one actual via');via=ts[ids[0]];expected_violation=sorted(('track_dangling',u)for u,t in ts.items()if u not in ids and t.GetNetname()=='UNUSED_B_INPUT'and via.GetPosition()in[t.GetStart(),t.GetEnd()]);req(len(expected_violation)==2,'exact two endpoint tracks at via')
for u in ids:b.Remove(ts[u])
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);b=p.LoadBoard(str(f));actual={n:components(v)for n,v in build(b).items()};expected={n:[c[:]for c in cs]for n,cs in before.items()}
for net in nets:expected[net]=sorted([[pin]for pin in model['targets'][net]])
req(actual==expected,'exact selected net split only '+target)
r=subprocess.run(['kicad-cli','pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','-o',str(N/'drc.json'),str(f)],capture_output=True,text=True);(N/'drc.log').write_text(r.stdout+r.stderr);d=json.loads((N/'drc.json').read_text());counts=[len(d[k])for k in ['violations','unconnected_items','schematic_parity']];req(counts==[len(expected_violation),71+len(nets),0],'exact cut DRC '+target);req(sorted((v['type'],i['uuid'])for v in d['violations']for i in v['items'])==expected_violation,'exact predicted dangling UUIDs')
(N/'result.json').write_text(json.dumps({'target':target,'removed_uuids':ids,'exact_selected_component_splits_only':True,'actual_DRC_unconnected_parity':counts,'predicted_violations':expected_violation,'pcb_sha256':hashlib.sha256(f.read_bytes()).hexdigest()},indent=2)+'\n');print('single cut pass',target)
