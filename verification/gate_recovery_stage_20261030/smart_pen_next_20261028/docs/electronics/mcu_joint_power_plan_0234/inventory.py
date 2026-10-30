import geometry as q,json
p=q.p
out=[]
for t in q.old:
 a=t.GetStart();b=t.GetEnd()
 if t.GetNetname()in ['CHIP_EN','BOOT_N'] or (min(a.x,b.x)<3500000 and min(a.y,b.y)<11000000):
  out.append(dict(uuid=q.uid(t),type=t.GetClass(),net=t.GetNetname(),layer=q.b.GetLayerName(t.GetLayer()),start=[a.x/1e6,a.y/1e6],end=[b.x/1e6,b.y/1e6],width=(t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth())/1e6))
pads=[]
for n,t in q.pm.items():
 a=t.GetPosition()
 if a.x<4500000 and a.y<11500000:pads.append(dict(name=n,net=t.GetNetname(),xy=q.xy(t),size=[t.GetSize().x/1e6,t.GetSize().y/1e6],layer=q.b.GetLayerName(t.GetLayer())))
print(json.dumps(dict(objects=out,pads=pads),indent=2))
