import os,sys,json,hashlib
from pathlib import Path
os.environ.update(XDG_CONFIG_HOME='/tmp/pcb_interface_clean_617a/config',XDG_CACHE_HOME='/tmp/pcb_interface_clean_617a/cache',XDG_DATA_HOME='/tmp/pcb_interface_clean_617a/data')
import pcbnew as p
D=Path(__file__).parent;sys.path.insert(0,str(D/'review_dependencies'));from native_blocks import blocks
c=json.loads((D/'native_contract.json').read_text());b=p.LoadBoard(str(D/'parent/mainboard_revD.kicad_pcb'));f=next(f for f in b.GetFootprints()if f.GetReference()=='R230');f.Flip(f.GetPosition(),False);f.SetOrientationDegrees(0);f.SetPosition(p.VECTOR2I(round(c['new_pose'][0]*1e6),round(c['new_pose'][1]*1e6)));j=next(f for f in b.GetFootprints()if f.GetReference()=='J107');t=next(t for t in j.GraphicalItems()if t.m_Uuid.AsString()==c['label_change']['uuid']);t.SetPosition(p.VECTOR2I(7600000,35710000));T=D/'rigid_only_diagnostic.kicad_pcb';p.SaveBoard(str(T),b)
def fp(path):return next(v for _,_,v in blocks(path.read_text())if v.startswith('(footprint')and '(property "Reference" "R230"'in v)
a=fp(T);z=fp(D/'candidate/mainboard_revD.kicad_pcb');res={'exact_whole_footprint_native_rigid_transform':a==z,'no_value_or_pad_net_or_model_edits':a==z,'expected_fp_sha256':hashlib.sha256(a.encode()).hexdigest()};(D/'rigid_transform.json').write_text(json.dumps(res,indent=2));(D/'footprint_delta.sexpr').write_text(a+'\n');print(res)
if a!=z:raise RuntimeError('native rigid transform mismatch')

j=next(v for _,_,v in blocks(T.read_text())if v.startswith('(footprint')and '(property "Reference" "J107"'in v)
jc=next(v for _,_,v in blocks((D/'candidate/mainboard_revD.kicad_pcb').read_text())if v.startswith('(footprint')and '(property "Reference" "J107"'in v)
if j!=jc:raise RuntimeError("J107 exact one text position mismatch")
(D/"label_footprint_delta.sexpr").write_text(j+"\n")
