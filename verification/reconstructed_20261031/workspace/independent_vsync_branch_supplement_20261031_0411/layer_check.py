from pathlib import Path
import os,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/vsync_supplement'
import pcbnew as p
D=Path(__file__).resolve().parent;f=D.parent/'independent_vsync_advisory_20261031_0357/final_candidate/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f));rows=[]
for t in b.GetTracks():
 if t.m_Uuid.AsString()in ['c38d278c-7993-48f5-8f50-9015d1a9bfef','14953b42-2271-42fb-8b2f-59304193614f']:
  rows.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'actual_layer':b.GetLayerName(t.GetLayer()),'dominant_reference':'In1.Cu GND'})
assert len(rows)==2 and all(r['actual_layer']=='In2.Cu'for r in rows)
(D/'layer_correction.json').write_text(json.dumps({'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'rows':rows},indent=2))
