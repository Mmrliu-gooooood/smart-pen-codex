from pathlib import Path
import json,math,collections
D=Path(__file__).resolve().parent;m=json.loads((D/'strategy1.json').read_text());nets={};collinear=[]
for tag,ts in m['parts'].items():
 for i,t in enumerate(ts):
  n=t['net'];q=nets.setdefault(n,{'tracks':0,'vias':0,'length_mm':0.,'segments_under_0_1mm':0,'layers':{}})
  if t['type']=='via':q['vias']+=1;continue
  le=math.dist(t['a'],t['b']);q['tracks']+=1;q['length_mm']+=le;q['segments_under_0_1mm']+=le<.1-1e-9;l=q['layers'].setdefault(t['layer'],{'tracks':0,'length_mm':0.});l['tracks']+=1;l['length_mm']+=le
  if i:
   a=ts[i-1]
   if a['type']=='track'and a['layer']==t['layer']and a['width']==t['width']and math.dist(a['b'],t['a'])<1e-9:
    v=[a['b'][j]-a['a'][j]for j in[0,1]];w=[t['b'][j]-t['a'][j]for j in[0,1]]
    if abs(v[0]*w[1]-v[1]*w[0])<1e-10 and v[0]*w[0]+v[1]*w[1]>0:collinear.append([tag,i-1,i])
print(json.dumps({'status':'MODEL_COPPER_LENGTH_NOT_ELECTRICAL_TIMING','new_copper_by_net':nets,'strict_collinear_adjacent_candidates':collinear,'limits':['Counts include all new local supply+fanout+long paths, no speculative smoothing','Grid zigzags/short segments retained; no claim of elegant final routing','Collinear compaction already performed within grid paths; changes crossing branch nodes not silently merged']},indent=2))
