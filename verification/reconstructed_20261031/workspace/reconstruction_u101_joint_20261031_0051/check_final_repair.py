import geometry_native as g
from pathlib import Path
import json,sys
D=Path(__file__).resolve().parent;v=D/'data8_review_native';r=json.loads((v/'trial.json').read_text());g.b=g.p.LoadBoard(str(v/'mainboard_revD.kicad_pcb'));alltracks=list(g.b.GetTracks());changed=[t for t in alltracks if t.m_Uuid.AsString()in r['changed']];g.old=[t for t in alltracks if t.m_Uuid.AsString()not in r['changed']];g.pads=[q for f in g.b.GetFootprints()for q in f.Pads()];g.MASK_OVERRIDE=D/'r101_proposed_obstacles.json';g.cache={};e=g.errors(changed);r['finite_errors']=e;(D/('final_repair_finite_optimized.json'if not __debug__ else'final_repair_finite.json')).write_text(json.dumps(r,indent=2));print(e)
if e:raise RuntimeError('finite check failed')
