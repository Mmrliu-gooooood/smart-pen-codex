import geometry_native as g,json,hashlib,sys
p=g.p;D=g.D;f=D/'final_candidate/mainboard_revD.kicad_pcb';a=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(f));old={t.m_Uuid.AsString():t for t in a.GetTracks()};new={t.m_Uuid.AsString():t for t in b.GetTracks()};added=[t for u,t in new.items()if u not in old];removed=[u for u in old if u not in new];g.b=b;g.old=[t for u,t in old.items()if u in new];g.pads=[q for z in b.GetFootprints()for q in z.Pads()];g.objs=[];e=g.errors(added)
sys.path.insert(0,str(D/'review_dependencies'));from finite_copper import build,components
av,bv=build(a),build(b);changes={};pe=[]
for n,v in av.items():
 ac=components(v);bc=components(bv[n]);expect=[sorted(sum(ac,[]))]if n in ['CAM_RESET_UART_TX','CAM_PWDN_UART_RX']else ac
 if ac!=bc:changes[n]={'old':ac,'new':bc}
 if bc!=expect:pe.append(n)
cores={n:len(next(c for c in components(bv[n])if anchor in c))for n,anchor in [('GND','J106.3'),('3V3_AON','J106.2'),('SENS_VIO_1V8','J202.23')]}
r={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'added_tracks':sum(t.GetClass()=='PCB_TRACK'for t in added),'added_vias':sum(t.GetClass()=='PCB_VIA'for t in added),'removed':removed,'finite_errors':e,'partition_errors':pe,'changes':changes,'cores':cores};(D/('candidate_check_optimized.json'if not __debug__ else'candidate_check.json')).write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if e or pe or removed or cores!={'GND':94,'3V3_AON':41,'SENS_VIO_1V8':12}:raise RuntimeError('candidate gates fail')
