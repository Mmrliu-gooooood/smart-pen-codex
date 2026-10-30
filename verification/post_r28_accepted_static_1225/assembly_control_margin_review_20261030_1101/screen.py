from pathlib import Path
import os,json,hashlib,math
os.environ['XDG_CONFIG_HOME']='/tmp/bias1048';import pcbnew as p
O=Path(__file__).resolve().parent;W=O.parent;H=W/'smart_pen_next_20261028/hardware';L=json.load(open(W/'assembly_context_audit_0818_20261030/all103_sync.json'))['rows']
stages=[('tail_courtyard_native_0949','8684d20fa449402ab1309b9af17d1cb64e0e6c4935532a36febaf362b0060f09'),('ground_pair_native_1007','6d05642f7d15ba10c22266e551d72b8457d703bd7328dca79ff5c1c50812b4d9'),('unused_bias_native_1017','2a5400724239f11fe6f589c4f954441deea3c89b0659d1a6292062c99e3e0866'),('control_envelope_native_1051','8312b1d5ec56f0ab4c396cba2b78449e191f06225bf9aa64ea6522fd1c3c68bb')]
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
def polyrect(bb):
 s=p.SHAPE_POLY_SET();s.NewOutline()
 for x,y in [(bb[0],bb[1]),(bb[2],bb[1]),(bb[2],bb[3]),(bb[0],bb[3])]:s.Append(round(x*1e6),round(y*1e6))
 return s
def area(a,b):
 s=p.SHAPE_POLY_SET();s.BooleanIntersection(a,b);return s.Area()/1e12
def fp(f):
 return [f.GetValue(),f.GetFPIDAsString(),f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees(),f.GetLayerName(),f.IsDNP(),sorted([(z.GetNumber(),z.GetPosition().x,z.GetPosition().y,z.GetSize().x,z.GetSize().y,z.GetOrientationDegrees(),str(z.GetLayerSet().FmtHex()),z.GetNetname(),int(z.GetShape()))for z in f.Pads()])]
def zones(b):
 out=[]
 for z in b.Zones():
  sh=z.Outline();lines=[]
  for i in range(sh.OutlineCount()):
   q=sh.Outline(i);lines.append([(q.CPoint(k).x,q.CPoint(k).y)for k in range(q.PointCount())])
   for h in range(sh.HoleCount(i)):
    q=sh.Hole(i,h);lines.append([(q.CPoint(k).x,q.CPoint(k).y)for k in range(q.PointCount())])
  out.append([z.GetNetname(),str(z.GetLayerSet().FmtHex()),z.GetIsRuleArea(),lines])
 return sorted(out,key=str)
def width(t):return t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth()
def ident(t):return [t.GetClass(),t.GetNetname(),t.GetLayerName(),width(t),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None]
def boxbounds(r,e):
 bb=e['projected_current_bounds_not_final_assembly'];v=[bb[0]+7,127-bb[5],bb[3]+7,127-bb[2]]
 if r['ref']=='J202':v[1]-=1.7;v[3]-=1.7
 return v
boards=[];man=[]
for name,expected in stages:
 q=H/name/'native/mainboard_revD.kicad_pcb'
 if sha(q)!=expected:raise RuntimeError('SHA '+name)
 boards.append(p.LoadBoard(str(q)));m=H/name/'manifest.json';j=json.load(open(m))if m.exists()else{};files=j.get('files',{});verified=0
 for rel,v in files.items():
  h=v['sha256']if isinstance(v,dict)else v;f=m.parent/rel
  if sha(f)!=h:raise RuntimeError('manifest '+str(f))
  verified+=1
 man.append({'stage':name,'manifest_sha256':sha(m)if m.exists()else'NOT_YET_FROZEN','files_verified':verified})
base={f.GetReference():fp(f)for f in boards[0].GetFootprints()};Z=zones(boards[0]);out=[]
for idx,(name,expected)in enumerate(stages[1:],1):
 b=boards[idx];old=boards[idx-1];fps={f.GetReference():f for f in b.GetFootprints()}
 if {k:fp(v)for k,v in fps.items()}!=base or len(fps)!=103:raise RuntimeError('FP changed')
 if zones(b)!=Z:raise RuntimeError('zone definition changed')
 edges=[]
 for e in b.GetDrawings():
  if e.GetLayerName()=='Edge.Cuts':edges.extend([(e.GetStart().x/1e6,e.GetStart().y/1e6),(e.GetEnd().x/1e6,e.GetEnd().y/1e6)])
 bounds=[min(x for x,y in edges),min(y for x,y in edges),max(x for x,y in edges),max(y for x,y in edges)]
 if bounds!=[0,-6.5,14,93.3]:raise RuntimeError('outline')
 outline_bounds=list(bounds)
 E=[];F=[];C=[]
 for r in L:
  if r['ref']!='J108':
   for e in r['contexts'][0]['entities']:E.append((r['ref'],e['label'],p.F_Cu if r['current_pose'][3]=='F.Cu'else p.B_Cu,polyrect(boxbounds(r,e)),boxbounds(r,e)))
  if r['ref']in ['U205','C209']:
   dx,dy=(3.7,2.7)if r['ref']=='U205'else(.62,1.52);x,y=r['current_pose'][:2];bb=[x-dx/2,y-dy/2,x+dx/2,y+dy/2];E.append((r['ref'],'package_plus_assumed_solder',p.F_Cu,polyrect(bb),bb))
 for ref,f in fps.items():
  f.BuildCourtyardCaches()
  for layer in [p.F_CrtYd,p.B_CrtYd]:
   q=f.GetCourtyard(layer)
   if q.OutlineCount():C.append((ref,layer,q))
  for fl in [p.F_Fab,p.B_Fab]:
   bounds=[]
   for g in f.GraphicalItems():
    if g.GetLayer()==fl and isinstance(g,p.PCB_SHAPE):
     bb=g.GetBoundingBox();bounds.append([bb.GetX()/1e6,bb.GetY()/1e6,bb.GetRight()/1e6,bb.GetBottom()/1e6])
   if bounds:F.append((ref,fl,polyrect([min(v[0]for v in bounds),min(v[1]for v in bounds),max(v[2]for v in bounds),max(v[3]for v in bounds)])))

 targets=json.load(open(H/name/'selected_final.json')).get('targets',{})if name!='ground_pair_native_1007'else{'GND':['R219.2','R226.2','R229.2','U202.8']}
 allowed={n:{r.split('.')[0]for r in rr}for n,rr in targets.items()}
 oldset={str(ident(t))for t in old.GetTracks()};rows=[]
 for t in b.GetTracks():
  if str(ident(t))in oldset:continue
  via=isinstance(t,p.PCB_VIA);layers=[p.F_Cu,p.B_Cu]if via else[t.GetLayer()]
  if not via and t.GetLayer()not in [p.F_Cu,p.B_Cu]:raise RuntimeError('unexpected inner new track')
  rr={'type':'via'if via else'track','net':t.GetNetname(),'start':[t.GetStart().x/1e6,t.GetStart().y/1e6],'end':[t.GetEnd().x/1e6,t.GetEnd().y/1e6],'width':width(t)/1e6,'layer':t.GetLayerName(),'envelope_hits':[],'fab_bbox_hits':[],'courtyard_hits':[],'via_near_envelopes':[]}
  for layer in layers:
   s=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(s,layer,0,50,p.ERROR_OUTSIDE)
   for ref,label,el,shape,bb in E:
    if el!=layer:continue
    v=area(s,shape)
    if v>1e-8:rr['envelope_hits'].append({'ref':ref,'entity':label,'side':b.GetLayerName(layer),'area_mm2':v,'declared_target_ref':ref in allowed.get(t.GetNetname(),set())})
    if via:
     x,y=rr['start'];gap=math.hypot(max(bb[0]-x,0,x-bb[2]),max(bb[1]-y,0,y-bb[3]))-rr['width']/2
     if gap<.6:rr['via_near_envelopes'].append({'ref':ref,'entity':label,'side':b.GetLayerName(layer),'signed_gap_mm':gap})
   for ref,cl,shape in C:
    if cl!=(p.F_CrtYd if layer==p.F_Cu else p.B_CrtYd):continue
    v=area(s,shape)
    if v>1e-8:rr['courtyard_hits'].append({'ref':ref,'side':b.GetLayerName(layer),'area_mm2':v,'declared_target_ref':ref in allowed.get(t.GetNetname(),set())})
   for ref,fl,shape in F:
    if fl!=(p.F_Fab if layer==p.F_Cu else p.B_Fab):continue
    v=area(s,shape)
    if v>1e-8:rr['fab_bbox_hits'].append({'ref':ref,'side':b.GetLayerName(layer),'area_mm2':v,'declared_target_ref':ref in allowed.get(t.GetNetname(),set())})
  rows.append(rr)
 result={'stage':name,'sha256':expected,'parent_sha256':stages[idx-1][1],'all103_contract_equal':True,'reference_zone_definitions_equal':True,'outline':outline_bounds,'declared_target_refs':{k:sorted(v)for k,v in allowed.items()},'new_tracks':sum(r['type']=='track'for r in rows),'new_vias':sum(r['type']=='via'for r in rows),'rows':rows};out.append(result);print(name,result['new_tracks'],result['new_vias'],'unrelatedEnvelope',[(r['net'],h['ref'])for r in rows for h in r['envelope_hits']if not h['declared_target_ref']],flush=True);print('vias',[(r['start'],r['envelope_hits'],r['courtyard_hits'],r['via_near_envelopes'])for r in rows if r['type']=='via'],flush=True)
(O/'results.json').write_text(json.dumps({'stages':out,'manifests':man,'numeric_geometry':'KiCad ERROR_OUTSIDE,50nm polygon chord approximation; finite physical width; area threshold1e-8mm2','scope':'retained full budgets and provisional U205/C209; native Fab graphical bounding boxes conservative; courtyard geometry. Projection overlap is not fabricated protrusion or process pass. J108 no fitted body, explicit mixed-side operation qualification still open.'},indent=2)+'\n')
