import contextlib,io,json
import geometry as q
from finite_copper import build,components,shape,L
with contextlib.redirect_stdout(io.StringIO()):import two_vias as z
p=q.p
def require(x):
 if not x:raise ValueError("negative expectation failed")
bad=q.via('3V3_AON',[.8,7.8]);ee=q.errors([bad]);require(any(x['kind']=='via_pad_including_same_net' and x['other']=='C103.1'for x in ee))
# Removing only U101.2's unique short escape breaks its isolated physical pad from the modeled supply tree.
n=[t for i,t in enumerate(z.n)if i!=0];model=build(q.b)
for i,t in enumerate(n):model.setdefault(t.GetNetname(),[]).append(('negative/'+str(i),False,{l:shape(t,l)for l in L if t.IsOnLayer(l)}))
a=components(model['3V3_AON']);require(not any(set(['U101.2','J106.2'])<=set(c)for c in a))
# Existing GND stub still overlaps the shifted capacitor; added tail is reinforcement, not sole return.
n=[t for t in z.n if t.GetNetname()!='GND'];model=build(q.b)
for i,t in enumerate(n):model.setdefault(t.GetNetname(),[]).append(('negative/'+str(i),False,{l:shape(t,l)for l in L if t.IsOnLayer(l)}))
a=components(model['GND']);require(any(set(['C103.2','J106.3'])<=set(c)for c in a))
print(json.dumps({'same_net_via_pad_negative_rejected':True,'U101_2_escape_removal_disconnects':True,'C103_added_ground_tail_is_redundant_reinforcement':True,'scope':'finite-model tests, not native fault injection'},indent=2))
