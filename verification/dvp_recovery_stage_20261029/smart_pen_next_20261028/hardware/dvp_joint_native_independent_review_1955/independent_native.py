from pathlib import Path
import json,hashlib,collections,os,sys
os.environ.update(XDG_CONFIG_HOME='/tmp/dvp-review1955-config',XDG_CACHE_HOME='/tmp/dvp-review1955-cache',XDG_DATA_HOME='/tmp/dvp-review1955-data')
import pcbnew as p
from finite_copper import build,components,L
D=Path(__file__).resolve().parent;R=D.parents[1];C=D/'native';A=R/'hardware/j202_low_speed_reference_candidate/native';S=R/'hardware/dvp_rotated_group_placement_1835/native'
def req(x,m):
 if not x:raise RuntimeError(m)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
b=p.LoadBoard(str(C/'mainboard_revD.kicad_pcb'));a=p.LoadBoard(str(A/'mainboard_revD.kicad_pcb'));s=p.LoadBoard(str(S/'mainboard_revD.kicad_pcb'))
req(sha(C/'mainboard_revD.kicad_pcb')=='184dce12e82219e5d4bb3e1f20f84cf2bc6e06c1494f5b23862f5e1978024f81','HASH')
source=[]
for f in A.rglob('*'):
 if f.is_file() and f.suffix in ['.kicad_sch','.kicad_sym','.kicad_pro','.kicad_dru']:
  q=C/f.relative_to(A);req(q.is_file()and sha(q)==sha(f),'SOURCE '+str(f));source.append(str(f.relative_to(A)))
rows=json.loads((R/'docs/electronics/dvp_topology_handoff_1852/topology.json').read_text())['rows'];nodes=build(b);chain=[];negative=[]
for row in rows:
 n=row['net'];src=row['translator_pin'];dst='J202.'+row['J202_pin'];cc=components(nodes[n]);req(any(src in c and dst in c for c in cc),'FINITE_CHAIN '+n)
 ts=[t for t in b.GetTracks()if t.GetNetname()==n];chain.append({'net':n,'from':src,'to':dst,'pad_groups':cc,'tracks':sum(not isinstance(t,p.PCB_VIA)for t in ts),'vias':sum(isinstance(t,p.PCB_VIA)for t in ts),'track_length_mm':sum(t.GetLength()/1e6 for t in ts if not isinstance(t,p.PCB_VIA))})
 t=next(t for t in ts if not isinstance(t,p.PCB_VIA));u=t.m_Uuid.AsString();nc=components([x for x in nodes[n]if x[0]!=u]);req(not any(src in c and dst in c for c in nc),'NEGATIVE '+n);negative.append({'net':n,'removed':u,'disconnected':True})
# Confirm native no planes / ground routing instead of estimating nonexistent return vias.
fill=[]
for z in b.Zones():
 if z.GetIsRuleArea():continue
 for l in L:
  if z.IsOnLayer(l) and z.GetFilledPolysList(l).OutlineCount():fill.append([z.GetNetname(),b.GetLayerName(l)])
req(not fill,'UNEXPECTED_REFERENCE')
tracks=list(b.GetTracks());req(len(tracks)==76 and not any(t.GetNetname()in ['GND','3V3_AON','CAM_3V3_SW']for t in tracks),'OBJECT_SCOPE')
def pose(f):return (f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees(),f.GetLayer())
def fs(q):return {f.GetReference():f for f in q.GetFootprints()}
fb,fa,fsrc=fs(b),fs(a),fs(s);changed={k:{'accepted':pose(fa[k]),'candidate':pose(v)}for k,v in fb.items()if pose(v)!=pose(fa[k])};delta=[k for k,v in fb.items()if pose(v)!=pose(fsrc[k])];req(len(changed)==29 and len(delta)==6,'POSES')
drc=json.loads((D/'fresh_drc.json').read_text());counts=[len(drc[k])for k in ['violations','unconnected_items','schematic_parity']];req(counts==[0,262,0],'FRESH_DRC')
pr=json.loads((C/'mainboard_revD.kicad_pro').read_text());ds=pr['board']['design_settings'];req(not ds['drc_exclusions'],'EXCLUSIONS')
out={'status':'TWELVE_LOCAL_CHAINS_STATIC_CHECKED_ONLY_NOFAB','pcb_sha256':sha(C/'mainboard_revD.kicad_pcb'),'source_equal_to_accepted':source,'chains':chain,'finite_copper_negative_tests':negative,'fresh_counts':counts,'pose_changes_6':delta,'pose_changes_29_from_accepted':changed,'filled_reference_polygons':fill,'ground_via_count':0,'power_track_count':0,'return_path_qualification':'NOT POSSIBLE: no planes or ground wiring. Refill and ground return restoration require new assessment.','existing_ignored_severities':[k for k,v in ds['rule_severities'].items()if v=='ignore'],'exclusions':ds['drc_exclusions']}
(D/'independent_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
