from pathlib import Path
import pcbnew as p,json,hashlib,shutil
D=Path(__file__).resolve().parent;root=D.parent;oldpath=root/'mainboard_revD/routing_trial/xclk5_review/mainboard_revD.kicad_pcb';researchpath=root/'mainboard_revD/routing_trial/href_frontier_study/href_left_source.kicad_pcb'
a=p.LoadBoard(str(oldpath));r=p.LoadBoard(str(researchpath));b=p.LoadBoard(str(D/'baseline.kicad_pcb'))
def sig(t):return(t.GetClass(),t.GetNetname(),t.GetLayer(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth(),t.GetDrillValue() if isinstance(t,p.PCB_VIA) else 0)
x={t.m_Uuid.AsString():t for t in a.GetTracks()};y={t.m_Uuid.AsString():t for t in r.GetTracks()};z={t.m_Uuid.AsString():t for t in b.GetTracks()};removed=x.keys()-y.keys();added=y.keys()-x.keys();changed={k for k in x.keys()&y.keys() if sig(x[k])!=sig(y[k])}
for k in removed|changed:
 if k not in z or sig(z[k])!=sig(x[k]):raise RuntimeError('Cannot transplant overlapping predecessor edit: '+k)
for k in added:
 if k in z:raise RuntimeError('New UUID already present')
expected={}
for k in removed|changed:b.Delete(z[k])
for k in added|changed:
 t=y[k].Duplicate();t.SetNet(b.FindNet(y[k].GetNetname()));b.Add(t);expected[t.m_Uuid.AsString()]=y[k].GetNetname()
name='transplanted';p.SaveBoard(str(D/(name+'.kicad_pcb')),b);b=p.LoadBoard(str(D/(name+'.kicad_pcb')));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(D/(name+'.kicad_pcb')),b)
for ext in ['.kicad_pro','.kicad_dru']:shutil.copyfile(D/('baseline'+ext),D/(name+ext))
(D/'transplant_contract.json').write_text(json.dumps({'old_source_sha256':hashlib.sha256(oldpath.read_bytes()).hexdigest(),'research_sha256':hashlib.sha256(researchpath.read_bytes()).hexdigest(),'removed':sorted(removed),'changed':sorted(changed),'expected':expected},indent=2));print('Removed',len(removed),'changed',len(changed),'added',len(added))
