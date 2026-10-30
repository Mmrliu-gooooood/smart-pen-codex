from pathlib import Path
import json,hashlib,math,os
os.environ['XDG_CONFIG_HOME']='/tmp/masks1228';import pcbnew as p
O=Path(__file__).resolve().parent;W=O.parent;src=W/'smart_pen_next_20261028/hardware/sccb_local_reference_1216/native/mainboard_revD.kicad_pcb';sha=hashlib.sha256(src.read_bytes()).hexdigest()
if sha!='dcbd2e6501c8294ece5ecf7b41ffcc86ccc7f58f7cb54ececfdf24962a50f697':raise RuntimeError('basis changed')
b=p.LoadBoard(str(src));fps={f.GetReference():f for f in b.GetFootprints()};L=json.load(open(W/'assembly_context_audit_0818_20261030/all103_sync.json'))['rows'];out=[];ops=[]
for r in L:
 f=fps[r['ref']];x,y,a=f.GetPosition().x/1e6,f.GetPosition().y/1e6,f.GetOrientationDegrees();ox,oy,oa=r['current_pose'][:3];ang=math.radians(a-oa)
 if r['ref']!='J108':
  for e in r['contexts'][0]['entities']:
   z=e['projected_current_bounds_not_final_assembly'];bb=[z[0]+7,127-z[5],z[3]+7,127-z[2]];pts=[]
   for xx in [bb[0],bb[2]]:
    for yy in [bb[1],bb[3]]:
     dx,dy=xx-ox,yy-oy;pts.append((x+dx*math.cos(ang)+dy*math.sin(ang),y-dx*math.sin(ang)+dy*math.cos(ang)))
   q=[min(xx for xx,yy in pts),min(yy for xx,yy in pts),max(xx for xx,yy in pts),max(yy for xx,yy in pts)];out.append({'ref':r['ref'],'side':f.GetLayerName(),'entity':e['label'],'xy_bounds':q,'height':z[4]-z[1],'basis':e['basis']})
 if r['ref']in ['U205','C209']:
  dx,dy,h=(3.7,2.7,1.25)if r['ref']=='U205'else(.62,1.52,.7);out.append({'ref':r['ref'],'side':'F.Cu','entity':'provisional_package_plus_assumed_mount','xy_bounds':[x-dx/2,y-dy/2,x+dx/2,y+dy/2],'height':h,'basis':'unchanged provisional official package+assumed .15mm mounting, not manufactured assembly'})
 if r['ref']in ['J108','J104','JP201','JP202','C106','C107']:
  f.BuildCourtyardCaches();courts=[]
  for lay in [p.F_CrtYd,p.B_CrtYd]:
   s=f.GetCourtyard(lay)
   for i in range(s.OutlineCount()):
    c=s.Outline(i);courts.append({'side':b.GetLayerName(lay),'vertices':[[c.CPoint(k).x/1e6,c.CPoint(k).y/1e6]for k in range(c.PointCount())]})
  ops.append({'ref':r['ref'],'DNP':f.IsDNP(),'pads':[{'num':z.GetNumber(),'xy':[z.GetPosition().x/1e6,z.GetPosition().y/1e6],'size':[z.GetSize().x/1e6,z.GetSize().y/1e6],'sides':[b.GetLayerName(lay)for lay in [p.F_Cu,p.B_Cu]if z.IsOnLayer(lay)]}for z in f.Pads()],'native_courtyard_polygons':courts,'status':'operation unqualified, no invented fitted body or zero access requirement'})
result={'basis_sha256':sha,'rectangles':[r for r in out if r['xy_bounds'][1]<=38 and r['xy_bounds'][3]>=20],'one_mm_neighbor_halo':[r for r in out if r['xy_bounds'][1]<=39 and r['xy_bounds'][3]>=19 and not(r['xy_bounds'][1]<=38 and r['xy_bounds'][3]>=20)],'all_static_rectangles':out,'unqualified_operations':ops,'warning':'Finite copper width/via radius must be tested against full rectangles and ALL actual native copper/courtyards. J108 phantom Fbody omitted; true mixed-side service pads/courtyards included separately. No physical-process qualification.'};(O/'route_masks_y20_38.json').write_text(json.dumps(result,indent=2)+'\n');print(len(result['rectangles']),len(out))
