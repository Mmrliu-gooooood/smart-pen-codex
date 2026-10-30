from pathlib import Path
import os,json
os.environ['XDG_CONFIG_HOME']='/tmp/pen-layout-config'
import pcbnew as p
D=Path(__file__).resolve().parent;f=D/'native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f));r=json.loads((D/'route_result.json').read_text());new={x['uuid']for x in r['added']};changes=[];keep=[]
for t in list(b.GetTracks()):
 if t.m_Uuid.AsString()in new or t.GetNetname()!='USB_EN1' or isinstance(t,p.PCB_VIA) or t.GetLayer()!=p.B_Cu:continue
 a,z=t.GetStart(),t.GetEnd();lo,hi=sorted([a.y,z.y]);L,H=55200000,70000000
 if hi<=L or lo>=H:continue
 old=[a.x,a.y,z.x,z.y]
 if lo>=L and hi<=H:
  changes.append({'uuid':t.m_Uuid.AsString(),'action':'remove_old_unused_tail','old_nm':old});b.Remove(t);keep.append(t)
 elif lo<L<hi:
  u=(L-a.y)/(z.y-a.y);v=p.VECTOR2I(round(a.x+u*(z.x-a.x)),L)
  if a.y<L:t.SetEnd(v)
  else:t.SetStart(v)
  changes.append({'uuid':t.m_Uuid.AsString(),'action':'trim_to_new_branch','old_nm':old,'new_nm':[t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y]})
 elif lo<H<hi:
  u=(H-a.y)/(z.y-a.y);v=p.VECTOR2I(round(a.x+u*(z.x-a.x)),H)
  if a.y>H:t.SetEnd(v)
  else:t.SetStart(v)
  changes.append({'uuid':t.m_Uuid.AsString(),'action':'trim_to_new_branch','old_nm':old,'new_nm':[t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y]})
 else:raise RuntimeError('UNEXPECTED_TAIL_SPAN')
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA) and t.m_Uuid.AsString() in new:
  t.SetFrontTentingMode(p.TENTING_MODE_TENTED);t.SetBackTentingMode(p.TENTING_MODE_TENTED)
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);(D/'tail_trim.json').write_text(json.dumps(changes,indent=2)+'\n');print(json.dumps(changes,indent=2))
