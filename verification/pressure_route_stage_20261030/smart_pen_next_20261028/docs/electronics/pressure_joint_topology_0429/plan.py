import geometry as g,json
p=g.p;F=p.F_Cu;B=p.B_Cu;I=p.In3_Cu;N='NIB_CONTACT_N';S='STRAP_GPIO3'
def tr(n,l,ps,w=.15):return[g.track(n,l,a,b,w)for a,b in zip(ps,ps[1:])]
def vi(n,pt):
 v=g.via(n,pt);v.SetWidth(F,450000);v.SetDrill(200000);return v
# Complete STRAP graph declared; preserve all but its exact local escape subgraph.
remove=['f12fdf92-70a3-4027-97c3-79601d921230','d15e2115-6a56-4f15-817e-74e5d889fcbc','3f3343b7-b5e0-44b5-a36e-3356136bbe32','b261b62a-8b85-442c-8bf2-db2a7abedfc0']
g.old=[t for t in g.old if t.m_Uuid.AsString()not in remove]
parts={
 'strap_reconnect':tr(S,F,[(2.575,10.2),(2.15,10.2),(1.65,10.5)])+[vi(S,(1.65,10.5))]+tr(S,I,[(1.65,10.5),(2.4,9.75),(2.4,9.575)]),
 'nib_local':tr(N,F,[(2.575,9.8),(2.15,9.8),(1.85,9.5)])+[vi(N,(1.85,9.5))]+tr(N,B,[(1.85,9.5),(3.475,9.8),(3.475,9.75),(3.325,11.5)]),
 'aon':tr('3V3_AON',B,[(1.675,11.5),(1.3,12.65)],.25)+[g.via('3V3_AON',(1.3,12.65))],
 'capgnd':tr('GND',B,[(5.025,9.75),(5.025,10.4),(4.25,10.75)],.25),
 'contact':tr('CONTACT',B,[(3,52),(3.825,53),(3.825,54.25)],.25),
 'j103gnd':tr('GND',B,[(5.4,52),(5.4,55)],.25)+[g.via('GND',(5.4,55))],
 'nib_long':tr(N,I,[(1.85,9.5),(1.2,9.1),(.6,9.7),(.6,13.5),(1.95,14.85),(1.95,29),(0.8,30.15),(.8,37.5),(1.95,38.65),(1.95,51.8),(1.2,52.55),(1.2,54.25)])+[vi(N,(1.2,54.25))]+tr(N,B,[(1.2,54.25),(2.175,54.25)])
}
for name,items in parts.items():print(name,json.dumps(g.errors(items)))
print('joint',json.dumps(g.errors(sum(parts.values(),[]))))
if __name__=='__main__':
 from pathlib import Path
 import sys,hashlib
 sys.path.insert(0,str(g.R/'hardware/translator_domain_candidate_0130'))
 from finite_copper import build,components,shape
 def req(c,m):
  if not c:raise RuntimeError(m)
 req(hashlib.sha256(g.S.read_bytes()).hexdigest()=='d6c91327a9335a0039c10cd34943664095ca476524b7b5bced8afa4dc0219c22','parenthash')
 allnew=sum(parts.values(),[]);req(not g.errors(allnew),'alljointgeom')
 oldall=list(g.b.GetTracks());req(len([t for t in oldall if t.m_Uuid.AsString()in remove])==4,'exactremove')
 req(all(t.GetNetname()==S for t in oldall if t.m_Uuid.AsString()in remove),'removalsstraponly')
 nodes=build(g.b);graphs={}
 for n in[S,N,'CONTACT']:
  ns=[x for x in nodes[n]if x[0]not in remove]
  ns += [('new'+str(i),False,{l:shape(t,l)for l in g.L if t.IsOnLayer(l)})for i,t in enumerate(allnew)if t.GetNetname()==n]
  graphs[n]=components(ns)
 req(graphs[S]==[['R103.1','U101.8']],'strapcomplete')
 req(graphs[N]==[['C504.1','R503.2','R504.1','U101.7']],'nibcomplete')
 req(graphs['CONTACT']==[['J103.1','R504.2']],'contactcomplete')
 def spec(t):
  v=isinstance(t,p.PCB_VIA)
  return dict(type='via'if v else'track',net=t.GetNetname(),layer='through'if v else g.b.GetLayerName(t.GetLayer()),start=[t.GetStart().x/1e6,t.GetStart().y/1e6],end=[t.GetEnd().x/1e6,t.GetEnd().y/1e6],width=(t.GetWidth(F)if v else t.GetWidth())/1e6,drill=t.GetDrillValue()/1e6 if v else None)
 result={'status':'readonly_joint_plan_not_native','parent_sha256':hashlib.sha256(g.S.read_bytes()).hexdigest(),'removed_strap_uuids':remove,'retained_strap_uuids':[t.m_Uuid.AsString()for t in oldall if t.GetNetname()==S and t.m_Uuid.AsString()not in remove],'geometry_errors':g.errors(allnew),'physical_signal_pad_components':graphs,'objects':[dict(tag=k,**spec(t))for k,ts in parts.items()for t in ts],'core_counts':'not recomputed: plan only, no native refill; inherited AON35/GND68/SENS12 must be preserved','plane_connectivity':'not proven for new AON/GND vias until actual native refill','layers':'long NIB In3 only; no new In1/In4 tracks; all through holes need reference/antipad review'}
 Path(__file__).with_name('plan_result.json').write_text(json.dumps(result,indent=2)+'\n')
 print('complete signal pad graphs',graphs)
