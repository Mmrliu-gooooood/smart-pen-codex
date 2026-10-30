from pathlib import Path
import hashlib,json,pcbnew
root=Path(__file__).resolve().parents[3];p=root/'hardware/gate_control_output_candidate/mainboard_revD.kicad_pcb'
sha=hashlib.sha256(p.read_bytes()).hexdigest()
if sha!='508e71cbc50437cfb64a28ea8169a8511eb884f8363620e95f58773f368c5b35':raise RuntimeError('Wrong board identity')
b=pcbnew.LoadBoard(str(p));pads={(f.GetReference(),x.GetNumber()):x for f in b.GetFootprints() for x in f.Pads()}
expect={('TP301','1'):'CAM_PWR_EN',('R302','1'):'CAM_PWR_EN',('R302','2'):'CAM_ON',('C302','1'):'CAM_3V3_PRELINK',('C302','2'):'GND',('JP301','1'):'CAM_3V3_PRELINK',('JP301','2'):'CAM_3V3_SW',('J301','1'):'CAM_3V3_SW',('J301','2'):'GND'}
rows=[]
for key,n in expect.items():
 p=pads[key]
 if p.GetNetname()!=n:raise RuntimeError('Pad net mismatch '+str(key))
 rows.append({'reference':key[0],'pad':key[1],'net':n,'centre_mm':[pcbnew.ToMM(p.GetPosition().x),pcbnew.ToMM(p.GetPosition().y)]})
print(json.dumps({'board_sha256':sha,'status':'NO_POWER_UP_AUTHORIZATION; geometry/tool/assembly pending','nodes':rows},indent=2))
