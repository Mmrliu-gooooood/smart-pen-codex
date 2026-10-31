from pathlib import Path
import os,sys,json,hashlib,difflib
os.environ.update(XDG_CONFIG_HOME='/tmp/newreconstruct/config',XDG_CACHE_HOME='/tmp/newreconstruct/cache',XDG_DATA_HOME='/tmp/newreconstruct/data')
import pcbnew as p
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D/'review_dependencies'));from finite_copper import build,components
src=D/'native/mainboard_revD.kicad_pcb';dst=D/'final_candidate/mainboard_revD.kicad_pcb';out=D/'final_validation';out.mkdir(exist_ok=True)
f=out/'native_reversible.ndiff'
if not f.exists():f.write_text(''.join(difflib.ndiff(src.read_text().splitlines(keepends=True),dst.read_text().splitlines(keepends=True))))
delta=f.read_text().splitlines(keepends=True)
if ''.join(difflib.restore(delta,1))!=src.read_text()or''.join(difflib.restore(delta,2))!=dst.read_text():raise RuntimeError('raw replay')
i=int(sys.argv[1]);n,ref,num=[('CAM_RESET_UART_TX','U101','49'),('CAM_PWDN_UART_RX','U101','50'),('CAM_RESET_UART_TX','J104','1'),('CAM_PWDN_UART_RX','J104','2')][i];b=p.LoadBoard(str(dst));fps=list(b.GetFootprints());f=next(f for f in fps if f.GetReference()==ref);pads=list(f.Pads());pad=next(q for q in pads if q.GetNumber()==num);tracks=list(b.GetTracks());ts=[t for t in tracks if not isinstance(t,p.PCB_VIA)and t.GetNetname()==n and(t.GetStart()==pad.GetPosition()or t.GetEnd()==pad.GetPosition())]
if len(ts)!=1:raise RuntimeError('not unique terminal')
u=ts[0].m_Uuid.AsString();b.Remove(ts[0]);c=components(build(b)[n]);name=ref+'.'+num
if [name]not in c or len(c)!=2:raise RuntimeError('cut undetected')
r={'normal_or_optimized':'optimized'if not __debug__ else'normal','sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'reversible_raw_native_replay_exact_both_directions':True,'cut':{'net':n,'terminal':name,'uuid':u,'components':c,'detected':True},'scope':'Diagnostic finite-copper terminal cuts; final unchanged, not dynamic test.'};(out/(('negative_optimized_'if not __debug__ else'negative_')+str(i)+'.json')).write_text(json.dumps(r,indent=2));print(r)

# Saved matched-project negative fixture, never an adoptable design.
import shutil
cutdir=out/('saved_cut'+('_optimized'if not __debug__ else'')+'_'+str(i));shutil.copytree(D/'final_candidate',cutdir);p.SaveBoard(str(cutdir/'mainboard_revD.kicad_pcb'),b)
