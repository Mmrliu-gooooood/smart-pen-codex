from pathlib import Path
import os,sys,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/xclk-physical'
import pcbnew as p
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D/'review_dependencies'));from finite_copper import build,components
A=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));B=p.LoadBoard(str(D/'final_candidate/mainboard_revD.kicad_pcb'));a,b=build(A),build(B);changes={};errors=[]
for n,v in a.items():
 old=components(v);new=components(b[n]);expected=[sorted(sum(old,[]))]if n=='CAM_XCLK'else old
 if old!=new:changes[n]={'before':old,'after':new}
 if new!=expected:errors.append(n)
cores={n:len(next(x for x in components(b[n])if q in x))for n,q in [('GND','J106.3'),('3V3_AON','J106.2'),('SENS_VIO_1V8','J202.23')]};r={'sha256':hashlib.sha256((D/'final_candidate/mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'changes':changes,'errors':errors,'cores':cores};(D/('physical_optimized.json'if not __debug__ else'physical.json')).write_text(json.dumps(r,indent=2));print(r)
if errors or cores!={'GND':94,'3V3_AON':41,'SENS_VIO_1V8':12}:raise RuntimeError('physical regression')
