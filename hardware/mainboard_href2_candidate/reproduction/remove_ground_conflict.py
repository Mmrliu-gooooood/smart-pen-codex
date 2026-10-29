from pathlib import Path
import pcbnew as p,json,shutil
D=Path(__file__).resolve().parent;b=p.LoadBoard(str(D/'transplanted.kicad_pcb'));expected=json.loads((D.parent/'mainboard_href3_candidate/href3b_candidate_expected_new.json').read_text());removed=[]
for t in list(b.GetTracks()):
 if t.m_Uuid.AsString() in expected:
  if t.GetNetname()!='GND':raise RuntimeError('ground delta ownership mismatch')
  removed.append(t.m_Uuid.AsString());b.Delete(t)
if set(removed)!=set(expected):raise RuntimeError('ground set mismatch')
name='ground_open_research';p.SaveBoard(str(D/(name+'.kicad_pcb')),b);b=p.LoadBoard(str(D/(name+'.kicad_pcb')));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(D/(name+'.kicad_pcb')),b)
for ext in ['.kicad_pro','.kicad_dru']:shutil.copyfile(D/('baseline'+ext),D/(name+ext))
(D/(name+'_removed.json')).write_text(json.dumps(removed,indent=2))
