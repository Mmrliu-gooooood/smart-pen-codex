from pathlib import Path
import subprocess,json
D=Path(__file__).resolve().parent;O=D/'guard_boards';O.mkdir(exist_ok=True)
code=r'''import os,sys,json
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config'
import pcbnew as p
b=p.LoadBoard(sys.argv[1]);case=sys.argv[3];fps={f.GetReference():f for f in b.GetFootprints()}
if case=='remove_input_via':
 t=next(t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetPosition()==p.VECTOR2I(9450000,83900000));b.Remove(t)
elif case=='wrong_old_width':
 from pathlib import Path
 old=p.LoadBoard(str(Path(sys.argv[1]).parent.parent.parent/'gate_input_local_routing/mainboard_revD.kicad_pcb'));ids={t.m_Uuid.AsString()for t in old.GetTracks()}
 t=next(t for t in b.GetTracks() if t.GetNetname()=='3V3_AON'and t.m_Uuid.AsString()in ids and not isinstance(t,p.PCB_VIA));t.SetWidth(p.FromMM(.11))
elif case=='wrong_C501_pad':next(x for x in fps['C501'].Pads() if x.GetNumber()=='1').SetNet(b.FindNet('GND'))
elif case=='MEMS_plane_intrusion':
 z=next(z for z in b.Zones() if not z.GetIsRuleArea() and z.GetLayer()==p.In1_Cu);q=p.SHAPE_POLY_SET(z.GetFilledPolysList(p.In1_Cu));h=p.SHAPE_POLY_SET();h.NewOutline()
 for x,y in [(3.5,81.5),(4,81.5),(4,82),(3.5,82)]:h.Append(p.FromMM(x),p.FromMM(y))
 q.BooleanAdd(h);q.Fracture();z.SetFilledPolysList(p.In1_Cu,q)
elif case=='MEMS_rule_removed':
 z=next(z for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName()=='LIS2DW12_BODY_ALL6_NO_PLANES_OR_VIAS');b.Remove(z)
elif case=='JP301_no_longer_OPEN':fps['JP301'].SetValue('CLOSED');fps['JP301'].SetFPID(p.LIB_ID('GateStudy','Commission_CLOSED'))
elif case=='raw_net':pass
else:raise RuntimeError(case)
p.SaveBoard(sys.argv[2],b)
if case=='raw_net':
 import re,pathlib
 dest=pathlib.Path(sys.argv[2]);txt=dest.read_text();netcode=b.FindNet('AON_I2C_SCL').GetNetCode()
 blocks=list(re.finditer(r'\n\t\(segment\n.*?\n\t\)',txt,re.S));aon=b.FindNet('3V3_AON').GetNetCode();m=next(m for m in blocks if '(net '+str(aon)+')' in m[0]);piece=m[0].replace('(net '+str(aon)+')','(net '+str(netcode)+')');dest.write_text(txt[:m.start()]+piece+txt[m.end():])
''' 
expected={'raw_net':'Explicit serialized copper net changed','remove_input_via':'Old pad component split','wrong_old_width':'Old copper changed','wrong_C501_pad':'Old pad component split 3V3_AON','MEMS_plane_intrusion':'Actual plane intrusion MEMS','MEMS_rule_removed':'MEMS rule area','JP301_no_longer_OPEN':'Value mismatch JP301'}
rows=[]
for case in ['raw_net','remove_input_via','wrong_old_width','wrong_C501_pad','MEMS_plane_intrusion','MEMS_rule_removed','JP301_no_longer_OPEN']:
 out=O/(case+'.kicad_pcb');r=subprocess.run(['/usr/bin/python3','-c',code,str(D/'native_snapshot/mainboard_revD.kicad_pcb'),str(out),case],capture_output=True,text=True)
 if r.returncode:raise RuntimeError('mutation failed '+r.stderr)
 for opt in [[],['-O']]:
  r=subprocess.run(['/usr/bin/python3']+opt+[str(D/'audit.py'),str(out)],capture_output=True,text=True)
  if r.returncode!=1 or expected[case] not in r.stderr:raise RuntimeError('guard accepted '+case+r.stderr)
  rows.append({'case':case,'optimized':bool(opt),'exit':r.returncode,'error':r.stderr.split('RuntimeError:')[-1].strip()})
print(json.dumps(rows,indent=2))
