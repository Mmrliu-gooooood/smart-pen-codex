from pathlib import Path
import pcbnew as p,math,json
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
  zone_entries=[]
  for zi,z in enumerate(board.Zones()):
   if z.GetNetname()!=net:continue
   l=z.GetLayer();poly=z.GetFilledPolysList(l)
   for island in range(poly.OutlineCount()):
    key='zone:'+str(zi)+':'+str(island);zone_entries.append({'key':key,'layer':board.GetLayerName(l),'island':island,'local_contacts':0})
    for uid,x in items.items():
     pts=[]
     if isinstance(x,p.PCB_VIA):
      center=x.GetPosition();inner=x.GetDrillValue()/2;outer=x.GetWidth(l)/2
      for rad in [(inner+outer)/2,outer-10000]:
       if rad>inner:
        pts.extend(p.VECTOR2I(int(center.x+rad*math.cos(math.radians(deg))),int(center.y+rad*math.sin(math.radians(deg)))) for deg in range(0,360,15))
     elif x.GetClass()=='PAD' and x.IsOnLayer(l):pts=[x.GetPosition()]
     elif x.GetClass()=='PCB_TRACK' and x.GetLayer()==l:pts=[x.GetStart(),x.GetEnd()]
     if any(poly.Contains(pt,island) for pt in pts):join(key,uid);zone_entries[-1]['local_contacts']+=1
  parts={}
  for x in pp:parts.setdefault(root(x.m_Uuid.AsString()),[]).append(x.GetParentFootprint().GetReference()+'.'+x.GetNumber()+'@'+x.m_Uuid.AsString())
  
  pad_roots={root(x.m_Uuid.AsString()) for x in pp}
  for z in zone_entries:z['root_matches_a_pad_component']=root(z['key']) in pad_roots
  res.append({'net':net,'pad_count':len(pp),'components':list(parts.values()),'zone_islands':zone_entries})
 return res

if __name__=='__main__':
 D=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(D/'mainboard_revD.kicad_pcb'));g=graph(b)
 for net,count in [('3V3_AON',27),('GND',77),('SENS_VIO_1V8',11)]:
  r=next(x for x in g if x['net']==net)
  if r['pad_count']!=count or len(r['components'])!=1:raise RuntimeError(('power graph failure',net,r))
 gr=next(x for x in g if x['net']=='GND')
 if not all(z['root_matches_a_pad_component'] for z in gr['zone_islands'] if z['layer']=='In4.Cu'):raise RuntimeError('floating In4 ground')
 (D/'physical_graph.json').write_text(json.dumps(g,indent=2))
 print({r['net']:len(r['components']) for r in g if len(r['components'])>1})
