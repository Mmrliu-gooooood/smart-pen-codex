#!/usr/bin/python3
"""Read-only native geometry; no save, mutation or fabrication output."""
import pcbnew as p,json,hashlib,math,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH=ROOT/'hardware/pressure_joint_native_0433/native/mainboard_revD.kicad_pcb'
PARENT=ROOT/'hardware/imu_j107_clock_native_0405/native/mainboard_revD.kicad_pcb'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
if sha(PATH)!='69d93e9dfa7afd427110a271d7fbdcdcd3a0841d79b502c436a50572849c08cc':raise RuntimeError('candidate changed')
b=p.LoadBoard(str(PATH)); f=next(f for f in b.GetFootprints()if f.GetReference()=='U203');v=next(t for t in b.GetTracks()if isinstance(t,p.PCB_VIA)and t.GetPosition()==p.VECTOR2I(5400000,55000000))
xy=lambda pt:[pt.x/1e6,pt.y/1e6]
def poly(x,l):
 q=p.SHAPE_POLY_SET();x.TransformShapeToPolygon(q,l,0,50,p.ERROR_OUTSIDE);return q
def segdist(c,a,z):
 dx=z.x-a.x;dy=z.y-a.y;t=max(0,min(1,((c.x-a.x)*dx+(c.y-a.y)*dy)/(dx*dx+dy*dy))) if dx*dx+dy*dy else 0
 return math.hypot(c.x-a.x-t*dx,c.y-a.y-t*dy)
def distance(q):
 if q.Contains(v.GetPosition()):return 0
 return min(segdist(v.GetPosition(),q.COutline(i).CPoint(j),q.COutline(i).CPoint((j+1)%q.COutline(i).PointCount()))for i in range(q.OutlineCount())for j in range(q.COutline(i).PointCount()))/1e6
layers=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]; checks=[]
for fp in b.GetFootprints():
 for pad in fp.Pads():
  for l in layers:
   if pad.IsOnLayer(l):
    q=poly(pad,l); gap=distance(q)-.3
    checks.append(dict(pad=fp.GetReference()+'.'+pad.GetNumber(),layer=b.GetLayerName(l),copper_disk_gap_mm=gap,drill_gap_mm=gap+.15,net=pad.GetNetname()))
source=ROOT/'hardware/pressure_joint_native_0433/native/schematic/controls_sccb.kicad_sch'
s=source.read_text(); i=s.index('(property "Reference" "U203"');source_excerpt=s[i:i+600]
out=dict(candidate_sha256=sha(PATH),parent_sha256=sha(PARENT),kicad_version=p.Version(),source_path=str(source.relative_to(ROOT)),source_excerpt=source_excerpt,U203=dict(value=f.GetValue(),footprint=str(f.GetFPID().GetLibItemName()),position=xy(f.GetPosition()),rotation=f.GetOrientationDegrees(),pads=[dict(number=x.GetNumber(),position=xy(x.GetPosition()),size=xy(x.GetSize()),rotation=x.GetOrientationDegrees(),layers=[b.GetLayerName(l)for l in [p.F_Cu,p.B_Cu,p.F_Mask,p.B_Mask,p.F_Paste,p.B_Paste]if x.IsOnLayer(l)],mask_margin=x.GetLocalSolderMaskMargin())for x in f.Pads()]),via=dict(uuid=v.m_Uuid.AsString(),position=xy(v.GetPosition()),size_mm=v.GetWidth(p.F_Cu)/1e6,drill_mm=v.GetDrillValue()/1e6,front_mode=v.GetFrontTentingMode(),back_mode=v.GetBackTentingMode(),from_rules_enum=p.TENTING_MODE_FROM_RULES,front_effective_tented=v.IsTented(p.F_Mask),back_effective_tented=v.IsTented(p.B_Mask),has_soldermask=v.HasSolderMask(),local_margin=v.GetLocalSolderMaskMargin(),board_front_tent=b.GetDesignSettings().m_TentViasFront,board_back_tent=b.GetDesignSettings().m_TentViasBack),all_copper_pad_checks=len(checks),nearest_all_pads=sorted(checks,key=lambda x:x['copper_disk_gap_mm'])[:10],U203_pad_gaps=[x for x in checks if x['pad'].startswith('U203.')],collisions=[x for x in checks if x['copper_disk_gap_mm']<=0])
Path(__file__).with_name('evidence.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['via','nearest_all_pads','collisions']},indent=2))
f2=next(f for f in b.GetFootprints()if f.GetReference()=='R222')
out['R222_opposite_face']={'value':f2.GetValue(),'position':xy(f2.GetPosition()),'rotation':f2.GetOrientationDegrees(),'footprint':str(f2.GetFPID().GetLibItemName()),'graphics':[{'layer':b.GetLayerName(d.GetLayer()),'start':xy(d.GetStart()),'end':xy(d.GetEnd())}for d in f2.GraphicalItems()if isinstance(d,p.PCB_SHAPE)and d.GetLayer()in[p.B_Fab,p.B_CrtYd]],'via_disk_to_nominal_body_gap_mm':.2875,'via_disk_courtyard_penetration_mm':.03,'note':'nominal footprint, not actual purchased resistor tolerance or assembly approval'}
Path(__file__).with_name('evidence.json').write_text(json.dumps(out,indent=2)+'\n')
