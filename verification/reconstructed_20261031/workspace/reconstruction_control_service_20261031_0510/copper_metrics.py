from pathlib import Path
import os,json,hashlib,math
os.environ['XDG_CONFIG_HOME']='/tmp/xclk-metrics'
import pcbnew as p
D=Path(__file__).resolve().parent;a=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(D/'final_candidate/mainboard_revD.kicad_pcb'));aa={t.m_Uuid.AsString():t for t in a.GetTracks()};bb={t.m_Uuid.AsString():t for t in b.GetTracks()};out={}
for n in ['CAM_RESET_UART_TX','CAM_PWDN_UART_RX']:
 def m(ts):
  tr=[t for t in ts if t.GetClass()=='PCB_TRACK'];vs=[t for t in ts if t.GetClass()=='PCB_VIA'];return {'tracks':len(tr),'vias':len(vs),'length_mm':sum(t.GetLength()/1e6 for t in tr),'layers_mm':{b.GetLayerName(l):sum(t.GetLength()/1e6 for t in tr if t.GetLayer()==l)for l in sorted({t.GetLayer()for t in tr})}}
 old=[t for t in aa.values()if t.GetNetname()==n];new=[t for t in bb.values()if t.GetNetname()==n];out[n]={'before_all':m(old),'after_all':m(new),'removed':m([t for t in old if t.m_Uuid.AsString()not in bb]),'added':m([t for t in new if t.m_Uuid.AsString()not in aa])}
r={'sha256':hashlib.sha256((D/'final_candidate/mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'nets':out,'scope':'Conductor inventory lengths, not shortest terminal paths or timing. Changed SCCB lengths/load/RC and IO_EN mux/startup gates remain. Clock centerline and true bias arm separately independently measured.'};(D/'copper_metrics.json').write_text(json.dumps(r,indent=2));print(json.dumps(out,indent=2))
