from pathlib import Path
import tempfile,subprocess,json
import build
original=subprocess.run
commands=[]
def omitted(cmd,*a,**kw):
 cmd=[c for c in cmd if not c.startswith('-DCANDIDATE_ENABLE_REFINEMENT=')];commands.append(cmd);return original(cmd,*a,**kw)
subprocess.run=omitted
with tempfile.TemporaryDirectory() as tmp:
 so=build.build(tmp,False);exe=Path(tmp)/'default_test'
 subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-pedantic','-I'+str(build.HERE),'-I'+str(build.V3/'firmware/vision'),str(build.HERE/'native_guards.c'),str(so),'-Wl,-rpath,'+tmp,'-lm','-o',str(exe)],check=True)
 p=subprocess.run([str(exe),str(build.HERE.parent/'optics_paper_screen_20261031_1752/decoder_probe/001.pgm')],capture_output=True,text=True)
 result={'gate_macro_omitted':True,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'commands':commands};(build.HERE/'verification/default_independent.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(p.returncode)
