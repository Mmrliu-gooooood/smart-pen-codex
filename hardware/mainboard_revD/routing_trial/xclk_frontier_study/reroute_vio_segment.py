from pathlib import Path
import pcbnew as p,json,shutil
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'channel_v2.kicad_pcb'));changed={}
for t in list(b.GetTracks()):
 if t.GetClass()!='PCB_TRACK' or t.GetNetname()!='SENS_VIO_1V8' or t.GetLayer()!=p.B_Cu:continue
 lo=min(p.ToMM(t.GetStart().y),p.ToMM(t.GetEnd().y));hi=max(p.ToMM(t.GetStart().y),p.ToMM(t.GetEnd().y))
 if lo>=43.15-1e-8 and hi<=53.15+1e-8:
  assert t.GetWidth()==p.FromMM(.15);changed[t.m_Uuid.AsString()]={'net':'SENS_VIO_1V8','old_layer':'B.Cu','new_layer':'In2.Cu','start':[p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y)],'end':[p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y)]};b.Delete(t)
assert len(changed)>1
points=[(8.85,43.15),(9.5,43.8),(9.5,47.75),(10.2,48.45),(10.2,51.8),(8.85,53.15)];expected={}
for a,z in zip(points,points[1:]):
 t=p.PCB_TRACK(b);t.SetNet(b.FindNet('SENS_VIO_1V8'));t.SetLayer(p.In2_Cu);t.SetWidth(p.FromMM(.15));t.SetStart(p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1])));t.SetEnd(p.VECTOR2I(p.FromMM(z[0]),p.FromMM(z[1])));expected[t.m_Uuid.AsString()]='SENS_VIO_1V8';b.Add(t)
name='vio_inner_detour';p.SaveBoard(str(D/(name+'.kicad_pcb')),b);b=p.LoadBoard(str(D/(name+'.kicad_pcb')));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(D/(name+'.kicad_pcb')),b);b=p.LoadBoard(str(D/(name+'.kicad_pcb')));actual={t.m_Uuid.AsString():t.GetNetname() for t in b.GetTracks()};assert all(actual.get(k)==v for k,v in expected.items()),'STOP unexpected migrated net'
for ext in ['.kicad_pro','.kicad_dru']:shutil.copy2(D/('channel_v2'+ext),D/(name+ext))
(D/(name+'_changes.json')).write_text(json.dumps(changed,indent=2));print('migrated segments',len(changed))

(D/'vio_inner_detour_expected_new_nets.json').write_text(json.dumps(expected,indent=2))
