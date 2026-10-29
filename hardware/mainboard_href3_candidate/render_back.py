from pathlib import Path
import pcbnew as p,json
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'mainboard_revD.kicad_pcb'));S=160;X0=0;Y0=44;im=Image.new('RGB',(1920,1440),'#17212b');d=ImageDraw.Draw(im)
def xy(v):return ((p.ToMM(v.x)-X0)*S,(p.ToMM(v.y)-Y0)*S)
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):
  x,y=xy(t.GetPosition());r=p.ToMM(t.GetWidth(p.B_Cu))/2*S;d.ellipse((x-r,y-r,x+r,y+r),outline='#ffba60',width=3);r=p.ToMM(t.GetDrillValue())/2*S;d.ellipse((x-r,y-r,x+r,y+r),fill='#17212b')
 elif t.GetLayer()==p.B_Cu:d.line([xy(t.GetStart()),xy(t.GetEnd())],fill='#ff765b',width=max(1,round(p.ToMM(t.GetWidth())*S)))
boxes={}
for f in b.GetFootprints():
 if not f.IsOnLayer(p.B_Cu):continue
 for a in f.Pads():
  if not a.IsOnLayer(p.B_Cu):continue
  box=a.GetBoundingBox();q=xy(box.GetOrigin());z=xy(box.GetEnd());d.rectangle([q,z],fill='#e7a751')
 for it in f.GraphicalItems():
  if it.GetLayer()==p.B_CrtYd and it.GetClass()=='PCB_SHAPE':d.line([xy(it.GetStart()),xy(it.GetEnd())],fill='#64e1d0',width=2)
 if f.GetReference() in ['U202','R220','C205','C206']:
  d.text(xy(f.GetPosition()),f.GetReference(),fill='white',stroke_width=1);items=[it.GetBoundingBox() for it in f.GraphicalItems() if it.GetLayer()==p.B_CrtYd];boxes[f.GetReference()]=[min(p.ToMM(x.GetLeft()) for x in items),min(p.ToMM(x.GetTop()) for x in items),max(p.ToMM(x.GetRight()) for x in items),max(p.ToMM(x.GetBottom()) for x in items)]
d.text((10,10),'Actual B.Cu / actual courtyards; x0-12 mm, y44-53 mm',fill='white');im.save(D/'R220_back.png');(D/'courtyard_bounds.json').write_text(json.dumps(boxes,indent=2));print(boxes)
