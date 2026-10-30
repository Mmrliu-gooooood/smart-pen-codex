from pathlib import Path
import pcbnew as p,json,math
import numpy as np
D=Path(__file__).resolve().parent;S=D.parent/'rf_width14_selected_board_candidate';b=p.LoadBoard(str(S/'mainboard_revD.kicad_pcb'));items=[]
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):
  a=(t.GetPosition().x/1e6,t.GetPosition().y/1e6);bb=a;rad=t.GetWidth(p.B_Cu)/2e6+.20
 elif t.GetLayer()==p.B_Cu:
  a=(t.GetStart().x/1e6,t.GetStart().y/1e6);bb=(t.GetEnd().x/1e6,t.GetEnd().y/1e6);rad=t.GetWidth()/2e6+.20
 else:continue
 items.append((a,bb,rad,t.GetNetname()))
for f in b.GetFootprints():
 for pad in f.Pads():
  if p.B_Cu not in pad.GetLayerSet().Seq():continue
  r=pad.GetBoundingBox();x1,y1,x2,y2=r.GetLeft()/1e6,r.GetTop()/1e6,r.GetRight()/1e6,r.GetBottom()/1e6
  # enclosing circle is conservative for existing pads
  a=((x1+x2)/2,(y1+y2)/2);rad=math.hypot(x2-x1,y2-y1)/2+.20;items.append((a,a,rad,pad.GetNetname()))
boxes=np.array([(min(a[0],b[0])-r,min(a[1],b[1])-r,max(a[0],b[0])+r,max(a[1],b[1])+r) for a,b,r,n in items])
def pointseg(a,b,c):
 vx=c[0]-b[0];vy=c[1]-b[1];ss=vx*vx+vy*vy
 t=max(0,min(1,((a[0]-b[0])*vx+(a[1]-b[1])*vy)/ss)) if ss else 0
 return math.hypot(a[0]-b[0]-t*vx,a[1]-b[1]-t*vy)
def ccw(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def segdist(a,b,c,d):
 if ccw(a,b,c)*ccw(a,b,d)<=0 and ccw(c,d,a)*ccw(c,d,b)<=0 and max(min(a[0],b[0]),min(c[0],d[0]))<=min(max(a[0],b[0]),max(c[0],d[0])) and max(min(a[1],b[1]),min(c[1],d[1]))<=min(max(a[1],b[1]),max(c[1],d[1])):return 0
 return min(pointseg(a,c,d),pointseg(b,c,d),pointseg(c,a,b),pointseg(d,a,b))
def blocked(poly,net):
 x1,y1,x2,y2=poly
 ids=np.where((boxes[:,0]<=x2)&(boxes[:,2]>=x1)&(boxes[:,1]<=y2)&(boxes[:,3]>=y1))[0]
 corners=[(x1,y1),(x2,y1),(x2,y2),(x1,y2)]
 for i in ids:
  a,b,rad,n=items[i]
  if n==net:continue
  if any(x1<=z[0]<=x2 and y1<=z[1]<=y2 for z in [a,b]):return True
  if min(segdist(a,b,corners[j],corners[(j+1)%4]) for j in range(4))<=rad:return True
 return False
c=json.loads((D.parent/'physical_interface_study/pin_contract.json').read_text());results={}
for ref,window in {'J105':(1.5,10,45,87),'J110':(1.5,8.5,45,87)}.items():
 v=c['ports'][ref];possible=[]
 for xx in range(round(window[0]*4),round(window[1]*4)+1):
  for yy in range(round(window[2]*4),round(window[3]*4)+1):
   x=xx/4;y=yy/4;good=True;polys=[]
   for i,net in enumerate(v['nets']):
    # B flip(False) mirrors x, keeps y.
    px=x+i*2.4;py=y
    poly=(px-.5,py-.5,px+.5,py+.5) if ref=='J104' else (px-.7,py-.9,px+.7,py+.9)
    if poly[0]<.3 or poly[2]>13.7 or poly[3]>94.7 or blocked(poly,net):good=False;break
    polys.append(poly)
   if good:possible.append({'origin':[x,y],'distance_from_proposal':math.hypot(x-7,y-window[2])})
 results[ref]=sorted(possible,key=lambda z:z['distance_from_proposal'])[:10]
print(json.dumps(results,indent=2));(D/'horizontal_placement_search.json').write_text(json.dumps(results,indent=2)+'\n')
