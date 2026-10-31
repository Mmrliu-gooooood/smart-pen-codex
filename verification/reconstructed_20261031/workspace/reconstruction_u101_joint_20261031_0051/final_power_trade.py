from pathlib import Path
import os,sys,json,math,hashlib
os.environ.update(XDG_CONFIG_HOME='/tmp/newreconstruct/config',XDG_CACHE_HOME='/tmp/newreconstruct/cache',XDG_DATA_HOME='/tmp/newreconstruct/data')
import pcbnew as p
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D/'review_dependencies'));from native_polygon import native_fractured_once
A=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));B=p.LoadBoard(str(D/'data8_review_native/mainboard_revD.kicad_pcb'))
def req(c,s):
 if not c:raise RuntimeError(s)
def sig(t):return[t.GetNetname(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetLayerSet().FmtHex(),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None]
a={t.m_Uuid.AsString():t for t in A.GetTracks()};b={t.m_Uuid.AsString():t for t in B.GetTracks()};ids=['11d26ef2-133b-41cb-8242-f0750c446f96','4b070c1d-13f5-48c3-a7dc-442af935bad8','6938faac-6324-49cf-90da-fc988559d16b'];req(all(sig(a[i])==sig(b[i])for i in ids),'exact direct capacitor pin conductors');length=sum(a[i].GetLength()/1e6 for i in ids);req(abs(length-2.55)<1e-8,'direct length')
for prefix in ['USB','BOOT_N']:
 old={i:sig(t)for i,t in a.items()if t.GetNetname().startswith(prefix)};new={i:sig(t)for i,t in b.items()if t.GetNetname().startswith(prefix)};req(old==new,'exact protected net '+prefix)
def plane(board,net,layer):
 q=p.SHAPE_POLY_SET()
 for z in board.Zones():
  if not z.GetIsRuleArea()and z.GetNetname()==net and z.IsOnLayer(layer):q.BooleanAdd(native_fractured_once(z.GetFilledPolysList(layer)))
 return q
def corridor(board,net,layer,x,y,w):
 t=p.PCB_TRACK(board);t.SetLayer(layer);t.SetWidth(round(w*1e6));t.SetStart(p.VECTOR2I(round(x[0]*1e6),round(x[1]*1e6)));t.SetEnd(p.VECTOR2I(round(y[0]*1e6),round(y[1]*1e6)));q=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(q,layer,0,50,p.ERROR_OUTSIDE);q.BooleanSubtract(plane(board,net,layer));return q.Area()/1e12
rows={}
for name,board,gnd,aon in [('baseline',A,(6.775,14.8),(5.4,14.2)),('source',B,(6.775,14.8),(5.4,14.75))]:
 rows[name]={'GND_surface_lead_mm':math.dist((6.775,15.8),gnd),'GND_straight_span_to_U101_7_5_11_5_mm':math.dist(gnd,(7.5,11.5)),'AON_pin_to_stitch_surface_mm':abs(aon[1]-13.425),'AON_cap_to_stitch_surface_mm':.175+abs(15.8-aon[1]),'GND_projected_corridor_missing_mm2':{board.GetLayerName(l):{str(w):corridor(board,'GND',l,gnd,(7.5,11.5),w)for w in [.15,.3,.5]}for l in [p.In1_Cu,p.In4_Cu]},'AON_projected_feed_corridor_missing_mm2':{str(w):corridor(board,'3V3_AON',p.In2_Cu,aon,(5.175,18.9),w)for w in [.15,.3,.5]}}
r={'status':'GEOMETRIC_TRADE_NOT_PDN_QUALIFICATION','direct_C104_pin_link_mm':length,'direct_track_uuids_exact':ids,'protected_USB_BOOT_exact':True,'comparison':rows,'ground_lead_plus_straight_span_delta_mm':sum(rows['source'][k]-rows['baseline'][k]for k in ['GND_surface_lead_mm','GND_straight_span_to_U101_7_5_11_5_mm']),'limits':'Straight projected corridors/lengths are geometric screens, not current density, inductance, decoupling equivalence, actual power sequence or timing. Original ground geometry restored exactly; AON pin-to-plane surface path grows .55mm while capacitor-to-plane surface path shortens .55mm. No PDN improvement or equivalence claim.'};(D/'final_power_trade.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
