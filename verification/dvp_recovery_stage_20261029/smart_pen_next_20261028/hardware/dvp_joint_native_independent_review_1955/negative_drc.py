from pathlib import Path
import os,json,subprocess,shutil,tempfile
os.environ.update(XDG_CONFIG_HOME='/tmp/dvp-review1955-config',XDG_CACHE_HOME='/tmp/dvp-review1955-cache',XDG_DATA_HOME='/tmp/dvp-review1955-data')
import pcbnew as p
D=Path(__file__).resolve().parent;out=[]
for case,expected in [('narrow_parallel_clearance','clearance'),('undersized_annulus','annular_width')]:
 with tempfile.TemporaryDirectory(prefix='dvp1955-negative-',dir='/tmp')as td:
  n=Path(td)/'native';shutil.copytree(D/'native',n);f=n/'mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f))
  if case=='narrow_parallel_clearance':
   t=next(t for t in b.GetTracks()if not isinstance(t,p.PCB_VIA)and t.GetNetname()=='SENS_D0'and t.GetStart().x==13500000 and t.GetEnd().x==13500000 and t.GetLength()>40000000)
   t.Move(p.VECTOR2I(-10000,0))
  else:
   t=next(t for t in b.GetTracks()if isinstance(t,p.PCB_VIA));t.SetDrill(400000)
  p.SaveBoard(str(f),b);r=D/(case+'.drc.json');cmd=['/usr/bin/kicad-cli','pcb','drc','--all-track-errors','--severity-all','--schematic-parity','--exit-code-violations','--format','json','-o',str(r),str(f)];q=subprocess.run(cmd,capture_output=True,text=True);(D/(case+'.log')).write_text(q.stdout+q.stderr)
  report=json.loads(r.read_text());types=[x['type']for x in report['violations']]
  if q.returncode!=5 or expected not in types:raise RuntimeError('NEGATIVE_NOT_DETECTED '+case+str(types))
  out.append({'case':case,'expected':expected,'types':types,'exit':q.returncode})
(D/'native_negative_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
