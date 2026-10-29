from pathlib import Path
import sys
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D/'tools'));from sexpr import *
changes=[]
for path in (D/'schematic').glob('*.kicad_sch'):
 s=parse(path.read_text());changed=False
 for sym in children(s,'symbol'):
  refs=[x for x in children(sym,'property') if val(x[1])=='Reference']
  if refs and val(refs[0][2])in ['C106','C107']:
   prop(sym,'Footprint')[2]=q('Capacitor_SMD:C_0402_1005Metric');changes.append(val(refs[0][2]));changed=True
 if changed:path.write_text('('+s[0]+'\n'+'\n'.join(dump(c)if isinstance(c,list)else c for c in s[1:])+')\n')
if sorted(changes)!=['C106','C107']:raise RuntimeError(changes)
print(changes)
