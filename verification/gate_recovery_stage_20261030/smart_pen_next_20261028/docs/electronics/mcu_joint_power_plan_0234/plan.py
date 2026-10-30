import geometry as q,json,hashlib,uuid
p=q.p;F=p.F_Cu;I=p.In2_Cu;A='3V3_AON';E='CHIP_EN';B='BOOT_N'
removed=['2aadb490-36e4-4205-80e6-e9549156af81','58c0716f-a29f-4c36-afec-dea50e5d7d6b','d6da4b44-2d1f-4eb2-80f4-d7e1ba094da4','ed051403-ad39-4957-8652-ed6b66b442d2','841121a2-d892-481e-bf5e-69ce0966fda7','99ae2d9c-2f71-440b-a2f7-fbb0cbf3b6a5']
old=q.old;q.old=[t for t in old if q.uid(t)not in removed]
def spec(t):
 v=isinstance(t,p.PCB_VIA);return dict(uuid=q.uid(t),type='via'if v else'track',net=t.GetNetname(),layer='through'if v else q.b.GetLayerName(t.GetLayer()),start=[t.GetStart().x/1e6,t.GetStart().y/1e6],end=[t.GetEnd().x/1e6,t.GetEnd().y/1e6],width=(t.GetWidth(F)if v else t.GetWidth())/1e6,drill=t.GetDrillValue()/1e6 if v else None)
results=[];models=[];realuid=q.uid;modelids={};q.uid=lambda t:modelids.get(id(t),realuid(t))
for name,width,axy,ex,bx in [('main25mil',.635,[.65,8.9],1.45,1.95),('branch20mil',.508,[.65,8.8],1.5,1.98)]:
 n=[q.track(A,F,[2.575,7.8],[1.9,7.8],.25),q.track(A,F,[2.575,8.2],[1.9,8.2],.25),q.track(A,F,[1.9,7.8],[1.2,7.8],width),q.track(A,F,[1.9,8.2],[1.2,8.2],width),q.track(A,F,[1.2,7.8],[1.2,8.2],width),q.track(A,F,[1.2,8.2],axy,width),q.via(A,axy),q.track(E,F,[2.575,8.6],[ex,8.6],.15),q.track(E,F,[ex,8.6],[ex,9.4],.15),q.track(E,F,[ex,9.4],[.8,10.05],.15),q.track(E,F,[.8,10.05],[.8,11.85],.15),q.track(B,F,[2.575,9],[bx,9],.15),q.via(B,[bx,9]),q.track(B,I,[bx,9],[1.26,9.7],.15)]
 n[12].SetWidth(F,450000);n[12].SetDrill(200000)
 
 for i,t in enumerate(n):modelids[id(t)]='model/'+name+'/'+str(i)
 models.append(n);results.append(dict(name=name,removed=removed,objects=[spec(t)for t in n],errors=q.errors(n)))
print(json.dumps(dict(status='READ_ONLY_MAX_TWO_JOINT_TOPOLOGIES_NOFAB',base_sha=hashlib.sha256(q.S.read_bytes()).hexdigest(),base_objects=len(old),attempts=results),indent=2))
