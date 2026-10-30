from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent;B=D.parent/'j107_mode_port_closure';a=E.parse(B/'fresh.xml');b=E.parse(D/'fresh.xml')
for tag in ['components','libparts','nets']:
 if E.tostring(a.getroot().find(tag))!=E.tostring(b.getroot().find(tag)):raise RuntimeError('source identity delta '+tag)
def libraries(x,base):
 out={}
 for l in x.findall('./libraries/library'):
  parts=Path(l.findtext('uri')).parts
  if 'native' not in parts:raise RuntimeError('unexpected library root')
  i=max(i for i,v in enumerate(parts)if v=='native');rel=Path(*parts[i+1:]);path=base/'native'/rel
  if not path.is_file():raise RuntimeError('missing native library '+str(rel))
  out[l.get('logical')]={'relative_native_path':str(rel),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 return out
la,lb=libraries(a,B),libraries(b,D)
if la!=lb:raise RuntimeError('native library identity delta')
print(json.dumps({'components_libparts_nets_identical':True,'library_URI_difference':'only candidate root changes; actual relative native paths and file SHA checked','libraries':lb,'entities':len(b.findall('./components/comp'))},indent=2))
