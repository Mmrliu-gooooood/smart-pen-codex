import contextlib,io,json
import geometry as q
from finite_copper import build,components,shape,L
with contextlib.redirect_stdout(io.StringIO()):import two_vias as z
p=q.p
bad=q.via('3V3_AON',[.8,7.8]);ee=q.errors([bad]);assert any(x['kind']=='via_pad_including_same_net' and x['other']=='C103.1'for x in ee)
# Removing only U101.2's unique short escape breaks its isolated physical pad from the modeled supply tree.
n=[t for i,t in enumerate(z.n)if i!=0];model=build(q.b)
for i,t in enumerate(n):model.setdefault(t.GetNetname(),[]).append(('negative/'+str(i),False,{l:shape(t,l)for l in L if t.IsOnLayer(l)}))
a=components(model['3V3_AON']);assert not any(set(['U101.2','J106.2'])<=set(c)for c in a)
# GND return tail is necessary after moving C103; without the tail its GND pad is disconnected.
n=[t for t in z.n if t.GetNetname()!='GND'];model=build(q.b)
for i,t in enumerate(n):model.setdefault(t.GetNetname(),[]).append(('negative/'+str(i),False,{l:shape(t,l)for l in L if t.IsOnLayer(l)}))
a=components(model['GND']);assert not any(set(['C103.2','J106.3'])<=set(c)for c in a)
print(json.dumps({'same_net_via_pad_negative_rejected':True,'U101_2_escape_removal_disconnects':True,'C103_ground_tail_removal_disconnects':True,'scope':'finite-model tests, not native fault injection'},indent=2))
