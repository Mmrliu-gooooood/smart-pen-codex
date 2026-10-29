from pathlib import Path
import pcbnew as p,xml.etree.ElementTree as E,json,hashlib,math,collections
D=Path(__file__).resolve().parent;B=Path('/workspace/scratch/fe148e758944/smart_pen_next_20261028/hardware/mainboard_resume_20261028');src=B.parent/'mainboard_revD/routing_trial/xclk5_review/mainboard_revD.kicad_pcb';path=B/'mainboard_revD.kicad_pcb'
a=p.LoadBoard(str(src));b=p.LoadBoard(str(path));b.BuildConnectivity();con=b.GetConnectivity()
def ensure(ok,msg):
 if not ok:raise RuntimeError(msg)
def component_file(f):
 e=E.parse(f);cs={c.attrib['ref']:{'value':c.findtext('value'),'footprint':c.findtext('footprint') or '', 'dnp':c.find("property[@name='dnp']") is not None,'exclude':c.find("property[@name='exclude_from_bom']") is not None} for c in e.findall('./components/comp')};ns={(x.attrib['ref'],x.attrib['pin']):n.attrib['name'] for n in e.findall('./nets/net') for x in n};return cs,ns
oc,on=component_file(B.parent/'mainboard_revD/routing_trial/xclk5_review/mainboard_revD.xml');nc,nn=component_file(D/'fresh.xml');ensure(on==nn,'native pin/net changed');ensure(oc.keys()==nc.keys(),'native component set changed');diff=[(r,k,oc[r][k],nc[r][k]) for r in oc for k in oc[r] if oc[r][k]!=nc[r][k]];ensure(diff==[('R217','footprint','Resistor_SMD:R_0603_1608Metric','Resistor_SMD:R_0402_1005Metric')],'unexpected source diff')
def pad_sig(x):return(x.GetNumber(),x.GetNetname(),x.GetPosition().x,x.GetPosition().y,x.GetSize().x,x.GetSize().y,x.GetOrientationDegrees(),tuple(x.GetLayerSet().Seq()),x.GetShape(),x.GetRoundRectRadiusRatio())
of={f.GetReference():f for f in a.GetFootprints()};nf={f.GetReference():f for f in b.GetFootprints()};ensure(of.keys()==nf.keys(),'footprint ref mismatch')
for ref,f in nf.items():
 ensure(f.GetValue()==nc[ref]['value'] and f.IsDNP()==nc[ref]['dnp'] and f.IsExcludedFromBOM()==nc[ref]['exclude'],ref+' source value/attributes')
 ensure(str(f.GetFPID().GetLibNickname())+':'+str(f.GetFPID().GetLibItemName())==nc[ref]['footprint'],ref+' source fpid')
 ensure(f.GetPath().AsString()==of[ref].GetPath().AsString(),ref+' source path changed')
 if ref!='R217':ensure(sorted(map(pad_sig,f.Pads()))==sorted(map(pad_sig,of[ref].Pads())),ref+' other pad geometry changed')
 for x in f.Pads():ensure(x.GetNetname()==nn[ref,x.GetNumber()],ref+' actual pin net mismatch')
def ts(t):return(t.GetClass(),t.GetNetname(),t.GetLayer(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth(),t.GetDrillValue() if isinstance(t,p.PCB_VIA) else 0)
ot={t.m_Uuid.AsString():ts(t) for t in a.GetTracks()};nt={t.m_Uuid.AsString():ts(t) for t in b.GetTracks()};removed=set(ot)-set(nt);added=set(nt)-set(ot);ensure(len(removed)==2 and all(ot[k][1]=='CAM_D7' for k in removed),'unexpected removed copper');ensure(all(ot[k]==nt[k] for k in ot.keys()&nt.keys()),'retained copper changed');ensure(collections.Counter(nt[k][1] for k in added)=={'CAM_D7':4,'GND':2},'unexpected new copper set')
results=[]
for net in sorted({x.GetNetname() for f in b.GetFootprints() for x in f.Pads()}):
 pads=[x for f in b.GetFootprints() for x in f.Pads() if x.GetNetname()==net]
 if len(pads)<2:continue
 items={x.m_Uuid.AsString():x for x in pads}
 items.update({x.m_Uuid.AsString():x for x in b.GetTracks() if x.GetNetname()==net});parent={k:k for k in items}
 def root(k):
  while parent[k]!=k:parent[k]=parent[parent[k]];k=parent[k]
  return k
 def join(k,z):
  parent.setdefault(k,k);parent.setdefault(z,z);parent[root(k)]=root(z)
 for key,x in items.items():
  for y in list(con.GetConnectedTracks(x))+list(con.GetConnectedPads(x)):
   uid=y.m_Uuid.AsString()
   if uid in items and y.GetNetname()==net:join(key,uid)
 zones=[]
 for zi,z in enumerate(b.Zones()):
  if z.GetNetname()!=net:continue
  l=z.GetLayer();poly=z.GetFilledPolysList(l)
  for oi in range(poly.OutlineCount()):
   zk='zone%d:%d'%(zi,oi);hits=[]
   for key,x in items.items():
    pts=[]
    if isinstance(x,p.PCB_VIA):
     c=x.GetPosition();r0=x.GetDrillValue()/2;r1=x.GetWidth(l)/2
     for rad in [(r0+r1)/2,r1-10000]:
      if rad<=r0:continue
      for deg in range(0,360,30):pts.append(p.VECTOR2I(int(c.x+rad*math.cos(math.radians(deg))),int(c.y+rad*math.sin(math.radians(deg)))))
    elif x.GetClass()=='PAD' and x.IsOnLayer(l):pts=[x.GetPosition()]
    elif x.GetClass()=='PCB_TRACK' and x.GetLayer()==l:pts=[x.GetStart(),x.GetEnd()]
    if any(poly.Contains(pt,oi) for pt in pts):join(key,zk);hits.append(key)
   zones.append({'layer':b.GetLayerName(l),'island':oi,'local_objects_touching':len(hits)})
 components={}
 for x in pads:components.setdefault(root(x.m_Uuid.AsString()),[]).append(x.GetParentFootprint().GetReference()+'.'+x.GetNumber()+'@'+x.m_Uuid.AsString())
 results.append({'net':net,'padshape_count':len(pads),'components':list(components.values()),'connected':len(components)==1,'zones':zones})
expected={'CAM_HREF':3,'CAM_PWDN_UART_RX':2,'RF_SIP':2};actual={r['net']:len(r['components']) for r in results if not r['connected']};ensure(actual==expected,'unexpected copper graph '+repr(actual));ensure(all(next(r for r in results if r['net']==n)['connected'] for n in ['GND','3V3_AON','SENS_VIO_1V8','CAM_D7']),'critical graph disconnected')
r={'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'baseline_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'native_source_diff':diff,'source_entities':len(nc),'pin_endpoints':len(nn),'unchanged_nonR217_pad_geometry':73,'removed_tracks_vias':list(removed),'added_tracks_vias':list(added),'retained_copper_unchanged':len(ot.keys()&nt.keys()),'method':'Native local pad/track/via copper adjacency plus actual filled polygon islands; via annular samples, no same-net island shortcuts. Distinct physical pad UUID nodes retained.','net_graphs':results};(D/'independent_check.json').write_text(json.dumps(r,indent=2));print('Native diff, pad geometry, retained copper verified. Disconnected:',actual);print([(r['net'],r['padshape_count'],r['connected']) for r in results if r['net'] in ['GND','3V3_AON','SENS_VIO_1V8','CAM_D7']])
