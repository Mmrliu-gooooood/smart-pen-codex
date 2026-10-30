from pathlib import Path
import json,os
D=Path(__file__).resolve().parent;R=D.parents[2]
source=R/'hardware/dvp_role_first_group_planner/analysis'
core=(source/'router_core_input.py').read_text().replace("D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'))", "b=p.LoadBoard(str(D.parent/'native/mainboard_revD.kicad_pcb'))")
core=core.replace('vb[round(10.5/STEP):,round(40/STEP):round(88/STEP)]=True','pass # corridor assignment, no inherited arbitrary via ban')
exec(compile(core,str(source/'router_core_input.py'),'exec'))
exec(compile((source/'cpp_search.py').read_text(),str(source/'cpp_search.py'),'exec'))
assignment={f'SENS_D{i}':(0 if i<4 else 1,[13.5,13.2,12.9,12.6][i%4])for i in range(8)}
assignment.update({n:(2,x)for n,x in zip(['SENS_PCLK','SENS_VSYNC','SENS_HREF','SENS_EXTCLK'],[13.5,13.2,12.9,12.6])})
order=[f'SENS_D{i}'for i in range(8)]+['SENS_PCLK','SENS_VSYNC','SENS_HREF','SENS_EXTCLK']
removed=[]
# Explicit grouped source fanout: each .45/.20 via is below its own bottom-row pad;
# put ALL group vias in the native geometry before any path, rather than greedily blocking later source exits.
seed=[]
for net,ref,yy in [(f'SENS_D{i}','U201',37.95)for i in range(4,8)]+[(n,'U202',49.9)for n in ['SENS_PCLK','SENS_VSYNC','SENS_HREF']]+[('SENS_EXTCLK','U203',59.95)]:
 pad=next(q for f in b.GetFootprints()if f.GetReference()==ref for q in f.Pads()if q.GetNetname()==net);a=xy(pad.GetPosition());z=(a[0],yy)
 t=p.PCB_TRACK(b);t.SetStart(pt(a));t.SetEnd(pt(z));t.SetWidth(p.FromMM(.15));t.SetLayer(p.F_Cu);t.SetNet(b.FindNet(net));b.Add(t)
 v=p.PCB_VIA(b);v.SetPosition(pt(z));v.SetWidth(p.F_Cu,p.FromMM(.45));v.SetDrill(p.FromMM(.2));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(b.FindNet(net));b.Add(v);seed.append({'net':net,'pad_xy':a,'via_xy':z})
(D/'explicit_source_fanout.json').write_text(json.dumps(seed,indent=2))
result=[]
for net in order:
 obs,vb=masks(net,.15)
 obs[:,:,2401:]=True;vb[:,2360:]=True
 for other,(ol,ox) in assignment.items():
  if other!=net:
   sy=(38.0+.65*(int(other[-1])%4)) if other.startswith('SENS_D') else {'SENS_PCLK':50.2,'SENS_VSYNC':50.5,'SENS_HREF':50.8,'SENS_EXTCLK':59.5}[other]
   copper_capsule(obs[ol],(ox,sy),(ox,60),.3)
   copper_capsule(vb,(ox,sy),(ox,60),.45)
 # Source-local entry tongues reserve trace AND through-via finite clearance for every future bus port.
 
 labels=[f.GetReference()+'.'+q.GetNumber()for f in b.GetFootprints()for q in f.Pads()if q.GetNetname()==net and f.GetReference().startswith('U20')]
 part=next(x for x in parts(net,labels)if any(z in labels for z in x[1]));starts={a for a in anchors(part,obs)if a[2]<2390}
 k,x=assignment[net];goal=(k,round(x/STEP),2400);goals={goal}if not obs[goal]else set()
 path,meta=cpp_search(starts,goals,obs,vb)
 item={'net':net,'assignment':[b.GetLayerName(layers[k]),x,60],'found':path is not None,'meta':meta,'source_labels':labels,'start_count':len(starts),'goal_count':len(goals)}
 if path is not None:
  item['path']=[[b.GetLayerName(layers[k]),x*STEP,y*STEP]for k,x,y in path];add(net,path,.15)
 result.append(item);(D/'progress.json').write_text(json.dumps({'status':'NEW_PLACEMENT_SOURCE_FANOUT_ONLY_ALL_OTHER_NETS_UNROUTED','temporarily_removed_USB':removed,'results':result},indent=2));print(net,item['found'],str(meta),flush=True)
 if path is None:break
p.SaveBoard(str(D/'source_only_NOT_COMPLETE.kicad_pcb'),b)
