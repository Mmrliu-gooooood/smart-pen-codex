from pathlib import Path
import json,hashlib,os
os.makedirs('/tmp/data8mech0135',exist_ok=True);os.environ['XDG_CONFIG_HOME']='/tmp/data8mech0135';import pcbnew as p
O=Path(__file__).resolve().parent;W=O.parent

def need(v,m):
 if not v:raise RuntimeError(m)
for path,h in [('reconstruction_mechanics_20261031_0053','421ebdb5c1a0ce9bcb6378a525d5c5de2b93a1bc2e9c27dfc076711ba4d4e252'),('reconstruction_r101_repack_20261031_0127','93068b12dacf851e782eb1e853d3378aba7bf986d835b915f6085d8378245ba2')]:
 q=W/path;need(hashlib.sha256((q/'manifest.json').read_bytes()).hexdigest()==h,'frozen geometry evidence')
 for f,sha in json.load(open(q/'manifest.json'))['files'].items():need(hashlib.sha256((q/f).read_bytes()).hexdigest()==sha,'prior artifact')
j=json.load(open(O/'results.json'));need((j['new_tracks'],j['new_outer_tracks'],j['new_vias'],j['removed_count'])==(614,221,23,16),'exact actual delta');need(not j['unqualified_body_Fab_hits'],'new body/Fab intrusion');need(all(not r['body_hits']and not r['Fab_bbox_hits']for r in j['rows']if r['type']=='via'),'underbody new via');ret=[r for r in j['rows']if 'exact_retained_subset_extra_mm2'in r];need(len(ret)==1 and ret[0]['exact_retained_subset_extra_mm2']==0,'single exact old subset');need((O/'results.json').read_bytes()==(O/'results_normal.json').read_bytes(),'normal/O results')
ops={'J104','J108','JP201','JP202','C106','C107'};op_hits=[{'uuid':r['uuid'],**h}for r in j['rows']for h in r['courtyard_hits']if h['ref']in ops];need(not op_hits,'operational native courtyard projection')
base=p.LoadBoard(str(W/'recovery_inputs59_20261031/smart_pen_next_20261028/hardware/data_bias_relocate_1242/native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(O/'selected_native.kicad_pcb'));new={t.m_Uuid.AsString():t for t in b.GetTracks()}
def ident(t):return [t.GetClass(),t.GetNetname(),t.GetLayerName(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None]
original_ground=[]
for t in base.GetTracks():
 if t.GetNetname()!='GND':continue
 a=(t.GetStart().x/1e6,t.GetStart().y/1e6);z=(t.GetEnd().x/1e6,t.GetEnd().y/1e6)
 if isinstance(t,p.PCB_VIA)and a==(6.775,14.8)or not isinstance(t,p.PCB_VIA)and{a,z}=={(6.775,14.8),(6.775,15.8)}:
  need(t.m_Uuid.AsString()in new and ident(t)==ident(new[t.m_Uuid.AsString()]),'original C104 GND changed');original_ground.append({'uuid':t.m_Uuid.AsString(),'identity':ident(t)})
need(len(original_ground)==2,'C104 original ground pair')
courts=[{'uuid':r['uuid'],'net':r['net'],'a':r['a'],**h}for r in j['rows']if r['type']=='via'for h in r['courtyard_hits']];need(len(courts)==10,'ten via/ref court projections')
need(not any(r['net']in ['CAM_SCL','CAM_SDA','CAM_PCLK','CAM_VSYNC','CAM_HREF']for r in j['rows']),'removed reserved stubs not absent')
(O/'verification.json').write_text(json.dumps({'nominal_new_full_envelope_screen_pass':True,'fullbody_R213_retained_projection_not_zero':True,'original_C104_GND_via_and_lead_exact_UUID_geometry':original_ground,'ordinary_via_court_projections':courts,'new_operational_native_courtyard_hits':op_hits,'six_missing_operation_gates_still_open':sorted(ops),'four_context_same_two_pose_evidence_verified':True,'no_new_reserved_receive_SCCB_stubs':True,'electrical_reference_process_review_separate':True,'NOFAB':True,'NO_POWER':True},indent=2)+'\n')
