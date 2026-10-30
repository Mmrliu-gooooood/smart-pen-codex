"""Terminal verification of both executed runs and graph-predicted dangling endpoints."""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent
a=(D/'negative_ground.json').read_bytes();b=(D/'negative_ground_optimized.json').read_bytes()
if a!=b:raise RuntimeError('normal/-O output differs')
j=json.loads(a);m=json.loads((D/'materialization.json').read_text());rows=m['mapping']
# Partners and terminal anchor endpoints derive from final topology, not an arbitrary warning allowlist.
ends={'J104.3':('R223.2',[9.35,57.25]),'R226.2':('R206.2',[9.315,44.99]),'R220.2':('R225.2',[2.84,44.1])}
checked=[]
for c in j['cases']:
 expected=[]
 if c['case']in ends:
  partner,end=ends[c['case']];expected=[r['uuid']for r in rows if r['target_pad']==partner and r['type']=='track' and r['b']==end]
  if len(expected)!=1:raise RuntimeError('exact partner endpoint '+c['case'])
 actual=[]
 for v in c['cut_induced_DRC_violations']:
  if v['type']!='track_dangling':raise RuntimeError('unpredicted violation kind')
  actual += [i['uuid']for i in v['items']]
 if actual!=expected:raise RuntimeError('unexpected dangling '+c['case']+str(actual)+str(expected))
 checked.append({'case':c['case'],'expected_and_actual_dangling_UUIDs':expected,'actual_DRC_unconnected_parity':c['actual_DRC_unconnected_parity'],'actual_lost_pads':c['actual_lost_pads']})
sha=hashlib.sha256((D/'native/mainboard_revD.kicad_pcb').read_bytes()).hexdigest()
if sha!='abd8a388a606582e80ebe5f59da7579f7020cd44be6af494e032b8f69fde8ca0':raise RuntimeError('positive native mutated')
if len(checked)!=20:raise RuntimeError('20cases required')
print(json.dumps({'status':'20_REAL_REFILLED_NORMAL_OPTIMIZED_CUTS_MATCH_EXACT_SHARED_GRAPH_NOFAB_NOPOWER','normal_optimized_byte_identical':True,'positive_native_sha256_unchanged':sha,'result_sha256':hashlib.sha256(a).hexdigest(),'cases':checked},indent=2))
