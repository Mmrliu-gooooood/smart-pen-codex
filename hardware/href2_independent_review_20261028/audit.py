from pathlib import Path
import pcbnew as p,hashlib,json,math,collections,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent;H=D.parent;A=H/'mainboard_href3_candidate';B=H/'mainboard_href2_candidate'
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
require(sha(A/'mainboard_revD.kicad_pcb')=='f00d85c7eea8e8abdbf89eb83720fa7aeca564e939f0b6b5f89d548881cb7815','wrong baseline')
require(sha(B/'mainboard_revD.kicad_pcb')=='228b04b42c45ebb37ca96a27d84a4f7a48f3e2b805c63dff0c2c6a5be2e6fb69','wrong candidate')
def xml(f):
 root=E.parse(f)
 comps={c.attrib['ref']:{'value':c.findtext('value'),'fp':c.findtext('footprint'),'props':sorted((p.attrib.get('name'),p.attrib.get('value')) for p in c.findall('property'))} for c in root.findall('./components/comp')}
 ns={(c.attrib['ref'],c.attrib['pin']):n.attrib['name'] for n in root.findall('./nets/net') for c in n}
 return comps,ns
ac,an=xml(A/'mainboard_revD.xml');bc,bn=xml(D/'fresh.xml');require(ac==bc and an==bn,'native source changed')
a=p.LoadBoard(str(A/'mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(B/'mainboard_revD.kicad_pcb'))
def fps(board):return {f.GetReference():f for f in board.GetFootprints()}
af,bf=fps(a),fps(b);require(af.keys()==bf.keys(),'footprints changed')
def pads(f):return sorted((x.GetNumber(),x.GetNetname(),x.GetPosition().x,x.GetPosition().y,x.GetSize().x,x.GetSize().y,x.GetOrientationDegrees(),tuple(x.GetLayerSet().Seq()),int(x.GetShape()),x.GetRoundRectRadiusRatio()) for x in f.Pads())
for r,f in bf.items():
 old=af[r];require(f.GetValue()==old.GetValue() and str(f.GetFPID())==str(old.GetFPID()) and f.GetPath().AsString()==old.GetPath().AsString() and f.GetAttributes()==old.GetAttributes(),r+' identity changed')
 require(pads(f)==pads(old),r+' pad geometry changed')
 for q in f.Pads():require(q.GetNetname()==bn[r,q.GetNumber()],r+' pin mapping wrong')
f=bf['R220'];require(f.IsOnLayer(p.B_Cu) and af['R220'].IsOnLayer(p.B_Cu),'R220 side unexpected');q={x.GetNumber():x for x in f.Pads()};require((q['1'].GetPosition().x,q['1'].GetPosition().y)==(1200000,45000000),'R220.1 position');require((q['2'].GetPosition().x,q['2'].GetPosition().y)==(2850000,45000000),'R220.2 position')
def copper(board):
 return {t.m_Uuid.AsString():(t.GetClass(),t.GetNetname(),int(t.GetLayer()),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth(),t.GetDrillValue() if isinstance(t,p.PCB_VIA) else 0) for t in board.GetTracks()}
at,bt=copper(a),copper(b)
T=H/'mainboard_mainhref_trial_1844';X=H/'mainboard_revD/routing_trial/xclk5_review/mainboard_revD.kicad_pcb';R=H/'mainboard_revD/routing_trial/href_frontier_study/href_left_source.kicad_pcb'
contract=json.loads((T/'transplant_contract.json').read_text());require(sha(X)==contract['old_source_sha256'] and sha(R)==contract['research_sha256'],'research identity mismatch')
xt,rt=copper(p.LoadBoard(str(X))),copper(p.LoadBoard(str(R)))
removed=set(xt)-set(rt);changed={k for k in xt.keys()&rt.keys() if xt[k]!=rt[k]};added=set(rt)-set(xt)
require(removed==set(contract['removed']) and changed==set(contract['changed']),'transplant contract mismatch')
for key in removed|changed:require(key in at and at[key]==xt[key],'predecessor transplant overlap mismatch')
expected=collections.Counter(at.values())
for key in removed|changed:expected[xt[key]]-=1
for key in added|changed:expected[rt[key]]+=1
ground_removed=json.loads((T/'ground_open_research_removed.json').read_text());require(len(ground_removed)==5 and len(set(ground_removed))==5,'ground removal set')
for key in ground_removed:
 require(key in at and at[key][1]=='GND','removed non-ground');expected[at[key]]-=1
new_contract={}
for f in ['hrefmain_ground_open_expected_new.json','href2b_candidate_expected_new.json']:
 jj=json.loads((T/f).read_text());require(not set(jj)&set(new_contract),'duplicate new contract UUID');new_contract.update(jj)
for key,net in new_contract.items():
 require(key in bt and bt[key][1]==net,'literal new route ownership mismatch');expected[bt[key]]+=1
require(+expected==collections.Counter(bt.values()),'actual final geometry is not exact explicit transplant plus route contracts')
retained={k for k in at.keys()&bt.keys() if at[k]==bt[k]};final_removed=set(at)-set(bt);final_changed={k for k in at.keys()&bt.keys() if at[k]!=bt[k]};new=set(bt)-set(at)
length=collections.defaultdict(float);vias=[]
for t in b.GetTracks():
 if t.m_Uuid.AsString() not in new:continue
 if isinstance(t,p.PCB_VIA):vias.append({'net':t.GetNetname(),'x_mm':p.ToMM(t.GetPosition().x),'y_mm':p.ToMM(t.GetPosition().y),'diameter_mm':p.ToMM(t.GetWidth(p.F_Cu)),'drill_mm':p.ToMM(t.GetDrillValue())})
 else:length[t.GetNetname()]+=p.ToMM(t.GetLength())
def graph(board):
 board.BuildConnectivity();conn=board.GetConnectivity();res=[]
 for net in sorted({x.GetNetname() for f in board.GetFootprints() for x in f.Pads()}):
  pp=[x for f in board.GetFootprints() for x in f.Pads() if x.GetNetname()==net]
  if len(pp)<2:continue
  items={x.m_Uuid.AsString():x for x in pp};items.update({x.m_Uuid.AsString():x for x in board.GetTracks() if x.GetNetname()==net});parents={k:k for k in items}
  def root(k):
   parents.setdefault(k,k)
   while k!=parents[k]:parents[k]=parents[parents[k]];k=parents[k]
   return k
  def join(k,j):parents[root(k)]=root(j)
  for key,x in items.items():
   for t in list(conn.GetConnectedPads(x))+list(conn.GetConnectedTracks(x)):
    if t.m_Uuid.AsString() in items and t.GetNetname()==net:join(key,t.m_Uuid.AsString())
  for zi,z in enumerate(board.Zones()):
   if z.GetNetname()!=net:continue
   l=z.GetLayer();poly=z.GetFilledPolysList(l)
   for island in range(poly.OutlineCount()):
    key='zone:'+str(zi)+':'+str(island)
    for uid,x in items.items():
     pts=[]
     if isinstance(x,p.PCB_VIA):
      center=x.GetPosition();inner=x.GetDrillValue()/2;outer=x.GetWidth(l)/2
      for rad in [(inner+outer)/2,outer-10000]:
       if rad>inner:
        pts.extend(p.VECTOR2I(int(center.x+rad*math.cos(math.radians(deg))),int(center.y+rad*math.sin(math.radians(deg)))) for deg in range(0,360,15))
     elif x.GetClass()=='PAD' and x.IsOnLayer(l):pts=[x.GetPosition()]
     elif x.GetClass()=='PCB_TRACK' and x.GetLayer()==l:pts=[x.GetStart(),x.GetEnd()]
     if any(poly.Contains(pt,island) for pt in pts):join(key,uid)
  parts={}
  for x in pp:parts.setdefault(root(x.m_Uuid.AsString()),[]).append(x.GetParentFootprint().GetReference()+'.'+x.GetNumber()+'@'+x.m_Uuid.AsString())
  res.append({'net':net,'pad_count':len(pp),'components':list(parts.values())})
 return res
ag,bg=graph(a),graph(b);ad={x['net']:x for x in ag};bd={x['net']:x for x in bg};require(ad.keys()==bd.keys(),'physical net set changed')
for net,x in ad.items():
 if len(x['components'])==1:require(len(bd[net]['components'])==1,'previously connected net opened: '+net)
remaining={n:len(x['components']) for n,x in bd.items() if len(x['components'])>1};require(remaining=={'CAM_PWDN_UART_RX':2,'RF_SIP':2},'unexpected missing graph')
for n,count in [('3V3_AON',27),('GND',75),('SENS_VIO_1V8',11)]:require(bd[n]['pad_count']==count and len(bd[n]['components'])==1,n+' endpoint loss')
require(any(any(s.startswith('R220.1@') for s in part) and any(s.startswith('U202.6@') for s in part) for part in bd['CAM_HREF']['components']),'bias not joined to U202')
r={'source_entities':len(bc),'source_pin_endpoints':len(bn),'source_unchanged':True,'all_footprint_pads_unchanged':len(bf),'retained_exact_copper':len(retained),'removed_copper':len(final_removed),'same_uuid_changed_copper':len(final_changed),'added_copper':len(new),'removed_by_net':dict(collections.Counter(at[k][1] for k in final_removed)),'changed_by_net':dict(collections.Counter(at[k][1] for k in final_changed)),'added_by_net':dict(collections.Counter(bt[k][1] for k in new)),'new_length_by_net_mm':dict(length),'added_vias':vias,'remaining_net_components':remaining,'physical_graph':bg};(D/'audit_result.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='physical_graph'},indent=2))
