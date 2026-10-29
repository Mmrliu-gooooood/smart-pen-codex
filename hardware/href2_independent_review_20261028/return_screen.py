from pathlib import Path
import pcbnew as p,json,math,collections
D=Path(__file__).resolve().parent;A=D.parent/'mainboard_href3_candidate/mainboard_revD.kicad_pcb';B=D.parent/'mainboard_href2_candidate/mainboard_revD.kicad_pcb';a=p.LoadBoard(str(A));b=p.LoadBoard(str(B));old={t.m_Uuid.AsString():t for t in a.GetTracks()};new={t.m_Uuid.AsString():t for t in b.GetTracks()}
def xy(v):return[p.ToMM(v.x),p.ToMM(v.y)]
planes=[z.GetFilledPolysList(p.In1_Cu) for z in b.Zones() if z.GetLayer()==p.In1_Cu and z.GetNetname()=='GND']
def hit(x,y):
 q=p.VECTOR2I(p.FromMM(x),p.FromMM(y));return any(poly.Contains(q,i) for poly in planes for i in range(poly.OutlineCount()))
rows=[]
for t in b.GetTracks():
 if t.GetNetname()!='CAM_HREF' or t.GetClass()!='PCB_TRACK' or t.GetLayer()!=p.In2_Cu:continue
 u,v=xy(t.GetStart()),xy(t.GetEnd());length=p.ToMM(t.GetLength());n=max(1,math.ceil(length/.025));theta=math.atan2(v[1]-u[1],v[0]-u[0]);points=[]
 for i in range(n+1):
  x=u[0]+(v[0]-u[0])*i/n;y=u[1]+(v[1]-u[1])*i/n
  hits=[hit(x+off*math.sin(theta),y-off*math.cos(theta)) for off in [0,-.15,.15]]
  points.append({'x_mm':x,'y_mm':y,'centre_gnd':hits[0],'offset_minus150um_gnd':hits[1],'offset_plus150um_gnd':hits[2]})
 rows.append({'uuid':t.m_Uuid.AsString(),'start':u,'end':v,'length_mm':length,'width_mm':p.ToMM(t.GetWidth()),'samples':points})
gvias=[xy(t.GetPosition()) for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()=='GND'];viarows=[]
for t in b.GetTracks():
 if not isinstance(t,p.PCB_VIA) or t.GetNetname()!='CAM_HREF':continue
 q=xy(t.GetPosition());dist,pos=min((math.dist(q,g),g) for g in gvias);viarows.append({'signal_via_mm':q,'nearest_gnd_via_mm':pos,'distance_mm':dist,'is_new':t.m_Uuid.AsString() not in old})
changed={}
for net in ['3V3_AON','GND','CHIP_EN','CAM_D7','CAM_VSYNC']:
 out={}
 for tag,board,uidset in [('removed',a,set(old)-set(new)),('added',b,set(new)-set(old))]:
  data=[]
  for t in board.GetTracks():
   if t.GetNetname()!=net or t.m_Uuid.AsString() not in uidset:continue
   r={'type':t.GetClass(),'start':xy(t.GetStart()),'end':xy(t.GetEnd()),'layer':board.GetLayerName(t.GetLayer())}
   if isinstance(t,p.PCB_VIA):r.update(diameter_mm=p.ToMM(t.GetWidth(p.F_Cu)),drill_mm=p.ToMM(t.GetDrillValue()))
   else:r.update(length_mm=p.ToMM(t.GetLength()),width_mm=p.ToMM(t.GetWidth()))
   data.append(r)
  out[tag]=data
 changed[net]=out
summary={'inner_href_length_mm':sum(r['length_mm'] for r in rows),'samples_total':sum(len(r['samples']) for r in rows),'centre_no_ground':sum(not s['centre_gnd'] for r in rows for s in r['samples']),'corridor_any_no_ground':sum(not(s['centre_gnd'] and s['offset_minus150um_gnd'] and s['offset_plus150um_gnd']) for r in rows for s in r['samples']),'href_via_return_distance':viarows}
(D/'return_screen.json').write_text(json.dumps({'method':'Actual filled In1 GND polygon point containment every <=25um along In2 HREF centreline and +/−150um offsets. Coincident segment endpoint samples are repeated. This geometric screen is not return-current or impedance qualification.','summary':summary,'inner_tracks':rows,'changed_net_geometry':changed},indent=2));print(json.dumps(summary,indent=2));print('AON',json.dumps(changed['3V3_AON'],indent=2))
