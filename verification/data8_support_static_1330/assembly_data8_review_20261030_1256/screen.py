from pathlib import Path
import os,json,hashlib,math
os.environ['XDG_CONFIG_HOME']='/tmp/bias1048';import pcbnew as p
O=Path(__file__).resolve().parent;W=O.parent;H=W/'smart_pen_next_20261028/hardware';L=json.load(open(W/'assembly_context_audit_0818_20261030/all103_sync.json'))['rows']
stages=[('sccb_local_reference_1216','dcbd2e6501c8294ece5ecf7b41ffcc86ccc7f58f7cb54ececfdf24962a50f697'),('data_bias_relocate_1242','4d7d95d253b3c8c994a7f2c4c628087346c271ea290c69aa511ea9a1cb8eadad')]
MOVES={'R240':(11,70.5,180),'R241':(11.85,73.35,90),'C207':(10.85,65,-90),'R210':(10.5,28,0),'R217':(2.5,29,-90)}
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
def declared_refs(net,layer,start,end):
 if net.startswith('CAM_D')and net[-1]in '01234567':
  refs={'U201','R'+str(210+int(net[-1]))};ends={tuple(start),tuple(end)}
  return {ref for ref in refs if any((z.GetPosition().x/1e6,z.GetPosition().y/1e6)in ends and z.GetNetname()==net for z in fps[ref].Pads())}
 if net=='GND'and layer=='F.Cu':
  pts={tuple(start),tuple(end)}
  if pts=={(11.325,28.0),(11.325,26.8)}:return {'R210'}
  if pts=={(2.5,29.51),(3.375,29.5)}:return {'R217'}
 return set()

def declared_court_continuation(net,layer,start,end,ref):
 cases={('CAM_D5','F.Cu',(4.75,28.8),(4.85,29.075),'R215'),('CAM_D7','F.Cu',(2.95,28.95),(3.55,28.975),'R217')}
 return (net,layer,tuple(start),tuple(end),ref)in cases or(net,layer,tuple(end),tuple(start),ref)in cases

def boxbounds(r,e):
 bb=e['projected_current_bounds_not_final_assembly'];v=[bb[0]+7,127-bb[5],bb[3]+7,127-bb[2]]
 if r['ref']=='J202':v[1]-=1.7;v[3]-=1.7
 if r['ref']in MOVES:
  nx,ny,ang=MOVES[r['ref']];ox,oy,oa=r['current_pose'][:3];a=math.radians(ang-oa);pts=[]
  for x in [v[0],v[2]]:
   for y in [v[1],v[3]]:
    dx,dy=x-ox,y-oy;pts.append((nx+dx*math.cos(a)+dy*math.sin(a),ny-dx*math.sin(a)+dy*math.cos(a)))
  v=[min(x for x,y in pts),min(y for x,y in pts),max(x for x,y in pts),max(y for x,y in pts)]
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
expect=p.LoadBoard(str(H/stages[0][0]/'native/mainboard_revD.kicad_pcb'))
for f in expect.GetFootprints():
 if f.GetReference()in MOVES:
  x,y,a=MOVES[f.GetReference()];f.SetPosition(p.VECTOR2I(round(x*1e6),round(y*1e6)));f.SetOrientationDegrees(a)
base={f.GetReference():fp(f)for f in expect.GetFootprints()};Z=zones(boards[0]);out=[]
for idx,(name,expected)in enumerate(stages[1:],1):
 b=boards[idx];old=boards[idx-1];fps={f.GetReference():f for f in b.GetFootprints()}
 if {k:fp(v)for k,v in fps.items()}!=base or len(fps)!=103:raise RuntimeError('FP changed')
 zone_same=zones(b)==Z
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
  if not via and t.GetLayer()not in [p.F_Cu,p.B_Cu]:layers=[]
  rr={'type':'via'if via else'track','net':t.GetNetname(),'start':[t.GetStart().x/1e6,t.GetStart().y/1e6],'end':[t.GetEnd().x/1e6,t.GetEnd().y/1e6],'width':width(t)/1e6,'layer':t.GetLayerName(),'envelope_hits':[],'fab_bbox_hits':[],'courtyard_hits':[],'via_near_envelopes':[]}
  rr['segment_declared_refs']=sorted(declared_refs(rr['net'],rr['layer'],rr['start'],rr['end']))
  for layer in layers:
   s=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(s,layer,0,50,p.ERROR_OUTSIDE)
   for ref,label,el,shape,bb in E:
    if el!=layer:continue
    v=area(s,shape)
    if v>1e-8:rr['envelope_hits'].append({'ref':ref,'entity':label,'side':b.GetLayerName(layer),'area_mm2':v,'declared_target_ref':ref in rr['segment_declared_refs']})
    if via:
     x,y=rr['start'];gap=math.hypot(max(bb[0]-x,0,x-bb[2]),max(bb[1]-y,0,y-bb[3]))-rr['width']/2
     if gap<.6:rr['via_near_envelopes'].append({'ref':ref,'entity':label,'side':b.GetLayerName(layer),'signed_gap_mm':gap})
   for ref,cl,shape in C:
    if cl!=(p.F_CrtYd if layer==p.F_Cu else p.B_CrtYd):continue
    v=area(s,shape)
    if v>1e-8:rr['courtyard_hits'].append({'ref':ref,'side':b.GetLayerName(layer),'area_mm2':v,'declared_target_ref':ref in rr['segment_declared_refs'] or declared_court_continuation(rr['net'],rr['layer'],rr['start'],rr['end'],ref),'exact_courtyard_only_continuation':declared_court_continuation(rr['net'],rr['layer'],rr['start'],rr['end'],ref)})
   for ref,fl,shape in F:
    if fl!=(p.F_Fab if layer==p.F_Cu else p.B_Fab):continue
    v=area(s,shape)
    if v>1e-8:rr['fab_bbox_hits'].append({'ref':ref,'side':b.GetLayerName(layer),'area_mm2':v,'declared_target_ref':ref in rr['segment_declared_refs']})
  rows.append(rr)
 for rr in rows:
  for h in rr['courtyard_hits']:
   if h.get('exact_courtyard_only_continuation'):
    linked=[z for z in rows if z['net']==rr['net']and z['layer']==rr['layer']and h['ref']in z['segment_declared_refs']and {tuple(rr['start']),tuple(rr['end'])}&{tuple(z['start']),tuple(z['end'])}]
    if len(linked)!=1:raise RuntimeError('courtyard continuation not connected to unique pad-ended segment')
    h['directly_connected_pad_ended_segment']=[linked[0]['start'],linked[0]['end']]
 result={'static_entity_count':len(E),'stage':name,'sha256':expected,'parent_sha256':stages[idx-1][1],'all103_contract_equal':True,'reference_zone_definitions_equal':zone_same,'declared_internal_patch':json.load(open(H/name/'selected_final.json')).get('plane_patch'), 'expected_moved_poses':MOVES,'outline':outline_bounds,'declared_target_refs':{k:sorted(v)for k,v in allowed.items()},'new_tracks':sum(r['type']=='track'for r in rows),'new_outer_tracks':sum(r['type']=='track'and r['layer']in ['F.Cu','B.Cu']for r in rows),'new_inner_tracks':sum(r['type']=='track'and r['layer']not in ['F.Cu','B.Cu']for r in rows),'new_vias':sum(r['type']=='via'for r in rows),'rows':rows};out.append(result);print(name,result['new_tracks'],result['new_vias'],'unrelatedEnvelope',[(r['net'],h['ref'])for r in rows for h in r['envelope_hits']if not h['declared_target_ref']],flush=True);print('vias',[(r['start'],r['envelope_hits'],r['courtyard_hits'],r['via_near_envelopes'])for r in rows if r['type']=='via'],flush=True)
(O/'results.json').write_text(json.dumps({'stages':out,'manifests':man,'numeric_geometry':'KiCad ERROR_OUTSIDE,50nm polygon chord approximation; finite physical width; area threshold1e-8mm2','scope':'retained full budgets and provisional U205/C209; native Fab graphical bounding boxes conservative; courtyard geometry. Projection overlap is not fabricated protrusion or process pass. J108 no fitted body, explicit mixed-side operation qualification still open.'},indent=2)+'\n')
