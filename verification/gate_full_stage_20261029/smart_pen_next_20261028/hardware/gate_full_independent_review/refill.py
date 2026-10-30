from pathlib import Path
import os,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache';os.environ['XDG_DATA_HOME']='/tmp/rf-independent/data'
import pcbnew as p
D=Path(__file__).resolve().parent;f=D/'native_snapshot/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f))
def filled(b):
 out=[]
 for z in b.Zones():
  if z.GetIsRuleArea():continue
  for l in z.GetLayerSet().Seq():
   q=z.GetFilledPolysList(l)
   out.append((z.m_Uuid.AsString(),int(l),q.Format()))
 return out
# Serialize polygon chains through native numeric vertices; no Dk/default assumptions.
def filled(b):
 out=[]
 for z in b.Zones():
  if z.GetIsRuleArea():continue
  for l in z.GetLayerSet().Seq():
   q=z.GetFilledPolysList(l);out.append((z.m_Uuid.AsString(),int(l),str(q.Format())))
 return out
before=f.read_bytes();a=filled(b);p.ZONE_FILLER(b).Fill(b.Zones());c=filled(b)
O=D/'guard_boards';O.mkdir(exist_ok=True);dest=O/'fresh_refill.kicad_pcb';p.SaveBoard(str(dest),b)
if a!=c:raise RuntimeError('Fresh fill changes actual polygon data; re-audit changed successor required')
print(json.dumps({'pcb_sha256':hashlib.sha256(before).hexdigest(),'same_filled_polygon_native_serialization':True,'zone_layer_count':len(a),'fixture_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()},indent=2))
