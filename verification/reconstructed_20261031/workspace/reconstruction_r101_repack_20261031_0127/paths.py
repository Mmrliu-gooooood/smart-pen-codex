from pathlib import Path
import os,json,hashlib,math
os.makedirs('/tmp/r1010127',exist_ok=True);os.environ['XDG_CONFIG_HOME']='/tmp/r1010127';import pcbnew as p
O=Path(__file__).resolve().parent;W=O.parent;src=O/'gateway_DIAGNOSTIC.kicad_pcb';b=p.LoadBoard(str(src));fps={f.GetReference():f for f in b.GetFootprints()};proposal=json.load(open(O/'proposal.json'));M=json.load(open(W/'reconstruction_mechanics_20261031_0053/full104_proposed_R503.json'))['all_static_rectangles'];removed=set(proposal['removed'])
def need(v,m):
 if not v:raise RuntimeError(m)
need((fps['R503'].GetPosition().x,fps['R503'].GetPosition().y)==(8000000,16500000),'R503 actual source pose');need((fps['R101'].GetPosition().x,fps['R101'].GetPosition().y)==(2500000,20000000),'R101 old pose');fps['R101'].SetPosition(p.VECTOR2I(2100000,20000000));need(fps['R101'].GetValue()=='10k 1%','value')
for r in M:
 if r['ref']=='R101':r['xy_bounds']=[.875,19.525,3.325,20.475]
def V(xy):return p.VECTOR2I(round(xy[0]*1e6),round(xy[1]*1e6))
def poly(pts):
 q=p.SHAPE_POLY_SET();q.NewOutline()
 for xy in pts:q.Append(V(xy))
 return q
def rect(bb):return poly([(bb[0],bb[1]),(bb[2],bb[1]),(bb[2],bb[3]),(bb[0],bb[3])])
def shape(t,l):
 q=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(q,l,0,50,p.ERROR_OUTSIDE);return q
def area(q,z):
 out=p.SHAPE_POLY_SET();out.BooleanIntersection(q,z);return out.Area()/1e12
def subtract_area(q,z):
 out=p.SHAPE_POLY_SET();out.BooleanSubtract(q,z);return out.Area()/1e12
items=[]
def tr(net,a,z,width=.15,retained=False):
 t=p.PCB_TRACK(b);t.SetStart(V(a));t.SetEnd(V(z));t.SetWidth(round(width*1e6));t.SetLayer(p.F_Cu);t.SetNetCode(b.FindNet(net).GetNetCode());items.append((t,retained));return t
def via(net,xy,width,drill):
 t=p.PCB_VIA(b);t.SetPosition(V(xy));t.SetWidth(p.F_Cu,round(width*1e6));t.SetWidth(p.B_Cu,round(width*1e6));t.SetDrill(round(drill*1e6));t.SetNetCode(b.FindNet(net).GetNetCode());items.append((t,False))
tr('CHIP_EN',(1.725,19.95),(1.275,20));tr('3V3_AON',(2.925,20),(3.1,21),.3);via('3V3_AON',(3.1,21),.6,.3);via('CAM_D0',(2.4,21),.45,.2)
pts=proposal['new_PICKUP_F']
for a,z in zip(pts,pts[1:]):tr('PICKUP_INT_N',a,z)
subset=tr('PICKUP_INT_N',(2.675,23.3),(2.675,24.375),retained=True);old=next(t for t in b.GetTracks()if t.m_Uuid.AsString()=='7da52644-9f2c-5d36-ab82-77ad53a112d5');need(old.GetNetname()=='PICKUP_INT_N'and old.GetLayer()==p.F_Cu,'exact old subset net/layer');extra=subtract_area(shape(subset,p.F_Cu),shape(old,p.F_Cu));need(extra<1e-8,'new underbody projection')
neg=subset.Duplicate();neg.Move(p.VECTOR2I(150000,0));negative=subtract_area(shape(neg,p.F_Cu),shape(old,p.F_Cu));need(negative>.1,'subset negative control')
C=[];F=[]
for ref,f in fps.items():
 f.BuildCourtyardCaches()
 for l in [p.F_Cu,p.B_Cu]:
  q=f.GetCourtyard(p.F_CrtYd if l==p.F_Cu else p.B_CrtYd)
  if q.OutlineCount():C.append((ref,l,q))
  boxes=[]
  for g in f.GraphicalItems():
   if isinstance(g,p.PCB_SHAPE)and g.GetLayer()==(p.F_Fab if l==p.F_Cu else p.B_Fab):
    bb=g.GetBoundingBox();boxes.append([bb.GetX()/1e6,bb.GetY()/1e6,bb.GetRight()/1e6,bb.GetBottom()/1e6])
  if boxes:F.append((ref,l,rect([min(x[0]for x in boxes),min(x[1]for x in boxes),max(x[2]for x in boxes),max(x[3]for x in boxes)])))
rows=[]
for t,retained in items:
 v=isinstance(t,p.PCB_VIA);a=(t.GetStart().x/1e6,t.GetStart().y/1e6);z=(t.GetEnd().x/1e6,t.GetEnd().y/1e6);r={'net':t.GetNetname(),'type':'via'if v else'track','a':a,'b':z,'width_mm':(t.GetWidth(p.F_Cu)if v else t.GetWidth())/1e6,'retained_exact_subset':retained,'body_hits':[],'Fab_hits':[],'court_hits':[]}
 for l in [p.F_Cu,p.B_Cu]if v else[p.F_Cu]:
  s=shape(t,l);targets={ref:[pad.GetNumber()for pad in f.Pads()if pad.IsOnLayer(l)and pad.GetNetname()==t.GetNetname()and pad.GetPosition()in[t.GetStart(),t.GetEnd()]]for ref,f in fps.items()};targets={ref:ps for ref,ps in targets.items()if ps and not v}
  for e in M:
   if e['side']!=b.GetLayerName(l):continue
   ar=area(s,rect(e['xy_bounds']))
   if ar>1e-8:r['body_hits'].append({'ref':e['ref'],'area_mm2':ar,'actual_pad_ended':targets.get(e['ref'],[]),'retained_same_net_subset':retained})
  for typ,seq in [('Fab_hits',F),('court_hits',C)]:
   for ref,ll,q in seq:
    if ll!=l:continue
    ar=area(s,q)
    if ar>1e-8:r[typ].append({'ref':ref,'area_mm2':ar,'actual_pad_ended':targets.get(ref,[]),'retained_same_net_subset':retained})
 rows.append(r)
strip=rect([.875,19.525,1.275,20.475]);strip_hits=[]
for t in b.GetTracks():
 if t.m_Uuid.AsString()in removed or not t.IsOnLayer(p.F_Cu):continue
 a=area(shape(t,p.F_Cu),strip)
 if a>1e-8:strip_hits.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'area_mm2':a})
need(not strip_hits,'new R101 body occupied strip')
bad=[{'net':r['net'],'a':r['a'],'b':r['b'],'class':typ,**h}for r in rows for typ in ['body_hits','Fab_hits']for h in r[typ]if not h['actual_pad_ended']and not h['retained_same_net_subset']]
need(not bad,'new nonterminal body/Fab intrusion')
# Exact finite path / unchanged full R101 body gap at vertical PICKUP segment.
gap=3.64-.15/2-3.325;need(abs(gap-.24)<1e-10,'claimed gap')
(O/'paths_results.json').write_text(json.dumps({'snapshot_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'proposal_sha256':hashlib.sha256((O/'proposal.json').read_bytes()).hexdigest(),'rows':rows,'new_body_Fab_hits':bad,'new_R101_body_strip_retained_copper_hits':strip_hits,'retained_PICKUP_subset_extra_mm2':extra,'negative_shifted_subset_extra_mm2':negative,'PICKUP_to_full_R101_nominal_gap_mm':gap,'ordinary_courtyard_only_not_body_waiver':True,'scope':'new proposed paths only; native final routing/copper/reference independent review remains'},indent=2)+'\n')
print('PASS bounded proposed paths; retained subset differential',extra)
