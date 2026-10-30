from pathlib import Path
import json,os
D=Path(__file__).resolve().parent;R=D.parents[2]
source=R/'hardware/dvp_role_first_group_planner/analysis'
core=(source/'router_core_input.py').read_text().replace("D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'))", "b=p.LoadBoard(str(R/'hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb'))")
core=core.replace('vb[round(10.5/STEP):,round(40/STEP):round(88/STEP)]=True','pass # corridor assignment, no inherited arbitrary via ban')
exec(compile(core,str(source/'router_core_input.py'),'exec'))
exec(compile((source/'cpp_search.py').read_text(),str(source/'cpp_search.py'),'exec'))
assignment={f'SENS_D{i}':(0 if i<4 else 1,[13.5,13.2,12.9,12.6][i%4])for i in range(8)}
assignment.update({n:(2,x)for n,x in zip(['SENS_PCLK','SENS_VSYNC','SENS_HREF','SENS_EXTCLK'],[13.5,13.2,12.9,12.6])})
order=['SENS_PCLK','SENS_EXTCLK','SENS_VSYNC','SENS_HREF']+[f'SENS_D{i}'for i in range(8)]
# Only explicitly temporary removal of three USB excursion objects; low-speed worker must restore separately.
removed=[];removed_objects=[]
for t in list(b.GetTracks()):
 if t.m_Uuid.AsString()in ['7db29bab-2c54-4a06-b783-e6bfd50624b7','b9011739-3a4d-47b9-8ada-5a4b0a88e728','e9578fa6-43fa-465c-942f-4ffb1a024999']:removed.append(t.m_Uuid.AsString());removed_objects.append(t);b.Remove(t)
result=[]
for net in order:
 obs,vb=masks(net,.15)
 obs[:,:,2401:]=True;vb[:,2360:]=True
 for other,(ol,ox) in assignment.items():
  if other!=net:copper_capsule(obs[ol],(ox,59),(ox,60),.15+.15)
 # Predetermined 1mm entry tongues reserved on all 12 ports prevent earlier paths covering later endpoints.
 
 labels=[f.GetReference()+'.'+q.GetNumber()for f in b.GetFootprints()for q in f.Pads()if q.GetNetname()==net and f.GetReference().startswith('U20')]
 part=next(x for x in parts(net,labels)if any(z in labels for z in x[1]));starts={a for a in anchors(part,obs)if a[2]<2390}
 k,x=assignment[net];goal=(k,round(x/STEP),2400);goals={goal}if not obs[goal]else set()
 path,meta=cpp_search(starts,goals,obs,vb)
 item={'net':net,'assignment':[b.GetLayerName(layers[k]),x,60],'found':path is not None,'meta':meta,'source_labels':labels,'start_count':len(starts),'goal_count':len(goals)}
 if path is not None:
  item['path']=[[b.GetLayerName(layers[k]),x*STEP,y*STEP]for k,x,y in path];add(net,path,.15)
 result.append(item);(D/'progress.json').write_text(json.dumps({'status':'SOURCE_FANOUT_MODEL_ONLY_NOT_COMPLETE_BOARD','temporarily_removed_USB':removed,'results':result},indent=2));print(net,item['found'],str(meta),flush=True)
 if path is None:break
p.SaveBoard(str(D/'source_only_UNRESTORED_USB.kicad_pcb'),b)
