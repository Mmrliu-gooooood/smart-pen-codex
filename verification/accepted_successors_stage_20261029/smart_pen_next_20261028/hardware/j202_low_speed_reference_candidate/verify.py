from pathlib import Path
import os,sys,json,hashlib,re,xml.etree.ElementTree as ET,collections
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache'
import pcbnew as p
from copper_geometry import shape,build,components,L
D=Path(__file__).resolve().parent;B=D.parent/'j202_ground_return_candidate';path=Path(sys.argv[1])if len(sys.argv)>1 else D/'native/mainboard_revD.kicad_pcb'
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def raw(file):
 t=file.read_text();names={int(n):v for n,v in re.findall(r'\(net (\d+) "([^"\n]+)"\)',t)};out={}
 for q in re.findall(r'\n\t\((?:segment|via)\n.*?\n\t\)',t,re.S):
  u=re.search(r'\(uuid "([^"\n]+)"\)',q);n=re.search(r'\(net (\d+)\)',q)
  if u and n:out[u[1]]=names[int(n[1])]
 return out
ra,rb=raw(B/'native/mainboard_revD.kicad_pcb'),raw(path)
for u in sorted(ra.keys()&rb.keys()):require(ra[u]==rb[u],'SERIALIZED_NET_CHANGED '+u)
expected_delta=json.loads((D/'geometry_delta.json').read_text())
for u,record in sorted(expected_delta['added'].items()):
 require(rb.get(u)==record[1],'SERIALIZED_NEW_NET_CHANGED '+u)
def native_blocks(file,kind):
 t=file.read_text();out={}
 for block in re.findall(r'\n\t\('+kind+r'[^\n]*\n.*?\n\t\)',t,re.S):
  u=re.search(r'\(uuid "([^"\n]+)"\)',block)
  if u:out[u[1]]=block
 return out
fa,fb=native_blocks(B/'native/mainboard_revD.kicad_pcb','footprint'),native_blocks(path,'footprint');require(fa==fb,'COMPLETE_NATIVE_FOOTPRINT_BLOCK_CHANGED')
za,zb=native_blocks(B/'native/mainboard_revD.kicad_pcb','zone'),native_blocks(path,'zone');require(set(zb)==set(za),'ZONE_SET_CHANGED')
stripfill=lambda q:re.sub(r'\n\t\t\(filled_polygon\n.*?\n\t\t\)','',q,flags=re.S)
for u in sorted(za):
 require(stripfill(za[u])==stripfill(zb[u]),'UNCHANGED_ZONE_CONFIGURATION '+u)
a=p.LoadBoard(str(B/'native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(path));af={f.GetReference():f for f in a.GetFootprints()};bf={f.GetReference():f for f in b.GetFootprints()}
def fg(f):return(f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees(),f.GetLayer(),f.GetAttributes(),f.GetValue(),f.GetFPIDAsString(),f.GetPath().AsString(),sorted((q.GetNumber(),q.GetNetname(),q.GetPosition().x,q.GetPosition().y,q.GetSize().x,q.GetSize().y,q.GetOrientationDegrees(),tuple(q.GetLayerSet().Seq()))for q in f.Pads()))
require(set(af)==set(bf)and len(bf)==102,'FOOTPRINT_SET_CHANGED')
for r in sorted(af):require(fg(af[r])==fg(bf[r]),'FOOTPRINT_OR_PAD_CHANGED '+r)
x=ET.parse(D/'fresh.xml');cs={c.get('ref'):c for c in x.findall('./components/comp')};ns={(n.get('ref'),n.get('pin')):net.get('name')for net in x.findall('./nets/net')for n in net};require(len(cs)==102 and len(ns)==356,'SOURCE_COUNT')
vio_expected={'J202.23','C202.1','C204.1','C206.1','C208.1','U201.23','U201.24','U202.16','U203.16','U204.1','R242.2','R243.2'}
require({r+'.'+pin for(r,pin),n in ns.items()if n=='SENS_VIO_1V8'}==vio_expected,'VIO_EXTERNAL_INPUT_BOUNDARY_CHANGED')
for pin,n in {'19':'SENS_XSHUTDN_N','20':'SENS_TRIG_IN','21':'SENS_SCL','22':'SENS_SDA','23':'SENS_VIO_1V8'}.items():require(ns.get(('J202',pin))==n,'J202_FIVE_PIN_MAPPING_CHANGED')
mpns=json.loads((D/'native_mpn_contract.json').read_text())['parts']
for r,expected in sorted(mpns.items()):
 fields={f.get('name'):f.text for f in cs[r].findall('./fields/field')}
 for key,sourcekey in [('Manufacturer','manufacturer'),('MPN','mpn'),('ProcurementStatus','status')]:require(fields.get(key)==expected[sourcekey],'NATIVE_MPN_FIELD '+r+' '+key)
for r,f in bf.items():
 c=cs[r];require(f.GetValue()==c.findtext('value')and f.GetFPIDAsString()==c.findtext('footprint'),'SOURCE_PROPERTIES '+r);require(f.GetPath().AsString()=='/cebe562b-54ce-58d7-a4f0-094e70dd7d0a'+c.find('sheetpath').get('tstamps')+c.findtext('tstamps'),'SOURCE_PATH '+r)
 for q in f.Pads():require(q.GetNetname()==ns.get((r,q.GetNumber()),''),'SOURCE_PAD_NET '+r+'.'+q.GetNumber())
for f in(B/'native').rglob('*'):
 if f.is_file()and f.suffix in ['.kicad_sch','.kicad_pro','.kicad_dru']:
  other=D/'native'/f.relative_to(B/'native');require(other.is_file()and sha(f)==sha(other),'SOURCE_PROJECT_TREE_CHANGED '+str(other))
def tg(t):return(t.GetClass(),t.GetNetname(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetLayer(),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None)
at={t.m_Uuid.AsString():t for t in a.GetTracks()};bt={t.m_Uuid.AsString():t for t in b.GetTracks()};removed=set(expected_delta['removed']);require(set(at)-set(bt)==removed,'REMOVED_COPPER_SET');require(not expected_delta['modified'],'NO_OLD_MODIFICATION_CONTRACT')
for u in sorted(at.keys()&bt.keys()):require(tg(at[u])==tg(bt[u]),'UNDECLARED_OLD_COPPER_CHANGE '+u)
for u in sorted(removed):require(list(tg(at[u]))==expected_delta['removed'][u],'REMOVED_BASE_GEOMETRY '+u)
new=set(bt)-set(at);require(new==set(expected_delta['added']),'NEW_COPPER_SET')
for u in sorted(new):require(list(tg(bt[u]))==expected_delta['added'][u],'DECLARED_NEW_GEOMETRY_CHANGED '+u)
require(not removed and not expected_delta['modified'],'OLD_COPPER_MUST_REMAIN')
target_nets=['SENS_XSHUTDN_N','SENS_TRIG_IN','SENS_SCL','SENS_SDA','SENS_VIO_1V8']
require(all(bt[u].GetNetname()in target_nets for u in new),'ONLY_FIVE_DECLARED_NETS_NEW')
for u in sorted(new):
 t=bt[u];require(rb[u]==t.GetNetname(),'SERIALIZED_NEW_NET_CHANGED '+u)
 if isinstance(t,p.PCB_VIA):
  expected=(450000,200000)if t.GetNetname()=='SENS_XSHUTDN_N'else(600000,300000)
  require(t.GetViaType()==p.VIATYPE_THROUGH and all(t.IsOnLayer(l)for l in L)and t.GetDrillValue()==expected[1]and all(t.GetWidth(l)==expected[0]for l in L),'NEW_VIA_GEOMETRY')
  require(t.GetFrontTentingMode()==p.TENTING_MODE_TENTED and t.GetBackTentingMode()==p.TENTING_MODE_TENTED,'NEW_SIGNAL_VIA_TENTING_REQUIRED')
 else:require(t.GetWidth()==(250000 if t.GetNetname()=='SENS_VIO_1V8'else 150000)and t.GetLayer()in[p.F_Cu,p.In3_Cu,p.B_Cu]and not t.HasSolderMask(),'NEW_TRACE_GEOMETRY')
na,nb=build(a),build(b);ca={n:components(v)for n,v in na.items()};cb={n:components(v)for n,v in nb.items()};changed=[]
for n in sorted(ca):
 for c in ca[n]:require(any(set(c)<=set(z)for z in cb[n]),'OLD_PAD_COMPONENT_SPLIT '+n)
 if ca[n]!=cb[n]:changed.append(n)
require(changed==sorted(target_nets),'FIVE_ONLY_COMPONENT_MERGES')
for n in target_nets:require(len(cb[n])==1,'TARGET_NET_UNCONNECTED '+n)
core=next(g for g in cb['GND']if 'C104.2'in g);require(all('J202.'+pin in core for pin in ['1','4','7','10','13','17','24']),'SEVEN_CONNECTOR_GROUNDS_NOT_IN_CORE')
islands={}
for n,anchor in [('3V3_AON','C104.1'),('GND','C104.2')]:
 tagged=[(name,pad or '/'in name,ss)for name,pad,ss in nb[n]];cc=components(tagged);core=next(c for c in cc if anchor in c);allzones=[name for name,pad,ss in nb[n]if '/'in name];require(all(q in core for q in allzones),'UNCONNECTED_PLANE_ISLAND '+n);islands[n]=len(allzones)
# Island count recorded; each actual filled island must remain in core above.
def rect(xx,yy,zz,ww):
 q=p.SHAPE_POLY_SET();q.NewOutline()
 for x,y in[(xx,yy),(zz,yy),(zz,ww),(xx,ww)]:q.Append(p.FromMM(x),p.FromMM(y))
 return q
body=rect(3,81,5,83);central=rect(3.425,81.4125,4.575,82.5875);rules={z.GetZoneName():z for z in b.Zones()if z.GetIsRuleArea()};full=rules.get('LIS2DW12_F_BODY_NO_POUR_OR_THROUGH_VIA');c=rules.get('LIS2DW12_F_CENTRAL_NO_TRACK_PROJECT_SCREEN');require(full is not None and c is not None,'LAYERED_MEMS_RULE_MISSING')
for z,q in[(full,body),(c,central)]:
 require(set(z.GetLayerSet().Seq())=={p.F_Cu}and z.GetDoNotAllowVias()and z.GetDoNotAllowCopperPour(),'MEMS_LAYER_OR_FLAGS');d=p.SHAPE_POLY_SET();d.BooleanSubtract(z.Outline(),q);e=p.SHAPE_POLY_SET();e.BooleanSubtract(q,z.Outline());require(d.Area()+e.Area()<=1,'MEMS_RULE_SHAPE')
require(c.GetDoNotAllowTracks()and not c.GetDoNotAllowPads(),'CENTRAL_TRACK_RULE_FLAGS')
for z in b.Zones():
 if not z.GetIsRuleArea()and z.IsOnLayer(p.F_Cu):q=p.SHAPE_POLY_SET();q.BooleanIntersection(z.GetFilledPolysList(p.F_Cu),body);require(q.Area()<=1,'F_BODY_POUR_INTRUSION')
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):q=p.SHAPE_POLY_SET();q.BooleanIntersection(shape(t,p.F_Cu),body);require(q.Area()<=1,'F_BODY_THROUGH_VIA_INTRUSION')
 elif t.GetLayer()==p.F_Cu:q=p.SHAPE_POLY_SET();q.BooleanIntersection(shape(t,p.F_Cu),central);require(q.Area()<=1,'F_CENTRAL_TRACK_INTRUSION')
 if t.m_Uuid.AsString()in new and t.IsOnLayer(p.F_Cu):
  q=p.SHAPE_POLY_SET();q.BooleanIntersection(shape(t,p.F_Cu),body);require(q.Area()<=1,'NEW_F_BODY_INTRUSION')
require('OPEN'in bf['JP301'].GetValue().upper(),'COMMISSIONING_LINK_NOT_OPEN');require(len(cb['CAM_3V3_PRELINK'])==1 and len(cb['CAM_3V3_SW'])==1,'GATE_OUTPUT_CHANGED')
print(json.dumps({'status':'J202_FIVE_REFERENCE_CONTROL_NETS_STATIC_NOFAB','pcb_sha256':sha(path),'entities':len(bf),'source_endpoints':len(ns),'new_tracks_vias':len(new),'removed_old':len(removed),'only_pad_merges':changed,'all_plane_islands_in_core':islands,'J202_GND_pins_in_core':['1','4','7','10','13','17','24'],'pad_components':cb},indent=2))
