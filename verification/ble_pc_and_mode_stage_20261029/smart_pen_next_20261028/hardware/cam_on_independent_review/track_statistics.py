from pathlib import Path
import os,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache'
import pcbnew as p
D=Path(__file__).resolve().parent;out={}
for name,f,r in [('before',D.parent/'gate_control_output_candidate/mainboard_revD.kicad_pcb',D.parent/'gate_control_output_candidate/new_routes.json'),('after',D/'native/mainboard_revD.kicad_pcb',D/'new_routes.json')]:
 b=p.LoadBoard(str(f));ids={x['uuid']for x in json.loads(r.read_text())};ts=[t for t in b.GetTracks()if not isinstance(t,p.PCB_VIA)and t.m_Uuid.AsString()in ids];on=[t for t in ts if t.GetNetname()=='CAM_ON'];out[name]={'pcb_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'new_tracks':len(ts),'new_tracks_shorter_than_100000nm':sum(t.GetLength()<100000 for t in ts),'CAM_ON_tracks':len(on),'CAM_ON_tracks_shorter_than_100000nm':sum(t.GetLength()<100000 for t in on),'CAM_ON_total_length_mm':sum(t.GetLength()for t in on)/1e6}
out['metric']='KiCad native integer-nanometre GetLength threshold, not float math.dist <.1 (which misclassifies borderline .1mm segments due to floating rounding).'
print(json.dumps(out,indent=2))
