from pathlib import Path
import os,json,hashlib,shutil,subprocess
os.environ['XDG_CONFIG_HOME']='/tmp/pen-layout-config';os.environ['XDG_CACHE_HOME']='/tmp/pen-layout-cache';os.environ['XDG_DATA_HOME']='/tmp/pen-layout-data'
import pcbnew as p
D=Path(__file__).resolve().parent;S=D.parent/'j202_low_speed_reference_candidate/native';N=D/'native'
b=p.LoadBoard(str(S/'mainboard_revD.kicad_pcb'));c=p.LoadBoard(str(N/'mainboard_revD.kicad_pcb'))
changes=json.loads((D/'placement_changes.json').read_text())['changed']
def fpmap(board):return {f.GetReference():f for f in board.GetFootprints()}
def contract(f):return {'value':f.GetValue(),'footprint':[f.GetFPID().GetLibNickname(),f.GetFPID().GetLibItemName()],'pads':sorted((q.GetNumber(),q.GetNetname())for q in f.Pads())}
a,z=fpmap(b),fpmap(c)
if set(a)!=set(z) or len(z)!=102:raise RuntimeError('REF_DRIFT')
for r in a:
 if contract(a[r])!=contract(z[r]):raise RuntimeError('SOURCE_PIN_NET_DRIFT '+r)
 q,t=a[r],z[r];same=q.GetPosition()==t.GetPosition()and q.GetOrientationDegrees()==t.GetOrientationDegrees()and q.GetLayer()==t.GetLayer()
 if same!=(r not in changes):raise RuntimeError('UNLISTED_OR_MISSING_PLACEMENT_DELTA '+r)
 if r in changes:
  v=changes[r]
  if [t.GetPosition().x/1e6,t.GetPosition().y/1e6]!=v['after_xy'] or t.GetOrientationDegrees()!=v['after_angle'] or t.GetLayerName()!=v['after_layer']:raise RuntimeError('DELTA_TARGET '+r)
for f in S.rglob('*'):
 if f.is_file() and f.name!='mainboard_revD.kicad_pcb':
  g=N/f.relative_to(S)
  if not g.is_file() or f.read_bytes()!=g.read_bytes():raise RuntimeError('SOURCE_OR_RULE_BYTES_DRIFT '+str(f))
if len(list(c.GetTracks())):raise RuntimeError('PLACEMENT_DERIVATIVE_HAS_ROUTING')
for zz in c.Zones():
 if not zz.GetIsRuleArea():
  for l in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]:
   if zz.IsOnLayer(l)and zz.GetFilledPolysList(l).OutlineCount():raise RuntimeError('UNEXPECTED_FILLED_COPPER')
coll=[];fs=list(z.values())
for f in fs:f.BuildCourtyardCaches()
for i,f in enumerate(fs):
 for g in fs[:i]:
  if f.GetLayer()!=g.GetLayer():continue
  q=p.SHAPE_POLY_SET();q.BooleanIntersection(f.GetCourtyard(f.GetLayer()),g.GetCourtyard(g.GetLayer()))
  if q.Area()>1:coll.append([f.GetReference(),g.GetReference()])
if coll:raise RuntimeError('COURTYARD_OVERLAP '+str(coll))
r=json.loads((D/'drc_strict.json').read_text())
if r['violations']or r['schematic_parity']or len(r['unconnected_items'])!=274:raise RuntimeError('DRC_STATUS_DRIFT')
exe=Path(shutil.which('kicad-cli')).resolve();out={'status':'PLACEMENT_ONLY_NOT_ELECTRICAL_SUCCESSOR','baseline_sha256':hashlib.sha256((S/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'placement_sha256':hashlib.sha256((N/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'same_ref_value_footprint_pad_net_count':102,'changed_footprints':len(changes),'all_other_source_files_byte_identical':True,'no_old_copper_or_fill_retained':True,'courtyard_overlaps':coll,'strict_drc_counts':[0,274,0],'kicad_path':str(exe),'kicad_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'version':subprocess.check_output([str(exe),'version'],text=True).strip(),'command':['kicad-cli','pcb','drc','--all-track-errors','--format','json','--schematic-parity','-o','drc_strict.json','native/mainboard_revD.kicad_pcb'],'no_electrical_continuity_claim':True}
print(json.dumps(out,indent=2))
