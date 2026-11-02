"""Reconstruct exact reviewed projects in a disposable directory; do not mutate native inputs."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,tempfile
D=Path(__file__).resolve().parent;R=D.parents[1]
N=R/'hardware/mainboard_wip_20261102/candidate'
EXPECTED='617a991b39a05e53f6bbf55700d2aa84052a3b5140b947c2b66a503f9846d8b5'
PARENT='dcaaafa93bde51e58a96d9443cb77031773fc42a16ad3db20210b53f0394b052'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sha(N/'mainboard_revD.kicad_pcb')!=EXPECTED or sha(D/'parent24.kicad_pcb')!=PARENT:raise RuntimeError('Wrong native input')
for x in json.loads((D/'PUBLICATION_SOURCES.json').read_text())['mapping']:
 if sha(R/x['path'])!=x['sha256']:raise RuntimeError('Publication source mismatch:'+x['path'])
with tempfile.TemporaryDirectory(prefix='pen_interface23_')as tmp:
 t=Path(tmp);shutil.copytree(D/'source',t,dirs_exist_ok=True);shutil.copytree(N,t/'candidate');shutil.copytree(N,t/'parent')
 (t/'parent/GateStudy.pretty/J107_DistributedWireLands3_NOFAB.kicad_mod').unlink()
 shutil.copyfile(D/'parent24.kicad_pcb',t/'parent/mainboard_revD.kicad_pcb')
 shutil.copyfile(D/'parent_usb_entry.kicad_sch',t/'parent/schematic/usb_entry.kicad_sch')
 for name,n in [('parent',53),('candidate',54)]:
  if sum(p.is_file()for p in(t/name).rglob('*'))!=n:raise RuntimeError('Unexpected project file set')
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 for name in['CONFIG','DATA','CACHE']:
  p=t/('xdg_'+name.lower());p.mkdir();env['XDG_'+name+'_HOME']=str(p)
 def run(args,label):
  q=subprocess.run(args,cwd=t,env=env,capture_output=True,text=True)
  if q.returncode:raise RuntimeError(label+' failed\n'+q.stdout+'\n'+q.stderr)
  print(label+': PASS')
 for script in ['verify_candidate.py','references.py']:
  for opt in[[],['-O']]:run(['/usr/bin/python3']+opt+[str(t/script)],script+(' -O'if opt else''))
 for stem in['verify_candidate','references']:
  if json.loads((t/(stem+'.json')).read_text())!=json.loads((t/(stem+'_O.json')).read_text()):raise RuntimeError('Normal/-O mismatch: '+stem)
 for script in ['library_check.py','negative_checks.py','inverse.py']:
  run(['/usr/bin/python3',str(t/script)],script)
 run(['kicad-cli','pcb','drc','--format','json','--schematic-parity','--output',str(t/'fresh_drc.json'),str(t/'candidate/mainboard_revD.kicad_pcb')],'fresh native DRC')
 q=json.loads((t/'fresh_drc.json').read_text());counts=[len(q[k])for k in['violations','unconnected_items','schematic_parity']]
 if counts!=[0,23,0]:raise RuntimeError('Unexpected DRC counts:'+str(counts))
 if sha(t/'candidate/mainboard_revD.kicad_pcb')!=EXPECTED:raise RuntimeError('Candidate mutated')
 if sha(t/'inverse/mainboard_revD.kicad_pcb')!=PARENT:raise RuntimeError('Inverse not exact')
 print(json.dumps({'status':'PASS_STATIC_PUBLIC_SUBSET_ONLY_NOFAB_NO_POWER','native_counts':counts,'candidate_sha256':EXPECTED,'exact_parent_sha256':PARENT,'native_dependencies':'54 candidate /53 parent;51 shared','scope':'Not a replay of complete independent CAD/plane audit; not physical process or SI/PDN qualification.'},indent=2))
