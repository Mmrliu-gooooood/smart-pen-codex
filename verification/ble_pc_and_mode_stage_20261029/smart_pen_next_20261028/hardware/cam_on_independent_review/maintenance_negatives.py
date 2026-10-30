from pathlib import Path
import json,subprocess
D=Path(__file__).resolve().parent;O=D/'guard_boards';O.mkdir(exist_ok=True)
code=r'''import os,sys,json,pathlib
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache'
import pcbnew as p
b=p.LoadBoard(sys.argv[1]);case=sys.argv[3];D=pathlib.Path(sys.argv[1]).parent.parent;delta=json.loads((D/'maintenance_delta.json').read_text())
if case=='new_width':
 uid=delta['added'][0]['uuid'];t=next(t for t in b.GetTracks()if t.m_Uuid.AsString()==uid);t.SetWidth(140000)
elif case=='via_moved':
 uid=delta['unchanged_via_UUIDs'][0];t=next(t for t in b.GetTracks()if t.m_Uuid.AsString()==uid);t.Move(p.VECTOR2I(1000,0))
elif case=='TP_moved':next(f for f in b.GetFootprints()if f.GetReference()=='TP301').Move(p.VECTOR2I(1000,0))
elif case=='plane_changed':
 z=next(z for z in b.Zones()if not z.GetIsRuleArea()and z.IsOnLayer(p.In1_Cu));q=p.SHAPE_POLY_SET(z.GetFilledPolysList(p.In1_Cu));h=p.SHAPE_POLY_SET();h.NewOutline()
 for x,y in [(-20,-20),(-19,-20),(-19,-19),(-20,-19)]:h.Append(p.FromMM(x),p.FromMM(y))
 q.BooleanAdd(h);q.Fracture();z.SetFilledPolysList(p.In1_Cu,q)
else:raise RuntimeError(case)
p.SaveBoard(sys.argv[2],b)
'''
expected={'new_width':'Scope added non-CAM_ON or wrong width','via_moved':'Any surviving copper changed','TP_moved':'Physical footprint or source identity changed','plane_changed':'Actual filled plane geometry changed'};results=[]
for case,msg in expected.items():
 f=O/(case+'.kicad_pcb');r=subprocess.run(['/usr/bin/python3','-c',code,str(D/'native/mainboard_revD.kicad_pcb'),str(f),case],capture_output=True,text=True)
 if r.returncode:raise RuntimeError('Fixture construction failed '+r.stderr)
 for flags in [[],['-O']]:
  r=subprocess.run(['/usr/bin/python3']+flags+[str(D/'verify_maintenance.py'),str(f)],capture_output=True,text=True)
  if r.returncode!=1 or msg not in r.stderr:raise RuntimeError('Wrong negative outcome '+case+r.stderr)
  results.append({'case':case,'optimized':bool(flags),'exit':r.returncode,'expected_error':msg})
print(json.dumps(results,indent=2))
