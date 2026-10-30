from geometry import *
from finite_copper import build,components,shape as physicalshape
from native_polygon import native_fractured_once
import xml.etree.ElementTree as E
r=json.loads((D/'comparison.json').read_text());N='SENS_VIO_1V8';xml=E.parse(D/'source_netlist.xml').getroot();node=next(n for n in xml.findall('.//nets/net')if n.get('name')==N);src=[n.attrib for n in node];names=sorted(n['ref']+'.'+n['pin']for n in src)
if names!=sorted(x['name']for x in r['pads']):raise RuntimeError('source native mismatch')
source=[]
for n in src:
 q=pm[n['ref']+'.'+n['pin']];f=q.GetParentFootprint();n.update(value=f.GetValue(),footprint=str(f.GetFPID().GetLibItemName()));source.append(n)
# Plane risk model only: subtract nominal new foreign via annulus+0.15mm from current raw fills.
# No native new copper or zone fill is saved. This cannot certify actual post-fill returns.
rows=[];ns=build(b)[N]
for c in r['candidates']:
 items=[]
 for s in c['objects']:items.append(via(N,s['start'])if s['type']=='via'else track(N,b.GetLayerID(s['layer']),s['start'],s['end'],s['width']))
 nodes=ns+[(str(i),False,{l:physicalshape(t,l)for l in L if t.IsOnLayer(l)})for i,t in enumerate(items)]
 comps=components(nodes)
 zones=[];project=[]
 for z in b.Zones():
  if z.GetIsRuleArea()or z.GetNetname()!='GND':continue
  l=z.GetLayer();base=native_fractured_once(z.GetFilledPolysList(l));cut=p.SHAPE_POLY_SET()
  for t in items:
   if t.IsOnLayer(l):cut.BooleanAdd(shape(t,l,150000))
  cut.BooleanIntersection(base);after=p.SHAPE_POLY_SET();after.BooleanSubtract(base,cut);er=p.SHAPE_POLY_SET(after);er.Deflate(250000,p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000)
  zones.append(dict(uuid=z.m_Uuid.AsString(),layer=b.GetLayerName(l),nominal_potential_loss_mm2=cut.Area()/1e12,normalized_025_eroded_components=er.OutlineCount()))
  for t in old:
   if isinstance(t,p.PCB_VIA)or t.GetNetname()in['GND','3V3_AON','CAM_3V3_SW']:continue
   ref=p.In1_Cu if t.GetLayer()==p.F_Cu else p.In4_Cu
   if ref!=l:continue
   inter=p.SHAPE_POLY_SET();inter.BooleanIntersection(shape(t,t.GetLayer()),cut)
   if inter.Area()>10000:project.append(dict(uuid=t.m_Uuid.AsString(),net=t.GetNetname(),projected_loss_mm2=inter.Area()/1e12))
 rows.append(dict(topology=c['topology'],conceptual_same_net_pad_components=comps,all12_theoretically_connected=len(comps)==1 and len(comps[0])==12,planes=zones,old_signal_projected_potential_losses=project,warning='REJECTED GEOMETRY; hypothetical union ignores shorts. Plane subtraction is nominal risk only, not native fresh-fill or return qualification.'))
(D/'evidence.json').write_text(json.dumps(dict(source_count=len(src),source=source,TP_pads=[],external_input_semantics='J202.23 is passive connector pin in schematic, externally supplied head reference by design contract; no source power_out on this net',candidates=rows),indent=2)+'\n')
print(json.dumps(rows,indent=2))
