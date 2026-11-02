"""Exact selected copper reconstruction from accepted parent, not a route search."""
import os,sys,json,re,hashlib,shutil
from pathlib import Path
os.environ.setdefault('XDG_CONFIG_HOME','/tmp/cambus_reconstruct/config');os.environ.setdefault('XDG_CACHE_HOME','/tmp/cambus_reconstruct/cache');os.environ.setdefault('XDG_DATA_HOME','/tmp/cambus_reconstruct/data')
import pcbnew as p
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D/'review_dependencies'));from native_blocks import blocks
c=json.loads((D/'native_contract.json').read_text());S=D/'parent';A=S/'mainboard_revD.kicad_pcb';T=D/'reconstructed_candidate'
if T.exists():raise RuntimeError('no overwrite')
if hashlib.sha256(A.read_bytes()).hexdigest()!=c['parent_sha256']:raise RuntimeError('parent hash')
shutil.copytree(S,T);Q=T/A.name;raw=Q.read_text();removed=set(c['removed']);found=set()
for a,z,v in reversed(blocks(raw)):
 if v.startswith(('(segment','(via')):
  u=re.search(r'\(uuid "([^"]+)"\)',v).group(1)
  if u in removed:found.add(u);raw=raw[:a]+raw[z:]
if found!=removed:raise RuntimeError('removal')
oldfp=next(v for _,_,v in blocks(raw)if v.startswith('(footprint')and '(property \"Reference\" \"R230\"'in v)
raw=raw.replace(oldfp,(D/'footprint_delta.sexpr').read_text().strip(),1)
oldlabel=next(v for _,_,v in blocks(raw)if v.startswith('(footprint')and '(property "Reference" "J107"'in v)
raw=raw.replace(oldlabel,(D/'label_footprint_delta.sexpr').read_text().strip(),1)
pos=raw.rfind(')');raw=raw[:pos]+'\n'+(D/'copper_delta.sexpr').read_text()+'\n'+raw[pos:];Q.write_text(raw);b=p.LoadBoard(str(Q));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(Q),b);sha=hashlib.sha256(Q.read_bytes()).hexdigest();out={'expected':c['candidate_sha256'],'reconstructed':sha,'exact':sha==c['candidate_sha256']};(D/'reconstruction_result.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if not out['exact']:raise RuntimeError('reconstruction not byte exact')
