from geometry import *
N='SENS_VIO_1V8'
def serial(t):
 v=isinstance(t,p.PCB_VIA)
 return dict(type='via'if v else'track',net=t.GetNetname(),layer='through'if v else b.GetLayerName(t.GetLayer()),start=[t.GetStart().x/1e6,t.GetStart().y/1e6],end=[t.GetEnd().x/1e6,t.GetEnd().y/1e6],width=(t.GetWidth(p.F_Cu)if v else t.GetWidth())/1e6,drill=t.GetDrillValue()/1e6 if v else None)
oldpath=R/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb';ob=p.LoadBoard(str(oldpath));reuse=[];orig=[]
for t in ob.GetTracks():
 if t.GetNetname()!=N or min(t.GetStart().y,t.GetEnd().y)<75000000:continue
 if not isinstance(t,p.PCB_VIA)and t.GetLayer()!=p.B_Cu and t.GetLayer()!=p.F_Cu:continue
 s=serial(t);u=via(N,s['start'])if isinstance(t,p.PCB_VIA)else track(N,t.GetLayer(),s['start'],s['end'],s['width']);reuse.append(u);orig.append(dict(uuid=t.m_Uuid.AsString(),**s))
# Shared terminal accesses use already verified local geometry, not the obsolete cap pose.
access=[]
for name,pt in [('C202.1',(10.975,35.9625)),('C204.1',(9.575,47.9625)),('C206.1',(9.575,57.9625)),('U204.1',(3.8875,63.125))]:
 access +=[track(N,p.F_Cu,xy(pm[name]),pt,.25),via(N,pt)]
# Two complete conceptual trees, not a grid search. A uses reused source feeder + In3 spine;
# B uses direct In3 lower fanout and B zigzag upper chain with explicit central layer transition.
A=reuse+access
for x,y in [(10.975,35.9625),(9.575,47.9625),(9.575,57.9625),(3.8875,63.125),(11.05,75.15)]:
 A.append(track(N,p.In3_Cu,(x,y),(6.5,y),.25))
A +=[track(N,p.In3_Cu,(6.5,35.9625),(6.5,75.15),.25)]
B=access+[track(N,p.B_Cu,(1.75,90.5),(1.75,91.2),.25),track(N,p.B_Cu,(1.75,91.2),(4.5,91.2),.25),via(N,(4.5,91.2)),track(N,p.In3_Cu,(4.5,91.2),(4.5,77),.25),track(N,p.In3_Cu,(4.5,77),(6.5,75),.25),track(N,p.In3_Cu,(6.5,75),(6.5,63.125),.25),track(N,p.In3_Cu,(6.5,63.125),(3.8875,63.125),.25),via(N,(6.5,63.125)),track(N,p.B_Cu,(6.5,63.125),(9.575,57.9625),.25),track(N,p.B_Cu,(9.575,57.9625),(9.575,47.9625),.25),track(N,p.B_Cu,(9.575,47.9625),(10.975,35.9625),.25)]
for name,pt in [('R242.2',(8.325,75)),('R243.2',(11.325,75))]:
 B +=[track(N,p.F_Cu,xy(pm[name]),pt,.25),via(N,pt),track(N,p.In3_Cu,pt,(6.5,75),.25)]
rows=[]
for tag,items in [('A_reused_lower_feeder_In3_central_spine',A),('B_In3_lower_fanout_B_upper_zigzag',B)]:
 checks=[dict(index=i,object=serial(t),conflicts=errors([t]))for i,t in enumerate(items)]
 rows.append(dict(topology=tag,whole_candidate_conflicts=errors(items),objects=[serial(t)for t in items],checks=checks,blocked_objects=sum(bool(c['conflicts'])for c in checks),status='REJECTED_COLLISIONS'if any(c['conflicts']for c in checks)else'GEOMETRY_CANDIDATE_NOT_NATIVE_CHECKED'))
result=dict(base_sha=hashlib.sha256(S.read_bytes()).hexdigest(),source_pad_count=sum(q.GetNetname()==N for q in pads),pads=[dict(name=n,position=xy(q),layers=[b.GetLayerName(l)for l in L if q.IsOnLayer(l)],uuid=q.m_Uuid.AsString())for n,q in pm.items()if q.GetNetname()==N],source_existing_objects=[serial(t)for t in old if t.GetNetname()==N],old_source_sha=hashlib.sha256(oldpath.read_bytes()).hexdigest(),reused_lower_subgraph=orig,reuse_conflicts=errors(reuse),candidates=rows)
(D/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(source_pad_count=result['source_pad_count'],reuse_count=len(reuse),reuse_conflicts=len(result['reuse_conflicts']),results=[dict(topology=r['topology'],objects=len(r['objects']),blocked=r['blocked_objects'],conflicts=[c for c in r['checks']if c['conflicts']])for r in rows]),indent=2))
