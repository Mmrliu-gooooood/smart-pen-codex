from pathlib import Path
import pcbnew as p,json,math
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D.parent/'mainboard_href3_candidate/mainboard_revD.kicad_pcb'));S=150;X0=0;Y0=40;im=Image.new('RGB',(1800,1650),'#18212b');dr=ImageDraw.Draw(im)
def xy(v):return ((p.ToMM(v.x)-X0)*S,(p.ToMM(v.y)-Y0)*S)
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):
  x,y=xy(t.GetPosition());r=p.ToMM(t.GetWidth(p.B_Cu))/2*S;dr.ellipse((x-r,y-r,x+r,y+r),outline='#e2ab51',width=2);r=p.ToMM(t.GetDrillValue())/2*S;dr.ellipse((x-r,y-r,x+r,y+r),fill='#18212b')
 elif t.GetLayer()==p.B_Cu:dr.line([xy(t.GetStart()),xy(t.GetEnd())],fill='#64a6ff',width=max(1,round(p.ToMM(t.GetWidth())*S)))
boxes={}
for f in b.GetFootprints():
 if not f.IsOnLayer(p.B_Cu):continue
 for a in f.Pads():
  if a.IsOnLayer(p.B_Cu):bb=a.GetBoundingBox();dr.rectangle([xy(bb.GetOrigin()),xy(bb.GetEnd())],fill='#d3ae64')
 bs=[]
 for t in f.GraphicalItems():
  if t.GetLayer()==p.B_CrtYd:
   bs.append(t.GetBoundingBox())
   if t.GetClass()=='PCB_SHAPE':dr.line([xy(t.GetStart()),xy(t.GetEnd())],fill='#69dfb4',width=2)
 dr.text(xy(f.GetPosition()),f.GetReference(),fill='white',stroke_width=1)
 if bs:boxes[f.GetReference()]=[min(p.ToMM(x.GetLeft()) for x in bs),min(p.ToMM(x.GetTop()) for x in bs),max(p.ToMM(x.GetRight()) for x in bs),max(p.ToMM(x.GetBottom()) for x in bs)]
dr.text((15,15),'Actual B.Cu top-down projection, x0-12 / y40-51 mm; not a mirrored assembly instruction',fill='white');im.save(D/'R220_back.png');(D/'back_courtyards.json').write_text(json.dumps(boxes,indent=2));print(boxes)
