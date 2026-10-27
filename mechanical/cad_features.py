import FreeCAD as A, Part, math
V=A.Vector
def box(x,y,z,at):return Part.makeBox(x,y,z,V(*at))
def cyl(r,h,at,axis=(0,0,1)):return Part.makeCylinder(r,h,V(*at),V(*axis))
def cut_holes(s,locations,r,h,axis=(0,0,1)):
 for p in locations:s=s.cut(cyl(r,h,p,axis))
 return s
class ParamPart:
 def __init__(self,obj,kind):
  obj.addProperty('App::PropertyString','Kind');obj.Kind=kind;obj.Proxy=self
  obj.addProperty('App::PropertyLength','HoleClearance');obj.HoleClearance=4.6
 def execute(self,obj):obj.Shape=build(obj.Kind,float(obj.HoleClearance))
 def dumps(self):return None
 def loads(self,state):return None

def build(kind,hole=4.6):
 if kind=='Base':
  s=cut_holes(box(100,90,6,(-50,-45,0)),[(x,y,-1) for x in (-28,28) for y in (22,41)],hole/2,8)
  return cut_holes(s,[(x,y,-1) for x in (-28,28) for y in (22,41)],3.7,4.2)
 if kind=='Upright':
  s=box(80,28,6,(-40,16,6)).fuse(box(80,6,100,(-40,30,12)))
  s=cut_holes(s,[(x,y,5) for x in (-28,28) for y in (22,41)],hole/2,8)
  for x in (-28,28):
   slot=box(hole,8,70,(x-hole/2,29,24)).fuse(cyl(hole/2,8,(x,29,24),(0,1,0))).fuse(cyl(hole/2,8,(x,29,94),(0,1,0)))
   s=s.cut(slot)
  return s
 if kind=='Carrier':
  s=box(76,6,24,(-38,24,38)).fuse(box(76,44,4,(-38,-20,38)))
  s=s.cut(box(24,24,6,(-12,-12,37)))
  s=cut_holes(s,[(x,23,50) for x in (-28,28)],hole/2,8,(0,1,0))
  return cut_holes(s,[(x,y,37) for x in (-15,15) for y in (-12.5,12.5)],1.7,6)
 if kind=='Adapter_SC035HGS_candidate':
  s=box(40,35,3,(-20,-17.5,42)).cut(cyl(5.5,5,(0,0,41))).cut(box(9,11,5,(-4.5,-17.5,41)))
  for x in (-9,9):
   s=s.cut(box(.6,1.9,5,(x-.3,-.95,41)).fuse(cyl(.95,5,(x-.3,0,41))).fuse(cyl(.95,5,(x+.3,0,41))))
  return cut_holes(s,[(x,y,41) for x in (-15,15) for y in (-12.5,12.5)],1.7,5)
 if kind=='Nose_guide_coupon':
  # Standalone guide only; tube Ø2.35 nominal, 0.45mm diametric clearance; verify real refill.
  return cyl(9,4,(0,0,0)).fuse(Part.makeCone(5,3,8,V(0,0,4))).cut(cyl(1.4,14,(0,0,-1)))
 if kind.startswith('Paper_wedge_'):
  rise=8*math.tan(math.radians(int(kind.split('_')[-1])))
  pts=[V(-10,-4,0),V(-10,4,0),V(-10,4,3+rise),V(-10,-4,3),V(-10,-4,0)]
  return Part.Face(Part.makePolygon(pts)).extrude(V(20,0,0))
 raise ValueError(kind)

