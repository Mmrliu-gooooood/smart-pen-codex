from pathlib import Path
import pcbnew as p,json,shutil
D=Path(__file__).resolve().parent;S=D.parent/'backbias6_review';b=p.LoadBoard(str(S/'mainboard_revD.kicad_pcb'));changes=[];expected={}
def xy(q):return [p.ToMM(q.x),p.ToMM(q.y)]
def pt(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
for t in list(b.GetTracks()):
 uid=t.m_Uuid.AsString();net=t.GetNetname();a=xy(t.GetStart());z=xy(t.GetEnd())
 if uid=='9449df8a-f5b4-418d-827f-4d180c8745ef':changes.append({'removed_uuid':uid,'old_start':a,'old_end':z});b.Delete(t);continue
 if uid=='bb60773d-d053-47c2-b637-49b06ad3b32f':changes.append({'uuid':uid,'old_start':a,'old_end':z,'new_end':[10.9,23]});t.SetEnd(pt(10.9,23));continue
 if uid=='1a248b9c-c814-4672-9d57-ceece9eebe6a':changes.append({'uuid':uid,'old_start':a,'old_end':z,'new_start':[10.65,26]});t.SetStart(pt(10.65,26));continue
 if net in ['GND','CAM_SDA'] and min(a[1],z[1])>=23 and max(a[1],z[1])<=26 and max(a[0],z[0])>9.5:
  changes.append({'removed_uuid':uid,'net':net,'type':t.GetClass(),'start':a,'end':z});b.Delete(t)
def track(net,layer,points):
 for a,z in zip(points,points[1:]):
  t=p.PCB_TRACK(b);t.SetNet(b.FindNet(net));t.SetLayer(layer);t.SetWidth(p.FromMM(.15));t.SetStart(pt(*a));t.SetEnd(pt(*z));expected[t.m_Uuid.AsString()]=net;b.Add(t)
def via(net,x,y):
 v=p.PCB_VIA(b);v.SetNet(b.FindNet(net));v.SetPosition(pt(x,y));v.SetWidth(p.F_Cu,p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);expected[v.m_Uuid.AsString()]=net;b.Add(v)
via('GND',10.3,25.15);track('GND',p.F_Cu,[(10.35,22.05),(10.85,22.55),(10.85,24.5),(10.3,25.05),(10.3,25.15)]);track('GND',p.F_Cu,[(10.325,24),(10.85,24)]);track('GND',p.F_Cu,[(9,25.25),(10.2,25.25),(10.3,25.15)])
via('CAM_SDA',10.2,23);track('CAM_SDA',p.B_Cu,[(10.9,23),(10.2,23)]);track('CAM_SDA',p.In2_Cu,[(10.2,23),(9.6,23.6),(9.6,26),(10.65,26)])
name='channel_v2_guarded';p.SaveBoard(str(D/(name+'.kicad_pcb')),b);b=p.LoadBoard(str(D/(name+'.kicad_pcb')));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(D/(name+'.kicad_pcb')),b)
actual={t.m_Uuid.AsString():t.GetNetname() for t in b.GetTracks()};assert all(actual.get(k)==v for k,v in expected.items()), 'new net mismatch after reload'
(D/'channel_v2_expected_new_nets.json').write_text(json.dumps(expected,indent=2))
for ext in ['.kicad_pro','.kicad_dru']:shutil.copy2(S/('mainboard_revD'+ext),D/(name+ext))
(D/'fp-lib-table').write_text((S/'fp-lib-table').read_text().replace('${KIPRJMOD}/','${KIPRJMOD}/../backbias6_review/'))
(D/'channel_v2_changes.json').write_text(json.dumps(changes,indent=2))
