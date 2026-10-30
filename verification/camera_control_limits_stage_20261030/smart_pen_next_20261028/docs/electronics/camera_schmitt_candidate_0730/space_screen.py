from pathlib import Path
import os,json,hashlib,sys
os.environ['XDG_CONFIG_HOME']='/tmp/iso_space0730'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[2];S=R/'hardware/camera_isolation_control_native_0628/native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(S));q=next(f for f in b.GetFootprints()if f.GetReference()=='Q201');old=list(b.GetTracks());pads=[a for f in b.GetFootprints()if f.GetReference()!='Q201'for a in f.Pads()]
# Official TI DCK0005A land example, not blind use of the smaller generic KiCad SOT353 pads.
base={1:(-1.1,-.65),2:(-1.1,0),3:(-1.1,.65),4:(1.1,.65),5:(1.1,-.65)};nets={1:'',2:'ISO_GATE',3:'GND',4:'CAM_ISO_OE_N',5:'3V3_AON'}
def req(c,m):
 if not c:raise RuntimeError(m)
req(hashlib.sha256(S.read_bytes()).hexdigest()=='63d460c70405e1c1042f5e150a7fe5c5c5c32346fb37209a386cf03a1eacdd7c','parent')
def rect(x,y,w,h):
 poly=p.SHAPE_POLY_SET();poly.NewOutline()
 for a,z in[(x-w/2,y-h/2),(x+w/2,y-h/2),(x+w/2,y+h/2),(x-w/2,y+h/2)]:poly.Append(round(a*1e6),round(z*1e6))
 return poly
rows=[]
for angle in[0,180]:
 cx=q.GetPosition().x/1e6;cy=q.GetPosition().y/1e6;out=[]
 for num,(x,y)in base.items():
  if angle:x,y=-x,-y
  x+=cx;y+=cy;poly=rect(x,y,.95,.4);guard=rect(x,y,.95+.3,.4+.3);hits=[]
  for item in old+pads:
   if not item.IsOnLayer(p.F_Cu)or item.GetNetname()==nets[num]:continue
   sh=p.SHAPE_POLY_SET();item.TransformShapeToPolygon(sh,p.F_Cu,0,50,p.ERROR_OUTSIDE);z=p.SHAPE_POLY_SET();z.BooleanIntersection(guard,sh)
   if z.Area()>1:hits.append({'object':item.GetParentFootprint().GetReference()+'.'+item.GetNumber()if isinstance(item,p.PAD)else item.m_Uuid.AsString(),'net':item.GetNetname(),'overlap_guard_mm2':z.Area()/1e12})
  out.append({'pin':num,'net_proposed':nets[num],'xy_mm':[x,y],'land_mm':[.95,.4],'foreign_F_copper_clearance_conflicts':hits})
 rows.append({'pose':{'xy_mm':[cx,cy],'angle_deg':angle},'pins':out,'blocked_pin_count':sum(bool(r['foreign_F_copper_clearance_conflicts'])for r in out)})
print(json.dumps({'status':'PRELIMINARY_OFFICIAL_LAND_PATTERN_SCREEN_NOT_LAYOUT','source_pcb_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'TI_DCK0005A':{'body_max_mm':[1.4,2.15],'overall_lead_span_max_mm':2.4,'height_max_mm':1.1,'pitch_mm':.65,'example_land_size_mm':[.95,.4],'example_land_row_center_spacing_mm':2.2},'generic_KiCad_SOT353_not_same_as_TI_example':{'land_size_mm':[.65,.4],'row_spacing_mm':1.9},'two_same_center_orientations_only':rows,'limits':['Q201 removed hypothetically from this read-only clearance screen, old traces remain; no PCB saved','NC pin1 is a real solder pad, no arbitrary connection','This square expanded guard is conservative, not a rounded exact DRC calculation','Supply bypass C209 not placed; complete AON/GND access and all-layer checks not yet possible','If conflicts exist they show not drop-in, not global placement impossibility','Full source proof must precede any native revision']},indent=2))
