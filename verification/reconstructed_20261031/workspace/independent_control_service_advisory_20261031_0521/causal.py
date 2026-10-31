import reference_final as z
import json,sys
p=z.p;mode=sys.argv[1];b=z.b
before=(z.D/'candidate/mainboard_revD.kicad_pcb').read_bytes();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(z.D/('matched_'+mode+'.kicad_pcb')),b)
if (z.D/('matched_'+mode+'.kicad_pcb')).read_bytes()!=before:raise RuntimeError('prefill mismatch')
new={u:t for u,t in z.bb.items()if u not in z.aa};unions={}
for u,t in new.items():
 if t.GetClass()!='PCB_VIA':unions.setdefault((t.GetNetname(),t.GetLayer()),p.SHAPE_POLY_SET()).BooleanAdd(z.shape(t))
sel=[]
for u,t in z.bb.items():
 via=t.GetClass()=='PCB_VIA';xy=(t.GetPosition().x,t.GetPosition().y)
 if mode=='IOEN_SOURCE'and via and xy==(6875000,5775000) or mode=='FOREIGN'and via and t.GetNetname() not in ['CAM_RESET_UART_TX','CAM_PWDN_UART_RX'] or mode=='ALL_VIAS'and u in new and via or mode=='EDGE_VIA'and via and xy==(13350000,37025000) or mode=='IN2'and u in new and not via and t.GetLayer()==p.In2_Cu:sel.append(u)
for u in sel:b.Remove(z.bb[u])
p.ZONE_FILLER(b).Fill(b.Zones());pc=z.planes(b);rows=[]
for (net,l),q in unions.items():
 ref=(p.In1_Cu if l in [p.F_Cu,p.In2_Cu]else p.In4_Cu,'GND');old=p.SHAPE_POLY_SET();old.BooleanSubtract(q,z.pb[ref]);now=p.SHAPE_POLY_SET();now.BooleanSubtract(q,pc[ref]);recovered=p.SHAPE_POLY_SET();recovered.BooleanIntersection(old,pc[ref]);rows.append({'net':net,'layer':b.GetLayerName(l),'old_missing':old.Area()/1e12,'remaining_missing':now.Area()/1e12,'recovered_original':recovered.Area()/1e12})
(z.D/('causal_'+mode+'.json')).write_text(json.dumps({'mode':mode,'matched_prefill':True,'removed':sel,'projection_rows':rows,'AON_area':pc[p.In2_Cu,'3V3_AON'].Area()/1e12},indent=2))
