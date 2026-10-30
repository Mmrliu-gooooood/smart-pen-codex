from pathlib import Path
import os,json,sys,shutil,subprocess,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/ground0920negative'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));from finite_copper import build,components
m=json.loads((D/'materialization.json').read_text());N=D/'negative_cut';shutil.copytree(D/'native',N,dirs_exist_ok=True);f=N/'mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f));ts={t.m_Uuid.AsString():t for t in b.GetTracks()}
for u in m['added']:b.Remove(ts[u])
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);b=p.LoadBoard(str(f));base=p.LoadBoard(str(D.parent/'ground_recovery_native_0818/native/mainboard_revD.kicad_pcb'));a=build(base);c=build(b)
def req(x,msg):
 if not x:raise RuntimeError(msg)
req({n:components(v)for n,v in a.items()}=={n:components(v)for n,v in c.items()},'exact full parent components after native cut')
req(['R218.2']in components(c['GND']),'target returns singleton')
r=subprocess.run(['kicad-cli','pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','-o',str(D/'negative_drc.json'),str(f)],capture_output=True,text=True);(D/'negative_drc.log').write_text(r.stdout+r.stderr);d=json.loads((D/'negative_drc.json').read_text());counts=[len(d[k])for k in ['violations','unconnected_items','schematic_parity']];req(counts==[0,76,0],'exact cut DRC');req(r.returncode==5,'expected unconnected exit')
print(json.dumps({'target':'R218.2','removed_added_uuids':m['added'],'all_nets_exact_parent_components':True,'actual_DRC_unconnected_parity':counts,'negative_pcb_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'scope':'broken test specimen, never fabrication candidate'},indent=2))
