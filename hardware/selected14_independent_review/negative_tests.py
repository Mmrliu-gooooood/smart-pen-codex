import pathlib,sys,subprocess,json
D=pathlib.Path(__file__).resolve().parent;O=D/'guard_boards';O.mkdir(exist_ok=True)
code=r'''import os,sys
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config'
import pcbnew as p
b=p.LoadBoard(sys.argv[1]);case=sys.argv[3]
if case in ['remove_usb','remove_en1']:
 net='USB_DP_MCU' if case=='remove_usb' else 'USB_EN1'
 t=max((t for t in b.GetTracks() if t.GetNetname()==net and not isinstance(t,p.PCB_VIA)),key=lambda t:t.GetLength());b.Remove(t)
elif case=='remove_rf':
 t=next(t for t in b.GetTracks()if t.GetNetname()=='RF_SIP'and (t.GetStart().y>p.FromMM(6)or t.GetEnd().y>p.FromMM(6)));b.Remove(t)
elif case=='bad_width':
 t=next(t for t in b.GetTracks()if t.GetNetname()=='RF_SIP');t.SetWidth(p.FromMM(.15))
elif case=='keepout_intrusion':
 t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(p.FromMM(6),p.FromMM(-2)));t.SetEnd(p.VECTOR2I(p.FromMM(7),p.FromMM(-2)));t.SetWidth(p.FromMM(.2));t.SetLayer(p.In3_Cu);t.SetNet(b.FindNet('GND'));b.Add(t)
elif case=='reference_hole':
 h=p.SHAPE_POLY_SET();h.NewOutline()
 for x,y in [(3.7,.1),(4.5,.1),(4.5,.4),(3.7,.4)]:h.Append(p.FromMM(x),p.FromMM(y))
 for z in b.Zones():
  if z.GetIsRuleArea()or z.GetLayer()!=p.In1_Cu or z.GetNetname()!='GND':continue
  q=p.SHAPE_POLY_SET(z.GetFilledPolysList(p.In1_Cu));q.BooleanSubtract(h);q.Fracture();z.SetFilledPolysList(p.In1_Cu,q)
elif case=='strap_wrong_net':
 f=next(f for f in b.GetFootprints()if f.GetReference()=='R104');next(x for x in f.Pads()if x.GetNumber()=='1').SetNet(b.FindNet('GND'))
else:raise RuntimeError(case)
p.SaveBoard(sys.argv[2],b)
'''
rows=[]
for case in ['remove_usb','remove_en1','remove_rf','bad_width','keepout_intrusion','strap_wrong_net','reference_hole']:
 out=O/(case+'.kicad_pcb');r=subprocess.run(['/usr/bin/python3','-c',code,str(D/'native_snapshot/mainboard_revD.kicad_pcb'),str(out),case],capture_output=True,text=True)
 if r.returncode:raise RuntimeError('Mutation process failed '+r.stderr)
 for mode in [[],['-O']]:
  r=subprocess.run(['/usr/bin/python3']+mode+[str(D/'audit.py'),str(out)],capture_output=True,text=True)
  if r.returncode!=1 or 'RuntimeError:'not in r.stderr:raise RuntimeError('Guard not deliberate '+case+str(mode)+r.stderr)
  rows.append(dict(case=case,optimized=bool(mode),exit=r.returncode,error=r.stderr.split('RuntimeError:')[-1].strip()))
print(json.dumps(rows,indent=2))
