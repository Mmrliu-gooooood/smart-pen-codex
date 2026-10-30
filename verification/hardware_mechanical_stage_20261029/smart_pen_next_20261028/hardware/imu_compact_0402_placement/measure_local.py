from pathlib import Path
import pcbnew as p,json,math,hashlib
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'mainboard_revD.kicad_pcb'));ts={t.m_Uuid.AsString():t for t in b.GetTracks()};rows=json.loads((D/'new_local_routes.json').read_text());fps={f.GetReference():f for f in b.GetFootprints()}
def req(ok,msg):
 if not ok:raise RuntimeError(msg)
for r in rows:
 t=ts[r['uuid']];req(t.GetNetname()==r['net'],'net identity')
 if r['type']=='track':req([t.GetStart().x/1e6,t.GetStart().y/1e6]==r['a']and[t.GetEnd().x/1e6,t.GetEnd().y/1e6]==r['z']and t.GetWidth()==round(r['width']*1e6),'actual segment geometry')
def branch(name,net,points):
 out=[]
 for a,z in zip(points,points[1:]):
  hits=[r for r in rows if r['type']=='track'and r['net']==net and((r['a']==list(a)and r['z']==list(z))or(r['z']==list(a)and r['a']==list(z)))];req(len(hits)==1,'missing declared path '+name);r=hits[0];out.append({'uuid':r['uuid'],'length_mm':math.dist(a,z),'width_mm':r['width']})
 return {'name':name,'net':net,'segments':out,'trace_only_length_mm':sum(r['length_mm']for r in out)}
branches=[branch('C501.1 to U501.10 VDDIO','3V3_AON',[(5.72,80.7),(5.17,81.25),(4.7625,81.25)]),branch('C502.1 to U501.9 VDD','3V3_AON',[(5.72,82),(5.47,81.75),(4.7625,81.75)]),branch('shared AON local spine','3V3_AON',[(5.72,80.7),(5.72,82),(5.72,82.8)]),branch('C501.2 to local ground via','GND',[(6.68,80.7),(6.68,81.35),(6.55,81.35)]),branch('C502.2 to local ground via','GND',[(6.68,82),(6.68,81.35),(6.55,81.35)]),branch('U501.8 to chip ground via','GND',[(4.7625,82.25),(5.1,82.25),(5.1,83.2),(5.5,83.6),(5.7,83.6)]),branch('C503.2 to chip ground via','GND',[(6.25,84.5),(5.7,83.95),(5.7,83.6)]),branch('C503.1 to AON via','3V3_AON',[(4.35,84.5),(4.35,85.6)])]
for ref,pin,xy in [('C501','1',(5.72,80.7)),('C502','1',(5.72,82)),('U501','10',(4.7625,81.25)),('U501','9',(4.7625,81.75))]:
 q=next(q for q in fps[ref].Pads()if q.GetNumber()==pin);req((q.GetPosition().x/1e6,q.GetPosition().y/1e6)==xy,'pad endpoint '+ref+'.'+pin)
sep=math.dist((6.55,81.35),(5.7,83.6))
print(json.dumps({'pcb_sha256':hashlib.sha256((D/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'branches':branches,'cap_ground_via_to_chip_ground_via_planar_separation_mm':{'C501':sep,'C502':sep},'previous_independent_mm':{'C501':5.263079,'C502':4.181507},'notes':['Trace lengths exclude pad traversal and plane/via impedance.','Straight-line ground via separation is not actual return-current path or inductance.','0.15 mm remains only a 0.3375 mm ground pad escape; shared ground trunk is 0.25 mm.','No HF/PI qualification, only improved geometry.']},indent=2))
