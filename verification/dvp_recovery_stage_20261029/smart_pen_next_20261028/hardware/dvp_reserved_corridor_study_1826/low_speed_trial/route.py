from pathlib import Path
D=Path(__file__).resolve().parent
core=(D/'router_core_input.py').read_text().replace('vb[round(10.5/STEP):,round(40/STEP):round(88/STEP)]=True','pass # no old arbitrary strategic via ban')
core=core.replace("D/'native/mainboard_revD.kicad_pcb'","D.parents[1]/'j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb'")
core=core.replace('rect(vb,7,92,13.9,4,.15)','rect(vb,7,92,13.9,4,.275) # full .225 via radius + .05 nominal reserve')
exec(compile(core,str(D/'router_core_input.py'),'exec'))
exec(compile((D/'cpp_search.py').read_text(),str(D/'cpp_search.py'),'exec'))
basehash=__import__('hashlib').sha256((D.parents[1]/'j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb').read_bytes()).hexdigest()
delete={'7db29bab-2c54-4a06-b783-e6bfd50624b7','b9011739-3a4d-47b9-8ada-5a4b0a88e728','e9578fa6-43fa-465c-942f-4ffb1a024999'}
for t in b.GetTracks():
 if t.GetNetname()=='SENS_TRIG_IN' and not isinstance(t,p.PCB_VIA) and min(t.GetStart().y,t.GetEnd().y)>=86e6:delete.add(t.m_Uuid.AsString())
removed=[];removed_native_objects=[]
for t in list(b.GetTracks()):
 if t.m_Uuid.AsString() in delete:
  removed.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'a':xy(t.GetStart()),'z':xy(t.GetEnd()),'layer':b.GetLayerName(t.GetLayer())});b.Remove(t);removed_native_objects.append(t)
reports=[]
for net in ['USB_EN1','SENS_TRIG_IN']:
 labels=[f.GetReference()+'.'+q.GetNumber()for f in b.GetFootprints()for q in f.Pads()if q.GetNetname()==net]
 pp=parts(net,labels);print(net,[a[1] for a in pp],flush=True)
 if len(pp)!=2:raise RuntimeError('EXPECTED_TWO_COMPONENTS '+str([a[1]for a in pp]))
 obs,vb=masks(net,.15)
 for x in [12.6,12.9,13.2,13.5]:
  for k in range(N):copper_capsule(obs[k],(x,32),(x,89),.3)
  copper_capsule(vb,(x,32),(x,89),.45)
 aa=anchors(pp[0],obs);zz=anchors(pp[1],obs)
 path,info=cpp_search(aa,zz,obs,vb)
 reports.append({'net':net,'start_anchor_count':len(aa),'goal_anchor_count':len(zz),'search':info,'found':path is not None})
 print(reports[-1],flush=True)
 if path is None:
  (D/'route_result.json').write_text(json.dumps({'status':'BOUNDED_FAILED_NOT_CANDIDATE','basehash':basehash,'removed':removed,'reports':reports},indent=2));raise SystemExit(5)
 add(net,path,.15)
 reports[-1]['path']=[[b.GetLayerName(layers[k]),x*STEP,y*STEP]for k,x,y in path]
p.SaveBoard(str(D/'native/mainboard_revD.kicad_pcb'),b)
(D/'route_result.json').write_text(json.dumps({'status':'UNREVIEWED_ROUTED_PENDING_NATIVE_CHECKS','basehash':basehash,'removed':removed,'reports':reports,'added':rows},indent=2))
