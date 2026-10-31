from pathlib import Path
import os,sys,json,hashlib,math
os.environ.update(XDG_CONFIG_HOME='/tmp/newreconstruct/config',XDG_CACHE_HOME='/tmp/newreconstruct/cache',XDG_DATA_HOME='/tmp/newreconstruct/data')
import pcbnew as p
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D/'review_dependencies'));from finite_copper import build,components
from native_polygon import native_fractured_once
f=D/'data8_review_native/mainboard_revD.kicad_pcb';a=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(f));prior=a;at={t.m_Uuid.AsString():t for t in a.GetTracks()};bt={t.m_Uuid.AsString():t for t in b.GetTracks()};checks={}
def req(k,v):
 checks[k]=bool(v)
 if not v:raise RuntimeError(k)
def xy(v):return[v.x,v.y]
def raw(t):return{'net':t.GetNetname(),'layer':t.GetLayer(),'start':xy(t.GetStart()),'end':xy(t.GetEnd()),'width':t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),'drill':t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None}
req('retained_copper_exact',all(raw(t)==raw(bt[u])for u,t in at.items()if u in bt))
added=[t for u,t in bt.items()if u not in at];removed=[u for u in at if u not in bt]
req('C104_original_direct_and_ground_exact',all(u in bt and raw(at[u])==raw(bt[u])for u in ['11d26ef2-133b-41cb-8242-f0750c446f96','4b070c1d-13f5-48c3-a7dc-442af935bad8','6938faac-6324-49cf-90da-fc988559d16b','47b32f57-9185-4b15-9749-eae864f977ff','39c7d991-8635-4232-90dd-155b6366eb15']))
A=build(a);B=build(b);changes={}
for n,v in A.items():
 old=components(v);new=components(B[n]);expected=[sorted(sum(old,[]))]if n in ['CAM_D'+str(i)for i in range(8)]else old
 req('physical_partition_'+n,new==expected)
 if old!=new:changes[n]={'before':old,'after':new}
cores={n:len(next(x for x in components(B[n])if anchor in x))for n,anchor in [('3V3_AON','J106.2'),('GND','J106.3'),('SENS_VIO_1V8','J202.23')]};req('cores',cores=={'3V3_AON':41,'GND':94,'SENS_VIO_1V8':12})
fa={x.GetReference():x for x in a.GetFootprints()};fb={x.GetReference():x for x in b.GetFootprints()};poses={}
for ref,x in fa.items():
 y=fb[ref];old=[*xy(x.GetPosition()),x.GetOrientationDegrees(),x.GetLayer()];new=[*xy(y.GetPosition()),y.GetOrientationDegrees(),y.GetLayer()]
 if old!=new:poses[ref]={'old':old,'new':new}
 req('value_'+ref,x.GetValue()==y.GetValue())
 xp={q.GetNumber():(q.GetNetname(),q.GetSize().x,q.GetSize().y,q.GetLayerSet().FmtHex())for q in x.Pads()};yp={q.GetNumber():(q.GetNetname(),q.GetSize().x,q.GetSize().y,q.GetLayerSet().FmtHex())for q in y.Pads()};req('pad_contract_'+ref,xp==yp)
req('only_two_poses',set(poses)=={'R101','R503'})
req('R101_pose',xy(fb['R101'].GetPosition())==[2100000,20000000]);req('R503_pose',xy(fb['R503'].GetPosition())==[8000000,16500000])
plane_diffs=[]
for za,zb in zip(prior.Zones(),b.Zones()):
 if za.GetIsRuleArea():continue
 x=native_fractured_once(za.GetFilledPolysList(za.GetLayer()));y=native_fractured_once(zb.GetFilledPolysList(zb.GetLayer()));q=p.SHAPE_POLY_SET();q.BooleanSubtract(x,y);r=p.SHAPE_POLY_SET();r.BooleanSubtract(y,x)
 if q.Area()or r.Area():plane_diffs.append([za.GetLayer(),q.Area()/1e12,r.Area()/1e12])
req('baseline_plane_delta_limited_to_In1_In2_In4',set(x[0]for x in plane_diffs)=={p.In1_Cu,p.In2_Cu,p.In4_Cu})
metrics={}
for n in sorted({t.GetNetname()for t in added}):
 ts=[t for t in added if t.GetNetname()==n and not isinstance(t,p.PCB_VIA)];vs=[t for t in added if t.GetNetname()==n and isinstance(t,p.PCB_VIA)];lens=[t.GetLength()/1e6 for t in ts]
 metrics[n]={'new_track_count':len(ts),'new_via_count':len(vs),'total_new_copper_centerline_mm':sum(lens),'shorter_than_0_1mm_count':sum(x<.1 for x in lens),'shorter_than_0_05mm_count':sum(x<.05 for x in lens),'minimum_segment_mm':min(lens)if lens else None,'length_by_layer_mm':{b.GetLayerName(l):sum(t.GetLength()/1e6 for t in ts if t.GetLayer()==l)for l in sorted({t.GetLayer()for t in ts})},'widths_mm':sorted({t.GetWidth()/1e6 for t in ts})}
r={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'checks':checks,'physical_changes':changes,'cores':cores,'poses':poses,'added':{t.m_Uuid.AsString():raw(t)for t in added},'removed':{u:raw(at[u])for u in removed},'metrics':metrics,'filled_plane_delta_vs_recovered_4d7d':plane_diffs,'metric_scope':'New conductor totals are not propagation delay or receiver timing; source/bias branches and through-via stubs remain. No PCLK matching claim: PCLK still physically incomplete.'};(D/('final_verification_optimized.json'if not __debug__ else'final_verification.json')).write_text(json.dumps(r,indent=2));print(json.dumps({'checks':len(checks),'cores':cores,'added':len(added),'removed':len(removed),'metrics':metrics},indent=2))
