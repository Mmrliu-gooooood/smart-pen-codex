from pathlib import Path
import os,json,sys,hashlib,math
os.environ.update(XDG_CONFIG_HOME='/tmp/newreconstruct/config',XDG_CACHE_HOME='/tmp/newreconstruct/cache',XDG_DATA_HOME='/tmp/newreconstruct/data')
import pcbnew as p
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D/'review_dependencies'));from finite_copper import build,components
A=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));B=p.LoadBoard(str(D/'final_candidate/mainboard_revD.kicad_pcb'));a={t.m_Uuid.AsString():t for t in A.GetTracks()};b={t.m_Uuid.AsString():t for t in B.GetTracks()};checks={}
def req(k,v):
 checks[k]=bool(v)
 if not v:raise RuntimeError(k)
def xy(v):return[v.x,v.y]
def sig(t):return[t.GetNetname(),t.GetLayer(),xy(t.GetStart()),xy(t.GetEnd()),t.GetWidth(p.F_Cu)if t.GetClass()=='PCB_VIA'else t.GetWidth(),t.GetDrillValue()if t.GetClass()=='PCB_VIA'else None]
removed=set(a)-set(b);expected=set(json.loads((D/'ioen_prefilter.json').read_text())['removed'])|set(json.loads((D/'source_joint_preflight.json').read_text())['removed']);req('exact_declared_IO_EN_and_SCCB_replacements',removed==expected);req('every_other_old_copper_object_exact',all(sig(t)==sig(b[u])for u,t in a.items()if u not in removed));added=[t for u,t in b.items()if u not in a];req('only_XCLK_SCCB_IO_EN_additions',set(t.GetNetname()for t in added)=={'CAM_XCLK','CAM_SCL','CAM_SDA','CAM_IO_EN'});req('no_new_power_copper',not any(t.GetNetname()in['GND','3V3_AON','SENS_VIO_1V8']for t in added));req('signal_width_015',all(t.GetClass()=='PCB_VIA'or t.GetNetname()=='GND'or t.GetWidth()==150000 for t in added));req('all_new_vias_declared_common_sizes',all(not t.GetClass()=='PCB_VIA'or(t.GetWidth(p.F_Cu),t.GetDrillValue())in[(450000,200000),(600000,300000)]for t in added));req('signal_vias_045_020',all(not t.GetClass()=='PCB_VIA'or t.GetNetname()=='GND'or(t.GetWidth(p.F_Cu),t.GetDrillValue())==(450000,200000)for t in added))
in2=[t for t in added if not t.GetClass()=='PCB_VIA'and t.GetLayer()==p.In2_Cu];req('bounded_XCLK_In2_window',bool(in2)and all(t.GetNetname()=='CAM_XCLK'and all(3e6<=q.x<=13.4e6 and 49.8e6<=q.y<=52.2e6 for q in[t.GetStart(),t.GetEnd()])for t in in2));req('no_new_groundplane_tracks',all(t.GetClass()=='PCB_VIA'or t.GetLayer()not in[p.In1_Cu,p.In4_Cu]for t in added))
fa={f.GetReference():f for f in A.GetFootprints()};fb={f.GetReference():f for f in B.GetFootprints()};req('same103refs',set(fa)==set(fb)and len(fa)==103)
poses={}
for ref,f in fa.items():
 q=fb[ref];pos,ang=poses.get(ref,(xy(f.GetPosition()),f.GetOrientationDegrees()));req('FP_'+ref,[xy(q.GetPosition()),q.GetOrientationDegrees(),q.GetLayer(),q.GetValue(),q.GetFPID().GetLibItemName()]==[pos,ang,f.GetLayer(),f.GetValue(),f.GetFPID().GetLibItemName()]);oldpads=sorted(f.Pads(),key=lambda v:(v.GetNumber(),v.m_Uuid.AsString()));newpads=sorted(q.Pads(),key=lambda v:(v.GetNumber(),v.m_Uuid.AsString()));ok=len(oldpads)==len(newpads)
 for x,y in zip(oldpads,newpads):
  dx=x.GetPosition().x-f.GetPosition().x;dy=x.GetPosition().y-f.GetPosition().y;theta=math.radians(ang-f.GetOrientationDegrees());xp=round(pos[0]+math.cos(theta)*dx+math.sin(theta)*dy);yp=round(pos[1]-math.sin(theta)*dx+math.cos(theta)*dy)
  ok &= [x.GetNumber(),x.GetNetname(),xy(x.GetSize()),x.GetLayerSet().FmtHex(),x.m_Uuid.AsString()]==[y.GetNumber(),y.GetNetname(),xy(y.GetSize()),y.GetLayerSet().FmtHex(),y.m_Uuid.AsString()]and xy(y.GetPosition())==[xp,yp]and abs(((y.GetOrientationDegrees()-x.GetOrientationDegrees()-(ang-f.GetOrientationDegrees())+180)%360)-180)<1e-6
 req('PAD_'+ref,ok)
an=build(A);bn=build(B);changes={}
for n,v in an.items():
 old=components(v);new=components(bn[n]);expected=[sorted(sum(old,[]))]if n in ['CAM_XCLK']else old;req('PART_'+n,new==expected)
 if old!=new:changes[n]={'before':old,'after':new}
cores={n:len(next(x for x in components(bn[n])if q in x))for n,q in [('GND','J106.3'),('3V3_AON','J106.2'),('SENS_VIO_1V8','J202.23')]};req('cores',cores=={'GND':94,'3V3_AON':41,'SENS_VIO_1V8':12})
for ref in ['R221']:req(ref+'_100k_Bmounted_MCUoutput_U203input_bias',fb[ref].GetValue()=='100k 1%'and all(q.IsOnLayer(p.B_Cu)and not q.IsOnLayer(p.F_Cu)for q in fb[ref].Pads()))
metrics={}
for n in ['CAM_XCLK','CAM_SCL','CAM_SDA','CAM_IO_EN']:
 ts=[t for t in added if t.GetNetname()==n and not t.GetClass()=='PCB_VIA'];vs=[t for t in added if t.GetNetname()==n and t.GetClass()=='PCB_VIA'];metrics[n]={'new_tracks':len(ts),'new_vias':len(vs),'new_centerline_mm':sum(t.GetLength()/1e6 for t in ts),'by_layer_mm':{B.GetLayerName(l):sum(t.GetLength()/1e6 for t in ts if t.GetLayer()==l)for l in sorted({t.GetLayer()for t in ts})},'shorter_than_005mm':sum(t.GetLength()<50000 for t in ts),'shorter_than_01mm':sum(t.GetLength()<100000 for t in ts),'min_segment_mm':min(t.GetLength()/1e6 for t in ts),'via_coordinates_mm':[[t.GetPosition().x/1e6,t.GetPosition().y/1e6]for t in vs]}
r={'sha256':hashlib.sha256((D/'final_candidate/mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'checks':checks,'cores':cores,'physical_changes':changes,'removed':{u:sig(a[u])for u in sorted(removed)},'added':{t.m_Uuid.AsString():sig(t)for t in added},'metrics':metrics,'scope':'Two XCLK physical closures only. Exact declared SCCB/IO_EN copper replaced but their pad partitions unchanged. All pre-existing power tracks/poses/USB retained; new In2 crossing and vias alter plane material/reference and require explicit PDN/SI gates. No operational clock/capture or timing qualification.'};(D/('final_verification_optimized.json'if not __debug__ else'final_verification.json')).write_text(json.dumps(r,indent=2));print(json.dumps({'checks':len(checks),'metrics':metrics,'cores':cores},indent=2))
