from pathlib import Path
import os,subprocess,tempfile,json
from build import build,HERE,V3
image=HERE.parent/'optics_paper_screen_20261031_1752/decoder_probe/001.pgm'
rows=[]
for sanitizer in [False,True]:
 for enabled,cap in [(False,64),(True,64),(True,1)]:
  with tempfile.TemporaryDirectory() as tmp:
   so=build(tmp,enabled,sanitizer,seed_cap=cap);exe=Path(tmp)/'native'
   cmd=['cc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-pedantic','-I'+str(HERE),'-I'+str(V3/'firmware/vision'),f'-DCANDIDATE_ENABLE_REFINEMENT={int(enabled)}',f'-DPEN_ROI_REFINE_MAX_SEEDS={cap}',str(HERE/'native_guards.c'),str(so),'-Wl,-rpath,'+str(Path(tmp)),'-lm','-o',str(exe)]
   if sanitizer:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
   subprocess.run(cmd,check=True)
   env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
   r=subprocess.run([str(exe),str(image)],env=env,capture_output=True,text=True)
   row=dict(sanitizer=sanitizer,enabled=enabled,cap=cap,exit=r.returncode,stdout=r.stdout,stderr=r.stderr);rows.append(row);print(json.dumps(row),flush=True)
   if r.returncode:break
(HERE/'verification/native_results.json').write_text(json.dumps(rows,indent=2)+'\n')
raise SystemExit(int(len(rows)!=6 or any(r['exit'] for r in rows)))
