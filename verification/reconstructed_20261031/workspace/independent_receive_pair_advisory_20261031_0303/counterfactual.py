import reference_final as z
import sys,json,hashlib
p=z.p;mode=sys.argv[1];b=z.b;before=(z.D/'selected_candidate/mainboard_revD.kicad_pcb').read_bytes();p.ZONE_FILLER(b).Fill(b.Zones());tmp=z.D/('matched_'+mode+'.kicad_pcb');p.SaveBoard(str(tmp),b)
if tmp.read_bytes()!=before:raise RuntimeError('prefill differs')
sel=[]
for u,t in z.bb.items():
 if u in z.aa:continue
 via=isinstance(t,p.PCB_VIA);net=t.GetNetname();xy=(t.GetPosition().x,t.GetPosition().y)
 if (mode=='PCLK_SOURCE'and via and xy==(5937500,14300000))or(mode=='HREF_SOURCE'and via and xy==(6862500,14300000))or(mode=='IN2_TRACKS'and not via and t.GetLayer()==p.In2_Cu)or(mode=='C104_GND'and via and xy==(7850000,15200000)):sel.append(u)
for u in sel:b.Remove(z.bb[u])
p.ZONE_FILLER(b).Fill(b.Zones());pc=z.planes(b);rows=[]
for r in json.loads((z.D/'reference_checkpoint.json').read_text())['retained_reference_losses']:
 k=(b.GetLayerID(r['reference_layer']),r['reference_net']);old=p.SHAPE_POLY_SET();old.BooleanIntersection(z.shape(z.aa[r['uuid']]),z.pa[k]);lost=p.SHAPE_POLY_SET();lost.BooleanSubtract(old,z.pb[k]);remain=p.SHAPE_POLY_SET();remain.BooleanSubtract(old,pc[k]);recover=p.SHAPE_POLY_SET();recover.BooleanIntersection(lost,pc[k]);rows.append({'uuid':r['uuid'],'net':r['net'],'reference':r['reference_layer'],'original_loss':lost.Area()/1e12,'remaining_loss':remain.Area()/1e12,'recovered_original':recover.Area()/1e12})
(z.D/('cf_'+mode+'.json')).write_text(json.dumps({'mode':mode,'matched_prefill_exact':True,'removed':sel,'rows':rows,'scope':'Diagnostic only; deleted connectivity invalid as candidate'},indent=2))
