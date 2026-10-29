from pathlib import Path
import pcbnew as p
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D.parent/'mainboard_href2_candidate/mainboard_revD.kicad_pcb'));S=180;X0=0;Y0=36;im=Image.new('RGB',(900,1620),'#15212c');dr=ImageDraw.Draw(im)
def xy(v):return((p.ToMM(v.x)-X0)*S,(p.ToMM(v.y)-Y0)*S)
def pts(chain):return[xy(chain.CPoint(i)) for i in range(chain.PointCount())]
for z in b.Zones():
 if z.GetLayer()!=p.In1_Cu or z.GetNetname()!='GND':continue
 pp=z.GetFilledPolysList(p.In1_Cu)
 for i in range(pp.OutlineCount()):
  dr.polygon(pts(pp.COutline(i)),fill='#245b48')
  for j in range(pp.HoleCount(i)):dr.polygon(pts(pp.CHole(i,j)),fill='#15212c')
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):
  q=xy(t.GetPosition());r=p.ToMM(t.GetWidth(p.In1_Cu))/2*S
  dr.ellipse((q[0]-r,q[1]-r,q[0]+r,q[1]+r),outline='#e3be69',width=2)
  if .5<p.ToMM(t.GetPosition().x)<3.6 and 36<p.ToMM(t.GetPosition().y)<44.5:dr.text(q,t.GetNetname(),fill='white')
 elif t.GetLayer()==p.In2_Cu and t.GetNetname()=='CAM_HREF':dr.line([xy(t.GetStart()),xy(t.GetEnd())],fill='#62b4ff',width=max(1,round(p.ToMM(t.GetWidth())*S)))
dr.text((10,10),'Green actual In1 GND; blue In2 HREF; x0-5 / y36-45 mm',fill='white');im.save(D/'In2_HREF_vs_In1_GND.png')
