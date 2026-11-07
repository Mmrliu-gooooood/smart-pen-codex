#!/usr/bin/env python3
"""Additive, host-only activity status candidate. Does not edit frozen inputs."""
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
import argparse
parser = argparse.ArgumentParser(description='Host-only research replay; no target build or hardware access.')
parser.add_argument('--repo', required=True, type=Path, help='Read-only checkout of the pinned repository base')
parser.add_argument('--out', required=True, type=Path, help='New, absent output directory; created without overwriting')
args = parser.parse_args()
BASE = args.repo.resolve()
RUN = args.out.resolve()
if RUN.exists():
    raise RuntimeError('Output already exists; choose a new directory')
if any(RUN == p or p in RUN.parents for p in [BASE, HERE.parents[3]]):
    raise RuntimeError('Output must be outside source and repository trees')
gate = json.loads((HERE.parents[1]/'BASE_DEPENDENCIES.json').read_text())
for row in gate['records']:
    p = BASE / row['path']
    if p.is_symlink() or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != row['sha256']:
        raise RuntimeError('Pinned source mismatch: '+row['path'])
RUN.mkdir(parents=True, exist_ok=False)
FW = BASE / 'firmware'
GUARD = HERE.parent / 'guard_r3/candidate/firmware'
NEW = HERE / 'candidate/firmware/application'
OUT = RUN / 'build'
OUT.mkdir(exist_ok=True)
SRC = ['application/pipeline.c', 'runtime/recorder.c', 'runtime/contact_power.c',
       'storage/store.c', 'portable/pen.c', 'vision/roi_opt.c', 'codec/anoto.c']
INCLUDES = ['application', 'runtime', 'storage', 'portable', 'vision', 'application_idf/main']
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
results, log = [], []
started = time.time()
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
tracked = set(FW.rglob('*.h')) | {FW/s for s in SRC}
tracked |= {FW/'application_idf/main/application_main.c', FW/'application_idf/main/CMakeLists.txt',
            FW/'application_idf/main/board_provider_absent.c', FW/'application_idf/main/Kconfig.projbuild'}
tracked |= set((BASE/'tests/test_application_stubs').rglob('*'))
tracked |= {BASE/'tests'/s for s in ('test_application_pipeline.c','test_application_actor.c',
 'test_application_maintenance.c','test_contact_power.c','test_recorder.c','roi_fixture.py','roi_opt_fixture.py')}
tracked |= {BASE/row['path'] for row in gate['records']}
tracked = sorted(p for p in tracked if p.is_file())
before = {str(p.relative_to(BASE)):digest(p) for p in tracked}
guard_before = {str(p.relative_to(GUARD)):digest(p) for p in GUARD.rglob('*') if p.is_file()}
candidate_files=[NEW/'activity_status.h',NEW/'activity_status.c',HERE/'test_activity_status.c',HERE/'test_activity_alias.c',
                 HERE/'test_actor_observation.c',HERE/'run_host.py',
                 HERE/'r1_evidence/candidate/firmware/application/activity_status.c',
                 HERE/'r1_evidence/candidate/firmware/application/activity_status.h']
candidate_before={str(p.relative_to(HERE)):digest(p) for p in candidate_files}
sys.path.insert(0,str(BASE/'tests'))
from roi_opt_fixture import Render,render,vectors
v = vectors()[0]
frame = OUT/'frame.gray'
frame.write_bytes(render(v['directions'],Render(pitch=20,angle=0,scale_y=1)))
frame_args = [str(frame), *map(str,v['section']), *map(str,v['xy'])]

def run(args,expected=0):
    args=list(map(str,args))
    p=subprocess.run(args,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    log.append('$ '+' '.join(args)+'\n'+p.stdout+f'[exit {p.returncode}]\n')
    (RUN/'HOST_TESTS.log').write_text('\n'.join(log))
    if p.returncode!=expected:
        raise RuntimeError('Command failed: '+' '.join(args))
    return p
def execute(label,test,sources=SRC,args=(),flags=(),guard=False,sidecar=None,expected=0):
    cmd=['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-pedantic',*flags,
         '-I'+str(NEW),'-I'+str(BASE/'tests'),'-I'+str(BASE/'tests/test_application_stubs')]
    cmd += ['-I'+str(FW/d) for d in INCLUDES]
    cmd += [str(GUARD/s if guard and (GUARD/s).exists() else FW/s) for s in sources]
    implementation=sidecar or NEW/'activity_status.c'
    cmd += [str(implementation),str(test),'-lm','-o',str(OUT/'runner')]
    run(cmd)
    p=run([OUT/'runner',*args],expected);results.append({'label':label,'flags':list(flags),
       'upstream':'boolean guard R3 overlay' if guard else 'frozen source',
       'status_implementation':str(implementation.relative_to(HERE)),
       'expected_exit':expected,'exit':p.returncode,'stdout':p.stdout})
    print(label+(': EXPECTED R1 FAILURE' if expected else ': PASS'),flush=True)

for mode in ('stable','invalid','nested'):
    execute('R1/alias-regression/'+mode,HERE/'test_activity_alias.c',args=frame_args+[mode],
            flags=('-DNDEBUG',),sidecar=HERE/'r1_evidence/candidate/firmware/application/activity_status.c',expected=1)

for guard in (False,True):
    tag='guard_R3' if guard else 'frozen'
    for flags,mode in (((), 'O2'),(('-DNDEBUG',),'NDEBUG'),
        (('-DNDEBUG','-O1','-fsanitize=undefined','-fno-sanitize-recover=all'),'UBSAN_NDEBUG')):
        extra=('-DTEST_BOOLEAN_OVERLAY=1',) if guard else ()
        execute(tag+'/activity/'+mode,HERE/'test_activity_status.c',args=frame_args,
                flags=flags+extra,guard=guard)
        execute(tag+'/alias-and-freshness/'+mode,HERE/'test_activity_alias.c',args=frame_args+['all'],
                flags=flags,guard=guard)
    # Existing unmodified callers compile/link against unchanged legacy ABI.
    for flags,mode in (((), 'O2'),(('-DNDEBUG',),'NDEBUG')):
        actor=GUARD/'application_idf/main/application_main.c' if guard else FW/'application_idf/main/application_main.c'
        execute(tag+'/actor-observation/'+mode,HERE/'test_actor_observation.c',
                flags=flags+('-DACTOR_SOURCE="'+str(actor)+'"',),guard=guard)
        execute(tag+'/pipeline-existing/'+mode,BASE/'tests/test_application_pipeline.c',
                args=frame_args,flags=flags,guard=guard)
        execute(tag+'/maintenance-existing/'+mode,BASE/'tests/test_application_maintenance.c',
                flags=flags,guard=guard)
        for disabled in (False,True):
            execute(tag+'/actor-existing/'+mode+('/disabled' if disabled else '/enabled'),
                    BASE/'tests/test_application_actor.c',
                    sources=['application_idf/main/application_main.c',*SRC],
                    flags=flags+(('-DTEST_APP_DISABLED=1',) if disabled else ()),guard=guard)

after={str(p.relative_to(BASE)):digest(p) for p in tracked}
guard_after={str(p.relative_to(GUARD)):digest(p) for p in GUARD.rglob('*') if p.is_file()}
if before!=after or guard_before!=guard_after:
    raise RuntimeError('Input hashes changed')
if candidate_before!={str(p.relative_to(HERE)):digest(p) for p in candidate_files}:
    raise RuntimeError('Candidate changed during verification')
patch=[]
for name in ('activity_status.h','activity_status.c'):
    patch.extend(difflib.unified_diff([], (NEW/name).read_text().splitlines(True),
      fromfile='/dev/null',tofile='b/firmware/application/'+name))
(RUN/'activity_status.patch').write_text(''.join(patch))
summary={'kind':'HOST_ONLY_NOT_ADOPTED_NOFAB_NOPOWER','revision':'R2_ALIAS_REJECTION','test_executions':len(results),
 'expected_R1_failures':3,
 'unexpected_failures':0,'results':results,'frozen_hashes_unchanged':True,'frozen_source_sha256':before,
 'guard_R3_hashes_unchanged':True,'guard_R3_source_sha256':guard_before,
 'verified_candidate_sha256':candidate_before,
 'compiler':run(['cc','--version']).stdout.splitlines()[0], 'python':sys.version.split()[0],
 'frame_sha256':digest(frame),'elapsed_seconds':round(time.time()-started,3),
 'dependencies':{k:bool(importlib.util.find_spec(k)) for k in ('cv2','bleak')},
 'not_run':['full host integration gate','ESP-IDF target build','actual GPIO/camera/Flash/BLE/USB/sleep/power',
            'production provider or UI reporting integration'],
 'compatibility':'Only two new optional application files. No old header/structure/callback/wire/default build changes.'}
(RUN/'RESULTS.json').write_text(json.dumps(summary,indent=2)+'\n')
size=sum(p.stat().st_size for p in RUN.rglob('*') if p.is_file())
if size>=1024*1024:
    raise RuntimeError(f'Candidate exceeds 1 MiB: {size}')
print(f'{len(results)} executions: 32 pass, 3 expected R1 failures; {size} bytes retained.')
