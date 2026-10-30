from pathlib import Path
import os,sys,json,math,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/indedata81308';sys.path.append('/usr/lib/freecad-python3/lib');import pcbnew as p
O=Path(__file__).resolve().parent;W=O.parent;H=W/'smart_pen_next_20261028/hardware';q=H/'data_bias_relocate_1242/native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(q));old=p.LoadBoard(str(H/'sccb_local_reference_1216/native/mainboard_revD.kicad_pcb'));fps={f.GetReference():f for f in b.GetFootprints()}
def req(x,msg):
 if not x:raise RuntimeError(msg)
req(hashlib.sha256(q.read_bytes()).hexdigest()=='4d7d95d253b3c8c994a7f2c4c628087346c271ea290c69aa511ea9a1cb8eadad','exact PCB')
def xy(v):return(v.x/1e6,v.y/1e6)
def ident(t):return(t.GetClass(),t.GetNetname(),t.GetLayerName(),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),*xy(t.GetStart()),*xy(t.GetEnd()),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None)
oldset={ident(t)for t in old.GetTracks()};new=[t for t in b.GetTracks()if ident(t)not in oldset];req(sum(isinstance(t,p.PCB_VIA)for t in new)==11,'11via')
def rect(v):
 out=p.SHAPE_POLY_SET();out.NewOutline()
 for x,y in [(v[0],v[1]),(v[2],v[1]),(v[2],v[3]),(v[0],v[3])]:out.Append(round(x*1e6),round(y*1e6))
 return out
def cap(t):
 out=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(out,p.F_Cu,0,50,p.ERROR_OUTSIDE);return out
def area(a,b):
 out=p.SHAPE_POLY_SET();out.BooleanIntersection(a,b);return out.Area()/1e12
L=json.load(open(W/'assembly_context_audit_0818_20261030/all103_sync.json'))['rows']
def full(ref):
 r=next(r for r in L if r['ref']==ref);bb=r['contexts'][0]['entities'][0]['projected_current_bounds_not_final_assembly'];v=[bb[0]+7,127-bb[5],bb[3]+7,127-bb[2]]
 if ref=='R217':v=[v[0]+1.4,v[1]+7.19,v[2]+1.4,v[3]+7.19]
 return rect(v)
def fab(ref):
 boxes=[g.GetBoundingBox()for g in fps[ref].GraphicalItems()if isinstance(g,p.PCB_SHAPE)and g.GetLayer()==p.F_Fab];v=[min(x.GetX()for x in boxes)/1e6,min(x.GetY()for x in boxes)/1e6,max(x.GetRight()for x in boxes)/1e6,max(x.GetBottom()for x in boxes)/1e6];return rect(v)
rows=[]
for ref,net,a,c in [('R217','CAM_D7',(2.95,28.95),(3.55,28.975)),('R215','CAM_D5',(4.75,28.8),(4.85,29.075))]:
 tracks=[t for t in new if not isinstance(t,p.PCB_VIA)and t.GetNetname()==net and t.GetLayer()==p.F_Cu];t=next(t for t in tracks if {xy(t.GetStart()),xy(t.GetEnd())}=={a,c});pads={xy(z.GetPosition()):z.GetNumber()for z in fps[ref].Pads()if z.GetNetname()==net};linked=[x for x in tracks if x is not t and {xy(x.GetStart()),xy(x.GetEnd())}&{a,c}and {xy(x.GetStart()),xy(x.GetEnd())}&set(pads)];req(len(linked)==1,'unique pad-ended connected branch');s=cap(t);body_area=area(s,full(ref));fab_area=area(s,fab(ref));req(body_area<1e-10 and fab_area<1e-10,'exit underbody/Fab intrusion');f=fps[ref];f.BuildCourtyardCaches();poly=f.GetCourtyard(p.F_Cu);court_area=area(s,poly);rows.append({'ref':ref,'net':net,'continuation':[a,c],'connected_pad_segment':[xy(linked[0].GetStart()),xy(linked[0].GetEnd())],'same_net_pad_positions':list(pads),'body_area':body_area,'Fab_area':fab_area,'native_finite_courtyard_area':court_area})
u=fab('U201');hits=[];n=0
for t in new:
 if isinstance(t,p.PCB_VIA)or t.GetLayer()!=p.F_Cu:continue
 n+=1;v=area(cap(t),u)
 if v>1e-10:hits.append({'net':t.GetNetname(),'area':v})
req(not hits,'U201 Fab intruded')
(O/'independent_exits.json').write_text(json.dumps({'two_continuations':rows,'all_new_front_tracks_checked_U201Fab':n,'U201Fab_hits':hits},indent=2)+'\n');print(rows)
