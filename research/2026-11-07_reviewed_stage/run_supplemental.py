#!/usr/bin/env python3
"""Replay selected independent host checks; no hardware, source edits or deletion."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo', required=True, type=Path)
parser.add_argument('--out', required=True, type=Path)
args = parser.parse_args()
BASE, OUT = args.repo.resolve(), args.out.resolve()
if OUT.exists() or any(OUT == p or p in OUT.parents for p in [BASE, HERE.parents[1]]):
    raise SystemExit('Choose an absent output directory outside repository/source trees')
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
gate = json.loads((HERE / 'BASE_DEPENDENCIES.json').read_text())
for row in gate['records']:
    p = BASE / row['path']
    if p.is_symlink() or not p.is_file() or sha(p) != row['sha256']:
        raise SystemExit('Pinned dependency mismatch: ' + row['path'])
GUARD = HERE / 'firmware/guard_r3'
ACTIVITY = HERE / 'firmware/activity_r2'
FW = BASE / 'firmware'
NEW = ACTIVITY / 'candidate/firmware/application'
tracked = [BASE / r['path'] for r in gate['records']]
tracked += [p for p in HERE.rglob('*') if p.is_file() and p.suffix in ('.c', '.h', '.py')]
before = {str(p): sha(p) for p in tracked}
OUT.mkdir(parents=True, exist_ok=False)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', ASAN_OPTIONS='detect_leaks=0:halt_on_error=1')
src = ['application/pipeline.c', 'runtime/recorder.c', 'runtime/contact_power.c',
       'storage/store.c', 'portable/pen.c', 'vision/roi_opt.c', 'codec/anoto.c']
log, results = [], []
def command(argv):
    p = subprocess.run(list(map(str, argv)), text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, env=env)
    log.append('$ ' + ' '.join(map(str, argv)) + '\n' + p.stdout + '\nexit=' + str(p.returncode))
    (OUT / 'SUPPLEMENTAL.log').write_text('\n'.join(log))
    if p.returncode:
        raise RuntimeError('Supplemental command failed; retained log: ' + str(OUT / 'SUPPLEMENTAL.log'))
    return p
def execute(label, test, sources, overlay=True, flags=(), range_test=False):
    cmd = ['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-pedantic',*flags,
           '-I'+str(BASE/'tests'), '-I'+str(NEW)]
    cmd += ['-I'+str(FW/p) for p in ('application','runtime','storage','portable','vision')]
    if range_test:
        cmd += ['-DREVIEW_SIDECAR_SOURCE="'+str(NEW/'activity_status.c')+'"']
    cmd += [str(GUARD/'candidate/firmware'/s if overlay and (GUARD/'candidate/firmware'/s).is_file() else FW/s) for s in sources]
    cmd += [str(test), '-lm', '-o', str(OUT/'runner')]
    command(cmd)
    p = command([OUT/'runner'])
    results.append({'label':label,'exit':p.returncode,'stdout':p.stdout,'flags':list(flags)})
    print(label + ': PASS', flush=True)

ubsan = ('-DNDEBUG','-O1','-fsanitize=undefined','-fno-sanitize-recover=all')
for name in ['test_same_offer_retry.c','test_recovery_failures.c']:
    execute('guard_R3/'+name, GUARD/name, ['storage/store.c','portable/pen.c'], flags=ubsan)
for overlay in [False,True]:
    for name, flags in [('O2',()), ('UBSAN',ubsan),
                        ('ASAN_UBSAN',('-DNDEBUG','-O1','-fsanitize=address,undefined','-fno-sanitize-recover=all'))]:
        execute(('guard_R3/' if overlay else 'base/')+'range/'+name,
                ACTIVITY/'test_range_review.c',src,overlay,flags,True)
after = {str(p): sha(p) for p in tracked}
if before != after:
    raise RuntimeError('Source bytes changed during supplemental replay')
summary = {'status':'SCOPED_HOST_SUPPLEMENTAL_PASS','test_executions':len(results),
           'unexpected_failures':0,'results':results,'input_hashes_unchanged':True,
           'asan_leak_detection':False,'NOFAB':True,'NOPOWER':True,'not_adopted':True,
           'not_run':['target build','MemorySanitizer','hardware','production integration']}
(OUT/'RESULTS.json').write_text(json.dumps(summary,indent=2)+'\n')
print(str(len(results))+' supplemental executions passed')
