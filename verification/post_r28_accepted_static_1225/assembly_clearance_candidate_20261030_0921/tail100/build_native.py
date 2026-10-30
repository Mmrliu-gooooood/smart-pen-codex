from pathlib import Path
import os,shutil,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/tail100';os.environ['XDG_CACHE_HOME']='/tmp/tail100cache'
import pcbnew as p
O=Path(__file__).resolve().parent;W=O.parents[1];src=W/'smart_pen_next_20261028/hardware/ground_recovery_native_0818/native';dst=O/'native_placement_ONLY_NOFAB';shutil.copytree(src,dst,dirs_exist_ok=True);file=dst/'mainboard_revD.kicad_pcb';b=p.LoadBoard(str(file));f=next(f for f in b.GetFootprints()if f.GetReference()=='J202');f.SetPosition(p.VECTOR2I(p.FromMM(7),p.FromMM(88.8)))
for s in b.GetDrawings():
 if s.GetLayerName()=='Edge.Cuts':
  for method,setter in [('GetStart','SetStart'),('GetEnd','SetEnd')]:
   v=getattr(s,method)()
   if v.y==p.FromMM(95):getattr(s,setter)(p.VECTOR2I(v.x,p.FromMM(93.3)))
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(file),b)
(O/'candidate_identity.json').write_text(json.dumps({'status':'PLACEMENT_ONLY_NOFAB_NOT_CONNECTED_OR_ADOPTED','parent_sha256':hashlib.sha256((src/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'changes':['J202 origin(7,90.5)→(7,88.8), same180deg B.Cu','tail Edge.Cuts95→93.3; RF end unchanged−6.5','zone refill only; no deliberate track edits'],'nominal_outline_mm':[14,99.8],'unqualified_outline_tolerance_note':'0.2mm total nominal headroom is NOT proof finished board≤100; manufacturing tolerance must be confirmed'},indent=2))
