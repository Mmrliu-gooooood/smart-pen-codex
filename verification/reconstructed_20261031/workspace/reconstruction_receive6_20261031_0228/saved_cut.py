from pathlib import Path
import json,re,sys,shutil
from native_blocks import blocks
D=Path(__file__).resolve().parent;i=int(sys.argv[1]);mode='optimized_'if not __debug__ else'';r=json.loads((D/'final_validation'/('negative_'+str(i)+'.json')).read_text());u=r['cut']['uuid'];out=D/('saved_cut_'+mode+str(i));shutil.copytree(D/'final_candidate',out);f=out/'mainboard_revD.kicad_pcb';s=f.read_text();matched=[(a,z)for a,z,t in blocks(s)if t.startswith('(segment')and '(uuid "'+u+'")'in t]
if len(matched)!=1:raise RuntimeError('cut UUID not unique')
a,z=matched[0];f.write_text(s[:a]+s[z:]);print({'cut':r['cut'],'scope':'DIAGNOSTIC negative only; final unchanged.'})
