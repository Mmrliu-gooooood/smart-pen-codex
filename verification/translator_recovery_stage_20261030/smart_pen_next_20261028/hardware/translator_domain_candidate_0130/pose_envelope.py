from pathlib import Path
import os,json,math
os.environ['XDG_CONFIG_HOME']='/tmp/transpose0130'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];paths=[R/'hardware/mcu_power_ground_clearance_0109/native/mainboard_revD.kicad_pcb',D/'native/mainboard_revD.kicad_pcb'];results=[]
for path in paths:
 b=p.LoadBoard(str(path));ff=[f for f in b.GetFootprints()if f.GetReference()in['C207','C208']];pads=[];courtyard=[];models=[];parts=[]
 for f in ff:
  parts.append((f.GetValue(),str(f.GetFPID().GetLibNickname()),str(f.GetFPID().GetLibItemName()),f.GetLayer(),f.GetOrientationDegrees()))
  for q in f.Pads():pads.append((q.GetPosition().x,q.GetPosition().y,q.GetSize().x,q.GetSize().y,q.GetOrientationDegrees(),q.GetLayerSet().FmtHex(),q.GetShape()))
  for x in f.GraphicalItems():
   if x.GetLayer()==p.F_CrtYd:courtyard.append((str(x.GetShape()),x.GetStart().x,x.GetStart().y,x.GetEnd().x,x.GetEnd().y,x.GetWidth()))
  for x in f.Models():models.append((x.m_Filename,x.m_Offset.x,x.m_Offset.y,x.m_Offset.z,x.m_Scale.x,x.m_Scale.y,x.m_Scale.z))
 results.append(dict(pads=sorted(pads),courtyard=sorted(courtyard),models=sorted(models),parts=sorted(parts)))
if results[0]!=results[1]:raise RuntimeError('aggregate nominal mechanical occupancy changed')
old=math.hypot(8.1125-2,64.025-65.775);new=math.hypot(8.1125-10,64.025-65.775)
print(json.dumps(dict(status='NOMINAL_PAIR_OCCUPANCY_ONLY_NO_REAL_ASSEMBLY_QUALIFICATION',two_cap_value_package_orientation_identical=True,aggregate_actual_pad_courtyard_model_geometry_unchanged=True,pad_items=len(results[0]['pads']),courtyard_items=len(results[0]['courtyard']),models=results[0]['models'],TCA_cap_to_supply_pad_straight_distance_mm=dict(before_each=old,after_each=new),new_routed_path_centerline_mm=1.1125+1.75+.775,limits=['Same footprint/model occupancy is not measurement of actual vendor height or mounting process.','No shorter physical loop inductance or cap effective capacitance guarantee from Euclidean distance.','C207/C208 net identities never exchanged; only two identical nominal packages translated.']),indent=2))
