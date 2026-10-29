from pathlib import Path
import pcbnew as p, json, math, hashlib
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'mainboard_revD.kicad_pcb'));ref=p.SHAPE_POLY_SET()
for z in b.Zones():
 if not z.GetIsRuleArea() and z.GetNetname()=='GND' and z.GetLayer()==p.In1_Cu:ref.BooleanAdd(z.GetFilledPolysList(p.In1_Cu))
rows=[];nets=['USB_DP_MCU','USB_DM_MCU','USB_DP','USB_DM'];summary={}
for n in nets:
 tracks=[t for t in b.GetTracks() if t.GetNetname()==n];length=0
 for t in tracks:
  if isinstance(t,p.PCB_VIA) or t.GetLayer()!=p.F_Cu:raise RuntimeError('USB not same F layer')
  q=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(q,p.F_Cu,0,500,p.ERROR_OUTSIDE);r=p.SHAPE_POLY_SET();r.BooleanSubtract(q,ref)
  guard=p.SHAPE_POLY_SET(q);guard.Inflate(p.FromMM(.35),p.CORNER_STRATEGY_ROUND_ALL_CORNERS,1000);rg=p.SHAPE_POLY_SET();rg.BooleanSubtract(guard,ref)
  rows.append({'net':n,'uuid':t.m_Uuid.AsString(),'width_mm':p.ToMM(t.GetWidth()),'length_mm':p.ToMM(t.GetLength()),'unreferenced_trace_area_mm2':r.Area()/1e12,'unreferenced_0p35_guard_area_mm2':rg.Area()/1e12});length+=p.ToMM(t.GetLength())
 summary[n]={'length_mm':length,'segments':len(tracks)}
for aa,zz in [('USB_DP_MCU','USB_DM_MCU'),('USB_DP','USB_DM')]:
 summary[aa+'/'+zz]={'length_mismatch_mm':abs(summary[aa]['length_mm']-summary[zz]['length_mm']),'uniform_pair_spacing':False}
def point_segment(x,y,t):
 a,c=t.GetStart(),t.GetEnd();ax,ay,cx,cy=map(p.ToMM,[a.x,a.y,c.x,c.y]);dx,dy=cx-ax,cy-ay;den=dx*dx+dy*dy;u=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/den)) if den else 0
 return math.hypot(x-ax-u*dx,y-ay-u*dy)
for aa,zz in [('USB_DP_MCU','USB_DM_MCU'),('USB_DP','USB_DM')]:
 pair=[t for t in b.GetTracks() if t.GetNetname()==aa];other=[t for t in b.GetTracks() if t.GetNetname()==zz];distances=[]
 for t in pair:
  a,c=t.GetStart(),t.GetEnd();count=max(1,math.ceil(p.ToMM(t.GetLength())/.025))
  for k in range(count+1):
   x,y=p.ToMM(a.x+(c.x-a.x)*k/count),p.ToMM(a.y+(c.y-a.y)*k/count)
   distances.append(min(point_segment(x,y,z)-p.ToMM(t.GetWidth()+z.GetWidth())/2 for z in other))
 summary[aa+'/'+zz]['sampled_trace_edge_gap_min_mm']=min(distances)
 summary[aa+'/'+zz]['sampled_nearest_opposite_trace_edge_gap_max_mm']=max(distances)
 summary[aa+'/'+zz]['spacing_scope']='Nearest opposite-net track edge at <=.025 mm sample intervals; excludes pads; nonuniform geometry, not an impedance result.'
summary['complete_DP_trace_only_mm']=summary['USB_DP_MCU']['length_mm']+summary['USB_DP']['length_mm']
summary['complete_DM_trace_only_mm']=summary['USB_DM_MCU']['length_mm']+summary['USB_DM']['length_mm']
summary['complete_trace_only_mismatch_mm']=abs(summary['complete_DP_trace_only_mm']-summary['complete_DM_trace_only_mm'])
summary['length_scope']='Sum of actual native track centerline lengths only. U101 pad, R112/R113 pad/body/internal path, and J109 land traversal contributions are not included; external harness/tail PCB excluded. This is not full end-to-end electrical length.'
out={'status':'FINITE_REFERENCE_GEOMETRY_ONLY_NOT_IMPEDANCE_OR_USB_COMPLIANCE','pcb_sha256':hashlib.sha256((D/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'summary':summary,'rows':rows,'unsupported_trace_segments':sum(x['unreferenced_trace_area_mm2']>1e-12 for x in rows),'guard_note':'0.35 mm side envelope is screening only, not approved USB impedance model'}
(D/'usb_reference.json').write_text(json.dumps(out,indent=2));print(json.dumps(out['summary'],indent=2));print('unsupported',out['unsupported_trace_segments'])
if out['unsupported_trace_segments']:raise RuntimeError('USB trace lacks finite In1 reference')
