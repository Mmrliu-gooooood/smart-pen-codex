from pathlib import Path
import os,json,hashlib
os.makedirs('/tmp/f27pose0156',exist_ok=True);os.environ['XDG_CONFIG_HOME']='/tmp/f27pose0156';import pcbnew as p
O=Path(__file__).resolve().parent;W=O.parent;q=W/'reconstruction_receive_margin_mechanics_20261031_0305/selected_native.kicad_pcb';sha=hashlib.sha256(q.read_bytes()).hexdigest()
if sha!='d8550195b14521806a14654c4bdeba0a6d533b0aa536b473919481da2b9d6e5b':raise RuntimeError('selected native')
b=p.LoadBoard(str(q));rows={f.GetReference():{'xy':[f.GetPosition().x/1e6,f.GetPosition().y/1e6],'angle_deg':f.GetOrientationDegrees(),'side':f.GetLayerName(),'value':f.GetValue()}for f in b.GetFootprints()}
if len(rows)!=103:raise RuntimeError('all103')
(O/'native_pose_evidence.json').write_text(json.dumps({'sha256':sha,'rows':rows,'nominal_native_thickness_mm':b.GetDesignSettings().GetBoardThickness()/1e6,'CAD_thickness_budget_mm':.93},indent=2)+'\n')
