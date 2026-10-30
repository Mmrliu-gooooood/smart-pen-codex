import subprocess,tempfile,os
from pathlib import Path
p=Path(__file__).resolve().parent;s=p/'source/firmware'
with tempfile.TemporaryDirectory() as t:
 out=str(Path(t)/'seedcap');cmd=['cc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-pedantic','-fsanitize=address,undefined','-fno-omit-frame-pointer','-DPEN_PROJECTIVE_MAX_SEEDS=1','-I'+str(s/'vision'),str(p/'seedcap_v4.c'),str(s/'vision/roi_projective.c'),str(s/'codec/anoto.c'),'-lm','-o',out]
 print(' '.join(cmd),flush=True);subprocess.run(cmd,check=True)
 subprocess.run([out,str(p.parent/'smart_pen_optical_sampling_audit_20261030/tilt0_phase0.pgm')],check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1'))
