# NEW Oct31 independent helper, based only on restored4d7d and NEW diagnostic bytes.
from pathlib import Path
import os,json,hashlib,math
os.makedirs('/tmp/new_mech0056',exist_ok=True);os.environ['XDG_CONFIG_HOME']='/tmp/new_mech0056';import pcbnew as p
O=Path(__file__).resolve().parent;W=O.parent;B=W/'reconstruction_sccb_margin_mechanics_20261031_0214/selected_native.kicad_pcb';S=O/'selected_native.kicad_pcb';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def need(v,msg):
 if not v:raise RuntimeError(msg)
need(sha(B)=='c698310e125eb335dda4336a354a6e19b747d89fa513ca8afe8e94023bef0855','restored native');need(sha(S)=='d8550195b14521806a14654c4bdeba0a6d533b0aa536b473919481da2b9d6e5b','NEW native')
base=p.LoadBoard(str(B));b=p.LoadBoard(str(S));env=json.load(open(O/'proposed_full104.json'));M=env['all_static_rectangles'];need(len(M)==104,'full104')
def ident(t):return [t.GetClass(),t.GetNetname(),t.GetLayerName(),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None]
def fp(f):return [f.GetValue(),f.GetFPIDAsString(),f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees(),f.GetLayerName(),f.IsDNP(),sorted((z.GetNumber(),z.GetPosition().x,z.GetPosition().y,z.GetSize().x,z.GetSize().y,z.GetOrientationDegrees(),str(z.GetLayerSet().FmtHex()),z.GetNetname(),int(z.GetShape()))for z in f.Pads())]
fps={f.GetReference():f for f in b.GetFootprints()};oldfps={f.GetReference():f for f in base.GetFootprints()};need(len(fps)==103,'103 contracts')
for ref,f in fps.items():
 oldf=oldfps[ref]
 if ref in ['R230','R219']:
  x,y,angle,layer={'R230':(11.1,34.25,90,p.F_Cu),'R219':(6.2,39.5,0,p.B_Cu)}[ref]
  oldf.SetOrientationDegrees(angle);oldf.SetPosition(p.VECTOR2I(round(x*1e6),round(y*1e6)));need(f.GetLayer()==layer,'side preserved')
 need(fp(f)==fp(oldf),'exact rigid contract '+ref)

old={t.m_Uuid.AsString():t for t in base.GetTracks()};new={t.m_Uuid.AsString():t for t in b.GetTracks()};mat={'added':sorted(set(new)-set(old)),'removed':sorted(set(old)-set(new))};(O/'native_derived_delta.json').write_text(json.dumps(mat,indent=2)+'\n');need(len(new)==len(list(b.GetTracks())),'unique copper UUIDs');need(set(new)-set(old)==set(mat['added'])and set(old)-set(new)==set(mat['removed']),'exact added/removed');need(all(ident(t)==ident(new[u])for u,t in old.items()if u in new),'retained copper')
def poly(pts):
 q=p.SHAPE_POLY_SET();q.NewOutline()
 for x,y in pts:q.Append(round(x*1e6),round(y*1e6))
 return q
def rect(bb):return poly([(bb[0],bb[1]),(bb[2],bb[1]),(bb[2],bb[3]),(bb[0],bb[3])])
def area(a,z):
 q=p.SHAPE_POLY_SET();q.BooleanIntersection(a,z);return q.Area()/1e12
def pd(a,c,d):
 dx,dy=d[0]-c[0],d[1]-c[1];t=max(0,min(1,((a[0]-c[0])*dx+(a[1]-c[1])*dy)/(dx*dx+dy*dy)))if dx or dy else 0;return math.hypot(a[0]-c[0]-t*dx,a[1]-c[1]-t*dy)
def gap(a,z,pts,rad):return min(min(pd(a,c,d),pd(z,c,d),pd(c,a,z),pd(d,a,z))for c,d in zip(pts,pts[1:]+pts[:1]))-rad
outline=[(0,-6.5),(12,-6.5),(12,6),(14,6),(14,93.3),(0,93.3)];boardpoly=poly(outline)
def edges(bb):return sorted(sorted([(e.GetStart().x,e.GetStart().y),(e.GetEnd().x,e.GetEnd().y)])for e in bb.GetDrawings()if e.GetLayer()==p.Edge_Cuts)
need(edges(base)==edges(b)and len(edges(b))==6,'native outline unchanged');need(b.GetDesignSettings().GetBoardThickness()==base.GetDesignSettings().GetBoardThickness(),'native thickness')
C=[];F=[]
for ref,f in fps.items():
 f.BuildCourtyardCaches()
 for layer in [p.F_Cu,p.B_Cu]:
  court=f.GetCourtyard(p.F_CrtYd if layer==p.F_Cu else p.B_CrtYd)
  if court.OutlineCount():C.append((ref,layer,court))
  boxes=[]
  for g in f.GraphicalItems():
   if isinstance(g,p.PCB_SHAPE)and g.GetLayer()==(p.F_Fab if layer==p.F_Cu else p.B_Fab):
    bb=g.GetBoundingBox();boxes.append([bb.GetX()/1e6,bb.GetY()/1e6,bb.GetRight()/1e6,bb.GetBottom()/1e6])
  if boxes:F.append((ref,layer,rect([min(x[0]for x in boxes),min(x[1]for x in boxes),max(x[2]for x in boxes),max(x[3]for x in boxes)])))
rows=[]
for u in sorted(mat['added']):
 t=new[u];via=isinstance(t,p.PCB_VIA);a=(t.GetStart().x/1e6,t.GetStart().y/1e6);z=(t.GetEnd().x/1e6,t.GetEnd().y/1e6);width=(t.GetWidth(p.F_Cu)if via else t.GetWidth())/1e6;layers=[p.F_Cu,p.B_Cu]if via else[t.GetLayer()]if t.GetLayer()in[p.F_Cu,p.B_Cu]else[]
 r={'uuid':u,'type':'via'if via else'track','net':t.GetNetname(),'layer':t.GetLayerName(),'a':a,'b':z,'width_mm':width,'body_hits':[],'Fab_bbox_hits':[],'courtyard_hits':[],'near_courts':[],'near_full':[]}
 s=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(s,p.F_Cu if via else t.GetLayer(),0,50,p.ERROR_OUTSIDE);outside=p.SHAPE_POLY_SET();outside.BooleanSubtract(s,boardpoly);need(outside.Area()/1e12<1e-8,'outside actual outline');r['outline_gap_mm']=gap(a,z,outline,width/2)
 for layer in layers:
  s=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(s,layer,0,50,p.ERROR_OUTSIDE)
  terminals={ref:[pad.GetNumber()for pad in f.Pads()if pad.IsOnLayer(layer)and pad.GetNetname()==r['net']and (pad.GetPosition().x/1e6,pad.GetPosition().y/1e6)in[a,z]]for ref,f in fps.items()};terminals={ref:ps for ref,ps in terminals.items()if ps and not via}
  for e in M:
   if e['side']!=b.GetLayerName(layer):continue
   v=area(s,rect(e['xy_bounds']))
   if v>1e-8:r['body_hits'].append({'ref':e['ref'],'entity':e['entity'],'side':e['side'],'area_mm2':v,'actual_pad_ended':terminals.get(e['ref'],[])})
   bb=e['xy_bounds'];d=gap(a,z,[(bb[0],bb[1]),(bb[2],bb[1]),(bb[2],bb[3]),(bb[0],bb[3])],width/2)
   if via and d<.6:r['near_full'].append({'ref':e['ref'],'side':e['side'],'gap_mm_nonintersecting_only':d,'overlap_mm2':v})
  for ref,l,q in F:
   if l!=layer:continue
   v=area(s,q)
   if v>1e-8:r['Fab_bbox_hits'].append({'ref':ref,'side':b.GetLayerName(layer),'area_mm2':v,'actual_pad_ended':terminals.get(ref,[])})
  for ref,l,q in C:
   if l!=layer:continue
   v=area(s,q)
   if v>1e-8:r['courtyard_hits'].append({'ref':ref,'side':b.GetLayerName(layer),'area_mm2':v,'actual_pad_ended':terminals.get(ref,[]),'classification':'COURTYARD_PROJECTION_ONLY_NOT_A_BODY_WAIVER'})
   if via:
    for i in range(q.OutlineCount()):
     c=q.Outline(i);pts=[(c.CPoint(k).x/1e6,c.CPoint(k).y/1e6)for k in range(c.PointCount())];d=gap(a,z,pts,width/2)
     if d<.5:r['near_courts'].append({'ref':ref,'side':b.GetLayerName(layer),'gap_mm_nonintersecting_only':d,'overlap_mm2':v})
 rows.append(r)
# Only this exact PICKUP subset can inherit old underbody projection.
for r in rows:
 if r['type']=='track'and r['net']=='PICKUP_INT_N'and r['layer']=='F.Cu'and {tuple(r['a']),tuple(r['b'])}=={(2.675,23.3),(2.675,24.375)}:
  t=new[r['uuid']];old_t=old.get('7da52644-9f2c-5d36-ab82-77ad53a112d5');need(old_t is not None and old_t.GetNetname()=='PICKUP_INT_N','old PICKUP identity');s1=p.SHAPE_POLY_SET();s2=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(s1,p.F_Cu,0,50,p.ERROR_OUTSIDE);old_t.TransformShapeToPolygon(s2,p.F_Cu,0,50,p.ERROR_OUTSIDE);diff=p.SHAPE_POLY_SET();diff.BooleanSubtract(s1,s2);need(diff.Area()/1e12<1e-8,'retained subset adds area');r['exact_retained_subset_extra_mm2']=diff.Area()/1e12
  for k in ['body_hits','Fab_bbox_hits']:
   for h in r[k]:h['exact_old_subset_no_added_projection']=True
body_bad=[{'uuid':r['uuid'],'net':r['net'],'kind':k,**h}for r in rows for k in ['body_hits','Fab_bbox_hits']for h in r[k]if not h['actual_pad_ended']and not h.get('exact_old_subset_no_added_projection')]
out={'status':'NEW_DIAGNOSTIC_GEOMETRY_ONLY_NOFAB_NOPOWER','pcb_sha256':sha(S),'parent_sha256':sha(B),'mask_sha256':sha(O/'proposed_full104.json'),'all103_contracts_only_two_exact_rigid_changes':True,'all104_full_budgets_retained':True,'native_outline_thickness_unchanged':True,'undeleted_copper_unchanged':True,'new_tracks':sum(r['type']=='track'for r in rows),'new_outer_tracks':sum(r['type']=='track'and r['layer']in['F.Cu','B.Cu']for r in rows),'new_vias':sum(r['type']=='via'for r in rows),'removed_count':len(mat['removed']),'unqualified_body_Fab_hits':body_bad,'rows':rows};(O/'results.json').write_text(json.dumps(out,indent=2)+'\n');print('COUNTS',out['new_tracks'],out['new_outer_tracks'],out['new_vias'],'BODY_BAD',body_bad)
