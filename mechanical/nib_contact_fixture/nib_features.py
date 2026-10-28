import FreeCAD as A,Part
V=A.Vector
AXIS_Z=20.
def box(a,b,c,x,y,z):return Part.makeBox(a,b,c,V(x,y,z))
def cyl(r,l,x,y=0,z=AXIS_Z,d=(1,0,0)):return Part.makeCylinder(r,l,V(x,y,z),V(*d))
def vertical_hole(x,y,z=3,r=1.7,h=12):return cyl(r,h,x,y,z,(0,0,1))
def slot_x(x,y,z,length=3,r=1.7,h=12):
 return box(length,2*r,h,x-length/2,y-r,z).fuse(vertical_hole(x-length/2,y,z,r,h)).fuse(vertical_hole(x+length/2,y,z,r,h))
def holes(s,x,ys=(-12,12)):
 for y in ys:s=s.cut(vertical_hole(x,y,h=30))
 return s
class NibPart:
 def __init__(self,o,kind):
  o.addProperty('App::PropertyString','Kind');o.Kind=kind
  for p,v in [('Stroke',.65),('GuideDiameter',6.4)]:o.addProperty('App::PropertyLength',p);setattr(o,p,v)
  o.Proxy=self
 def execute(self,o):o.Shape=shape(o.Kind,float(o.Stroke),float(o.GuideDiameter))
 def dumps(self):return None
 def loads(self,s):pass

def shape(kind,stroke=.65,guide=6.4,refill=2.35,gap=.05):
 if kind=='Base':
  s=box(105,36,4,-5,-18,0)
  for x in [8,59.5,67.65,77,90]:
   for y in [-12,12]:s=s.cut(vertical_hole(x,y,-1,1.7,6)).cut(vertical_hole(x,y,-1,3.1,3.6))
  return s
 if kind=='NoseGuide':return holes(box(8,32,24,4,-16,4).cut(cyl(1.4,10,3)),8)
 if kind=='FrontGuide':return holes(box(7,32,24,56,-16,4).cut(cyl(guide/2,9,55)),59.5)
 if kind=='RearGuide':return holes(box(6,32,24,74,-16,4).cut(cyl(guide/2,8,73)),77)
 if kind=='Slider':
  s=cyl(3,30,54).fuse(cyl(7,2,63))
  s=s.cut(cyl(1.35,14,53)).cut(cyl(2.1,4,53))
  return s
 if kind=='HardStop':
  x=65+stroke
  s=cyl(9,4,x).cut(cyl(5.4,6,x-1)).fuse(box(10,32,8,x-2,-16,4))
  for y in [-12,12]:s=s.cut(slot_x(x+2,y,3,2,1.7,10))
  return s
 if kind=='SwitchCarrier':
  s=box(12,32,4,85,-16,4).fuse(box(4,16,22,88.2,-8,8))
  for y in [-12,12]:s=s.cut(slot_x(90,y,3,3,1.7,7))
  s=s.cut(cyl(3,6,87.2))
  for y in [-5,5]:
   for z in [15,25]:s=s.cut(cyl(1.2,6,87.2,y,z))
  return s
 raise ValueError(kind)
