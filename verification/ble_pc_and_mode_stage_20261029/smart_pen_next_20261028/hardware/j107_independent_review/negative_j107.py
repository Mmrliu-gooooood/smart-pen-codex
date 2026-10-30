from pathlib import Path
import json,re,subprocess
D=Path(__file__).resolve().parent;O=D/'guard_boards/mutations';O.mkdir(parents=True,exist_ok=True)
code=r'''import os,sys,json,pathlib,re
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache'
import pcbnew as p
src=pathlib.Path(sys.argv[1]);dest=pathlib.Path(sys.argv[2]);case=sys.argv[3];D=src.parent.parent;delta=json.loads((D/'j107_delta.json').read_text());b=p.LoadBoard(str(src))
if case=='thin_new_ground':
 uid=next(r['uuid']for r in delta['added']if r['net']=='GND');t=next(t for t in b.GetTracks()if t.m_Uuid.AsString()==uid);t.SetWidth(150000)
elif case=='move_current_input_GND_via':next(t for t in b.GetTracks()if t.m_Uuid.AsString()=='3e5c1457-dfe2-4fd3-8145-4f946500f344').Move(p.VECTOR2I(1000,0))
elif case=='renumber_J107':next(q for f in b.GetFootprints()if f.GetReference()=='J107'for q in f.Pads()if q.GetNumber()=='1').SetNumber('4')
elif case=='remove_EN1_via':
 uid=next(r['uuid']for r in delta['added']if r['net']=='USB_EN1'and r['type']=='via');raw=re.sub(r'\n\t\(via\n.*?\n\t\)',lambda m:''if uid in m[0]else m[0],src.read_text(),flags=re.S);dest.write_text(raw);sys.exit(0)
else:raise RuntimeError(case)
p.SaveBoard(str(dest),b)
'''
expected={'thin_new_ground':'Added width/layer/geometry','move_current_input_GND_via':'Surviving original copper changed','renumber_J107':'Any physical/source footprint changed','remove_EN1_via':'Exact J107 copper set'};rows=[]
for case,msg in expected.items():
 f=O/(case+'.kicad_pcb');r=subprocess.run(['/usr/bin/python3','-c',code,str(D/'native/mainboard_revD.kicad_pcb'),str(f),case],capture_output=True,text=True)
 if r.returncode:raise RuntimeError('Mutation failed '+case+r.stderr)
 for flags in [[],['-O']]:
  r=subprocess.run(['/usr/bin/python3']+flags+[str(D/'verify_j107.py'),str(f)],capture_output=True,text=True)
  if r.returncode!=1 or msg not in r.stderr:raise RuntimeError('Wrong rejection '+case+r.stderr)
  rows.append({'case':case,'optimized':bool(flags),'exit':r.returncode,'expected_error':msg})
print(json.dumps(rows,indent=2))
