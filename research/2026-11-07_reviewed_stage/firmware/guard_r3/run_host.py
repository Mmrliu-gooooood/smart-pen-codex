#!/usr/bin/env python3
"""Independent host-only overlay; never edits frozen inputs or deletes files."""
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
OUT = RUN / 'build'
OUT.mkdir(exist_ok=True)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
sources = ['application/pipeline.c', 'runtime/recorder.c', 'runtime/contact_power.c',
           'storage/store.c', 'portable/pen.c', 'vision/roi_opt.c', 'codec/anoto.c']
include_dirs = ['application', 'runtime', 'storage', 'portable', 'vision', 'application_idf/main']
results = []
log = []
started = time.time()

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

tracked = set(FW.rglob('*.h')) | set((BASE/'tests/test_application_stubs').rglob('*'))
tracked |= set((BASE/'tests/test_storage_stubs').rglob('*'))
tracked |= {FW / s for s in sources + ['application_idf/main/application_main.c','storage/storage_idf.c']}
tracked |= {BASE / ('tests/' + f) for f in ['test_contact_power.c', 'test_recorder.c',
    'test_application_pipeline.c', 'test_application_actor.c', 'test_application_maintenance.c',
    'test_storage.c','test_storage_idf_mock.c','roi_fixture.py', 'roi_opt_fixture.py']}
tracked |= {BASE/row['path'] for row in gate['records']}
tracked = sorted(p for p in tracked if p.is_file())
before = {str(p.relative_to(BASE)): digest(p) for p in tracked}

sys.path.insert(0, str(BASE / 'tests'))
from roi_opt_fixture import Render, render, vectors
v = vectors()[0]
frame = OUT / 'frame.gray'
frame.write_bytes(render(v['directions'], Render(pitch=20, angle=0, scale_y=1)))
frame_args = [str(frame), *map(str, v['section']), *map(str, v['xy'])]

def run(args, expected=0):
    proc = subprocess.run(list(map(str,args)), env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log.append('$ ' + ' '.join(map(str,args)) + '\n' + proc.stdout + f'[exit {proc.returncode}, expected {expected}]\n')
    if proc.returncode != expected:
        (RUN/'HOST_TESTS.log').write_text('\n'.join(log))
        raise RuntimeError('Unexpected return code: ' + ' '.join(map(str,args)))
    return proc

def execute(label, candidate, test, srcs, arguments=(), flags=(), expected=0, idf_storage=False):
    cmd = ['cc', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror', '-pedantic', *flags]
    if idf_storage:
        sdk=OUT/'storage_mock';sdk.mkdir(exist_ok=True)
        (sdk/'sdkconfig.h').write_text('/* Host-only fixture; enable switch comes from compiler flags. */\n')
        cmd += ['-Wno-unused-function','-I'+str(sdk),'-I'+str(BASE/'tests/test_storage_stubs')]
    else:
        cmd += ['-I'+str(BASE/'tests/test_application_stubs')]
    cmd += ['-I'+str(BASE/'tests')]
    if candidate:
        cmd += ['-I'+str(HERE/'candidate/firmware'/d) for d in include_dirs]
    cmd += ['-I'+str(FW/d) for d in include_dirs]
    for src in srcs:
        overlay = HERE/'candidate/firmware'/src
        cmd.append(str(overlay if candidate and overlay.is_file() else FW/src))
    cmd += [str(test), '-lm', '-o', str(OUT/'runner')]
    run(cmd)
    proc = run([OUT/'runner', *arguments], expected)
    results.append({'label':label,'source':'candidate overlay' if candidate else 'frozen original',
                    'flags':list(flags),'expected_exit':expected,'actual_exit':proc.returncode,
                    'stdout':proc.stdout})
    print(label + ': ' + ('EXPECTED REJECTION OF ORIGINAL' if expected else 'PASS'), flush=True)
    (RUN/'HOST_TESTS.log').write_text('\n'.join(log))

for candidate in (False, True):
    prefix = 'candidate' if candidate else 'original'
    execute(prefix+'/contact-existing', candidate, BASE/'tests/test_contact_power.c', ['runtime/contact_power.c'])
    execute(prefix+'/recorder-existing', candidate, BASE/'tests/test_recorder.c',
            ['portable/pen.c','storage/store.c','runtime/contact_power.c','runtime/recorder.c'])
    execute(prefix+'/storage-existing',candidate,BASE/'tests/test_storage.c',['storage/store.c','portable/pen.c'])
    for enabled in (False,True):
        execute(prefix+'/storage-idf-existing/'+str(enabled),candidate,BASE/'tests/test_storage_idf_mock.c',
                ['storage/storage_idf.c','storage/store.c','portable/pen.c'],
                flags=('-DCONFIG_PEN_FLASH_RECORDING=1',) if enabled else (),idf_storage=True)
    for flags, mode in (((), 'O2'), (('-DNDEBUG',), 'NDEBUG')):
        execute(prefix+'/maintenance-existing/'+mode,candidate,BASE/'tests/test_application_maintenance.c',sources,flags=flags)
        execute(prefix+'/pipeline-existing/'+mode, candidate, BASE/'tests/test_application_pipeline.c', sources, frame_args, flags)
        for disabled in (False, True):
            execute(prefix+'/actor-existing/'+mode+('/disabled' if disabled else '/enabled'), candidate,
                    BASE/'tests/test_application_actor.c', ['application_idf/main/application_main.c', *sources],
                    flags=(*flags, *(('-DTEST_APP_DISABLED=1',) if disabled else ())))

# Red tests must fail against the original, with the unsafe sleep trace retained.
for mode in ('cp','app'):
    execute('original/regression/'+mode, False, HERE/'test_boolean_guard.c', sources, (mode,), expected=1)
for mode in ('recording','replay'):
    execute('original/actor-regression/'+mode, False, HERE/'test_actor_boolean.c',
            ['application_idf/main/application_main.c', *sources], (mode,), expected=1)
execute('original/maintenance-regression/replay',False,HERE/'test_actor_maintenance_guard.c',
        ['application_idf/main/application_main.c',*sources],('replay',),flags=('-DNDEBUG',),expected=1)
execute('original/maintenance-regression/store',False,HERE/'test_reclaim_guard.c',sources,('store',),flags=('-DNDEBUG',),expected=1)
execute('original/maintenance-regression/recovery',False,HERE/'test_reclaim_guard.c',sources,('recovery',),flags=('-DNDEBUG',),expected=1)
# These adjacent entry points already use exact-domain guards. Confirm, do not claim new fixes.
execute('original/maintenance-sleep-already-safe',False,HERE/'test_actor_maintenance_guard.c',
        ['application_idf/main/application_main.c',*sources],('sleep',),flags=('-DNDEBUG',))
execute('original/app-reclaim-already-safe',False,HERE/'test_reclaim_guard.c',sources,('app',),flags=('-DNDEBUG',))
execute('original/idf-intent-already-safe',False,HERE/'test_storage_recovery_intent.c',
        ['storage/storage_idf.c','storage/store.c','portable/pen.c'],flags=('-DCONFIG_PEN_FLASH_RECORDING=1',),idf_storage=True)
execute('original/ack-regression/store',False,HERE/'test_ack_guard.c',sources,('store',),flags=('-DNDEBUG',),expected=1)
execute('original/ack-regression/idf',False,HERE/'test_idf_ack_guard.c',
        ['storage/storage_idf.c','storage/store.c','portable/pen.c'],flags=('-DCONFIG_PEN_FLASH_RECORDING=1',),expected=1,idf_storage=True)
execute('original/app-ack-already-safe',False,HERE/'test_ack_guard.c',sources,('app',),flags=('-DNDEBUG',))

# CHECK is explicit, so -DNDEBUG cannot turn tests into false passes.
for flags, mode in ((('-DNDEBUG',), 'NDEBUG'),
                    (('-DNDEBUG','-O1','-fsanitize=undefined','-fno-sanitize-recover=all'), 'UBSAN_NDEBUG')):
    for kind in ('cp','app'):
        execute('candidate/boolean/'+kind+'/'+mode, True, HERE/'test_boolean_guard.c', sources, (kind,), flags)
    for kind in ('recording','replay'):
        execute('candidate/actor-boolean/'+kind+'/'+mode, True, HERE/'test_actor_boolean.c',
                ['application_idf/main/application_main.c', *sources], (kind,), flags)
    for kind in ('sleep','replay'):
        execute('candidate/actor-maintenance/'+kind+'/'+mode,True,HERE/'test_actor_maintenance_guard.c',
                ['application_idf/main/application_main.c',*sources],(kind,),flags)
    for kind in ('store','app','recovery'):
        execute('candidate/reclaim/'+kind+'/'+mode,True,HERE/'test_reclaim_guard.c',sources,(kind,),flags)
    # Existing IDF mock helpers use assert, so retain assertions in this supplemental test.
    intent_flags=tuple(f for f in flags if f!='-DNDEBUG')+('-DCONFIG_PEN_FLASH_RECORDING=1',)
    execute('candidate/idf-intent/'+mode.replace('NDEBUG','ASSERT_ENABLED'),True,HERE/'test_storage_recovery_intent.c',
            ['storage/storage_idf.c','storage/store.c','portable/pen.c'],flags=intent_flags,idf_storage=True)
    for kind in ('store','app'):
        execute('candidate/ack/'+kind+'/'+mode,True,HERE/'test_ack_guard.c',sources,(kind,),flags)
    execute('candidate/idf-ack/'+mode.replace('NDEBUG','ASSERT_ENABLED'),True,HERE/'test_idf_ack_guard.c',
            ['storage/storage_idf.c','storage/store.c','portable/pen.c'],flags=intent_flags,idf_storage=True)

after = {str(p.relative_to(BASE)): digest(p) for p in tracked}
if before != after:
    raise RuntimeError('Frozen source hash changed')
summary = {'kind':'HOST_ONLY_NOT_ADOPTED_NOFAB_NOPOWER','compiler':run(['cc','--version']).stdout.splitlines()[0],
 'python':sys.version.split()[0], 'results':results, 'test_executions':len(results),
 'expected_original_failures':9,'unexpected_failures':0,'frozen_hashes_unchanged':True,
 'source_sha256':before, 'frame_sha256':digest(frame),
 'dependency_discovery':{k:bool(importlib.util.find_spec(k)) for k in ['cv2','numpy','fastapi','httpx','uvicorn','bleak']},
 'elapsed_seconds':round(time.time()-started,3),
 'scope':'Focused existing host regressions, exhaustive boolean bytes, signed maintenance and ACK security boundaries, real IDF adapter with host doubles only. Not full host gate, target compile, physical Flash, GPIO, USB, camera, sleep or power test.'}
(RUN/'RESULTS.json').write_text(json.dumps(summary,indent=2)+'\n')
(RUN/'HOST_TESTS.log').write_text('\n'.join(log))
size=sum(p.stat().st_size for p in RUN.rglob('*') if p.is_file())
if size >= 1024*1024:
    raise RuntimeError(f'Output size exceeds 1 MiB: {size}')
print(f'Focused suite complete: {len(results)} executions, 9 expected original failures, no unexpected failures; {size} bytes retained.')
