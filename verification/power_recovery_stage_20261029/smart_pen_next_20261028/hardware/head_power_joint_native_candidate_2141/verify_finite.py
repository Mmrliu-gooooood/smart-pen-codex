from pathlib import Path
import os,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/pen-headpowerfinite'
import pcbnew as p
from finite_copper import build,components
D=Path(__file__).resolve().parent;v=json.loads((D/'verify_normal.json').read_text());S=D/'native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(S));nets=build(b)
def req(x,m):
 if not x:raise ValueError(m)
def pair(c,a,z):return any(a in g and z in g for g in c)
for row in v['nineteen_nets']:
 n=row['net'];c=components(nets[n]);req(len(c)==1 and len(c[0])==row['actual_pad_count'],'19 finite '+n)
out=[]
for x in v['fourteen_single_object_negatives']:
 nodes=nets[x['net']];req(pair(components(nodes),x['start'],x['end']),'chain '+x['net']);req(not pair(components([q for q in nodes if q[0]!=x['removed_uuid']]),x['start'],x['end']),'negative '+x['net']);out.append(x['net'])
req(hashlib.sha256(S.read_bytes()).hexdigest()==v['pcb_sha'],'mutated')
print(json.dumps(dict(status='FINITE_COPPER_NOFAB_PARTIAL_CHAINS_ONLY',nineteen_whole_nets=19,fourteen_chains=out,fourteen_negatives_rejected=14,via_drill_subtracted=True,actual_pad_layer_sets_used=True,full_power_and_return_unqualified=True,native_unchanged=True),indent=2))
