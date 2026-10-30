"""V2: replay frozen V1 pixels plus independent exact fractional phase sweep."""
from pathlib import Path
# Reuse only our independent setup/raster/oracle functions; bind to new snapshot.
source=(Path(__file__).parent/'review.py').read_text().split('# Original API regression')[0]
source=source.replace("P=Path(__file__).resolve().parent;ROOT=P.parent;SNAP=P/'snapshot'","P=Path(__file__).resolve().parent/'v2';ROOT=P.parent.parent;SNAP=P/'snapshot'")
exec(source)
V1=P.parent; previous=json.loads((V1/'results.json').read_text());replay=[]
for old in previous:
 im=np.frombuffer((V1/old['fixture']).read_bytes().split(b'\n',3)[3],np.uint8).reshape(200,200);cfg={'wrong_section':(710,1000,11,3),'excluded_x':(100,1000,10,2),'excluded_y':(710,100,10,2),'invalid_bounds':(5,1000,10,2)}.get(old['kind'],(710,1000,10,2));r,o=call(im,cfg);r.update(kind=old['kind'],fixture='../'+old['fixture'],v1_status=old['status'])
 if old['kind']=='positive':check_truth(r,o,old['fov'],old['angle'],old['cx'],old['cy'])
 if old['kind']=='edge_ink':r['depth']=old['depth'];check_truth(r,o,6,0,320.317,550.681)
 replay.append(r)
(P/'replay_v1.json').write_text(json.dumps(replay,indent=2))
phase=[]
for fov in (5,6,7):
 for fx in (0,.125,.5,.875):
  for fy in (0,.125,.5,.875):
   cx,cy=330+fx,560+fy;im=render(fov,0,cx,cy);r,o=call(im);r.update(fov=fov,fx=fx,fy=fy);check_truth(r,o,fov,0,cx,cy);phase.append(r)
(P/'phase.json').write_text(json.dumps(phase,indent=2))
# Pixel-located empty border neighborhood; test thin clipped-dot-like components.
good=render(6,0,320.317,550.681);locations=[y for y in range(60,140) if np.min(good[y-2:y+4,52:56])>150];assert locations;y=locations[len(locations)//2];fragments=[]
for label,coords in [('sliver1x4',[(52,y+j) for j in range(4)]),('half_disk',[(52+i,y+j) for i in range(3) for j in range(-2,3) if i*i+j*j<=4]),('corner1x1',[(52,52)]),('corner1x4',[(52,52+j) for j in range(4)]),('corner4x1',[(52+j,52) for j in range(4)])]:
 im=good.copy()
 for x,yy in coords:im[yy,x]=30
 r,o=call(im);r['kind']=label;check_truth(r,o,6,0,320.317,550.681);name=label+'.pgm';(P/name).write_bytes(b'P5\n200 200\n255\n'+im.tobytes());r['fixture']=name;fragments.append(r)
(P/'fragments.json').write_text(json.dumps(fragments,indent=2));summary={'replay_count':len(replay),'positive_status':dict(Counter(r['status'] for r in replay if r['kind']=='positive')),'lost_v1_successes':[r['fixture'] for r in replay if r['v1_status']==0 and r['status']!=0],'edge_ink':[(r['depth'],r['status']) for r in replay if r['kind']=='edge_ink'],'phase_status':dict(Counter(r['status'] for r in phase)),'fragments':[(r['kind'],r['status']) for r in fragments]};(P/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
