from pathlib import Path
import os,json,hashlib
os.makedirs('/tmp/recovery_mech0053',exist_ok=True);os.environ['XDG_CONFIG_HOME']='/tmp/recovery_mech0053';import pcbnew as p
O=Path(__file__).resolve().parent;W=O.parent;R=W/'recovery_inputs59_20261031';q=R/'smart_pen_next_20261028/hardware/data_bias_relocate_1242/native/mainboard_revD.kicad_pcb';sha=hashlib.sha256(q.read_bytes()).hexdigest()
if sha!='4d7d95d253b3c8c994a7f2c4c628087346c271ea290c69aa511ea9a1cb8eadad':raise RuntimeError('actual recovered PCB hash')
b=p.LoadBoard(str(q));rows=[]
for f in b.GetFootprints():
 pads=[]
 for z in f.Pads():
  bb=z.GetBoundingBox();pads.append({'number':z.GetNumber(),'xy_mm':[z.GetPosition().x/1e6,z.GetPosition().y/1e6],'size_mm':[z.GetSize().x/1e6,z.GetSize().y/1e6],'copper_layers':[b.GetLayerName(l)for l in [p.F_Cu,p.B_Cu]if z.IsOnLayer(l)],'bbox_mm':[bb.GetX()/1e6,bb.GetY()/1e6,bb.GetRight()/1e6,bb.GetBottom()/1e6]})
 rows.append({'ref':f.GetReference(),'side':f.GetLayerName(),'pose':[f.GetPosition().x/1e6,f.GetPosition().y/1e6,f.GetOrientationDegrees()],'footprint':f.GetFPIDAsString(),'value':f.GetValue(),'pads':pads})
if len(rows)!=103:raise RuntimeError('103 native refs')
(O/'native_contracts.json').write_text(json.dumps({'pcb_sha256':sha,'source_path':str(q),'rows':sorted(rows,key=lambda r:r['ref'])},indent=2)+'\n')
