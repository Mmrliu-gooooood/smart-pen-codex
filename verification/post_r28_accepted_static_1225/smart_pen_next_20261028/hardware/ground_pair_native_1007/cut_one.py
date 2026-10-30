from pathlib import Path
import os,json,sys,shutil,subprocess,hashlib
os.environ.update(XDG_CONFIG_HOME='/tmp/ground1007neg/config',XDG_CACHE_HOME='/tmp/ground1007neg/cache',XDG_DATA_HOME='/tmp/ground1007neg/data')
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));from finite_copper import build,components
m=json.loads((D/'materialization.json').read_text());a=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));before={n:components(v)for n,v in build(a).items()};rows=[]
def req(x,msg):
 if not x:raise RuntimeError(msg)
for target in [sys.argv[1]]:
 targets=['R219.2','R229.2']if target=='BOTH'else[target];ids=[r['uuid']for r in m['mapping']if r['target_pad']in targets];N=D/'negative_cuts'/target;shutil.copytree(D/'native',N,dirs_exist_ok=True);f=N/'mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f));ts={t.m_Uuid.AsString():t for t in b.GetTracks()}
 for u in ids:b.Remove(ts[u])
 b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);b=p.LoadBoard(str(f));actual={n:components(v)for n,v in build(b).items()};expected={n:[c[:]for c in cs]for n,cs in before.items()}
 for name in targets:
  next(c for c in expected['GND']if name in c).remove(name);expected['GND'].append([name])
 expected['GND']=sorted(c for c in expected['GND']if c);req(actual==expected,'exact selected pad split only '+target)
 r=subprocess.run(['kicad-cli','pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','-o',str(N/'drc.json'),str(f)],capture_output=True,text=True);(N/'drc.log').write_text(r.stdout+r.stderr);d=json.loads((N/'drc.json').read_text());counts=[len(d[k])for k in ['violations','unconnected_items','schematic_parity']];req(counts==[0,73+len(targets),0],'exact cut DRC '+target);rows.append({'target':target,'removed_uuids':ids,'exact_named_pad_components_only':True,'actual_DRC_unconnected_parity':counts,'pcb_sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(N/'result.json').write_text(json.dumps(rows[0],indent=2)+'\n');print('single cut pass',target)
