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
def sig(t):return[t.GetNetname(),t.GetLayer(),xy(t.GetStart()),xy(t.GetEnd()),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None]
req('all_old_copper_UUIDs_retained',set(a)<=set(b));req('all_old_copper_geometry_exact',all(sig(t)==sig(b[u])for u,t in a.items()));added=[t for u,t in b.items()if u not in a];req('only_SCCB_additions',set(t.GetNetname()for t in added)=={'CAM_SCL','CAM_SDA'});req('no_In2_new_trace',all(isinstance(t,p.PCB_VIA)or t.GetLayer()!=p.In2_Cu for t in added));req('all_new_signal_width_015',all(isinstance(t,p.PCB_VIA)or t.GetWidth()==150000 for t in added));req('new_vias_045_020',all(not isinstance(t,p.PCB_VIA)or(t.GetWidth(p.F_Cu)==450000 and t.GetDrillValue()==200000)for t in added))
fa={f.GetReference():f for f in A.GetFootprints()};fb={f.GetReference():f for f in B.GetFootprints()}
for r,f in fa.items():
 g=fb[r];req('FP_'+r,[xy(f.GetPosition()),f.GetOrientationDegrees(),f.GetLayer(),f.GetValue()]==[xy(g.GetPosition()),g.GetOrientationDegrees(),g.GetLayer(),g.GetValue()]);pad=lambda x:sorted((q.GetNumber(),q.GetNetname(),xy(q.GetPosition()),xy(q.GetSize()),q.GetOrientationDegrees(),q.GetLayerSet().FmtHex())for q in x.Pads());req('PAD_'+r,pad(f)==pad(g))
an=build(A);bn=build(B);changes={}
for n,v in an.items():
 old=components(v);new=components(bn[n]);expected=[sorted(sum(old,[]))]if n in ['CAM_SCL','CAM_SDA']else old;req('PART_'+n,new==expected)
 if old!=new:changes[n]={'before':old,'after':new}
cores={n:len(next(x for x in components(bn[n])if q in x))for n,q in [('GND','J106.3'),('3V3_AON','J106.2'),('SENS_VIO_1V8','J202.23')]};req('cores',cores=={'GND':94,'3V3_AON':41,'SENS_VIO_1V8':12})
metrics={}
for n in ['CAM_SCL','CAM_SDA']:
 ts=[t for t in added if t.GetNetname()==n and not isinstance(t,p.PCB_VIA)];vs=[t for t in added if t.GetNetname()==n and isinstance(t,p.PCB_VIA)];metrics[n]={'new_tracks':len(ts),'new_vias':len(vs),'new_centerline_mm':sum(t.GetLength()/1e6 for t in ts),'by_layer_mm':{B.GetLayerName(l):sum(t.GetLength()/1e6 for t in ts if t.GetLayer()==l)for l in sorted({t.GetLayer()for t in ts})},'shorter_than_005mm':sum(t.GetLength()<50000 for t in ts),'shorter_than_01mm':sum(t.GetLength()<100000 for t in ts),'min_segment_mm':min(t.GetLength()/1e6 for t in ts),'via_coordinates_mm':[[t.GetPosition().x/1e6,t.GetPosition().y/1e6]for t in vs],'retained_branch_network_mm':sum(t.GetLength()/1e6 for t in a.values()if t.GetNetname()==n and not isinstance(t,p.PCB_VIA))}
r={'sha256':hashlib.sha256((D/'final_candidate/mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'checks':checks,'cores':cores,'physical_changes':changes,'added':{t.m_Uuid.AsString():sig(t)for t in added},'metrics':metrics,'scope':'Lengths are added conductor totals, not timing qualification; old feed+pullup branch total is not falsely called pure stub length. All eight data paths and original C104 direct/ground and all power copper exact.'};(D/('final_verification_optimized.json'if not __debug__ else'final_verification.json')).write_text(json.dumps(r,indent=2));print(json.dumps({'checks':len(checks),'metrics':metrics,'cores':cores},indent=2))
