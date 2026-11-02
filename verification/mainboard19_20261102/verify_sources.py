"""Dependency-free source integrity, NOT DRC/MCAD/finite-copper verification."""
from pathlib import Path
import hashlib,json,re,sys
D=Path(__file__).resolve().parent;R=D.parents[1]
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
source=json.loads((D/'PUBLICATION_SOURCES.json').read_text())['mapping'];require(len(source)==96,'source map count');require(len({r['path']for r in source})==96,'unique source paths')
for row in source:
 path=R/row['path'];require(path.is_file()and not path.is_symlink(),'missing input '+row['path']);require(digest(path)==row['sha256'],'input hash '+row['path'])
N=R/'hardware/mainboard_wip19_20261102/candidate';require(len([p for p in N.rglob('*')if p.is_file()])==54,'native54')
sys.path.insert(0,str(D/'source/review_dependencies'));from native_blocks import blocks
def raw(text):
 rows=[v for _,_,v in blocks(text)if v.startswith('(footprint')];require(len(rows)==103,'nonempty raw103');refs=[re.search(r'\(property "Reference" "([^"]+)"',v).group(1)for v in rows];require(len(set(refs))==103,'unique raw103');return rows
boards=[D/'parent20.kicad_pcb',N/'mainboard_revD.kicad_pcb'];expected=['1639b8db38415f0466c13334add7cd4bfe6708b0caa232e8b1e79a7044fdf8e7','f7632bf6296ba212ec59e54edb1dfdb91995f6f4f071a3d9505b6638f3fbf416']
for p,h in zip(boards,expected):require(digest(p)==h,'native hash');raw(p.read_text())
txt=boards[-1].read_text();rows=raw(txt);negatives=['',txt.replace(rows[0],'',1)]
# A duplicate reference preserves103 raw blocks but must fail uniqueness.
r0=re.search(r'\(property "Reference" "([^"]+)"',rows[0]).group(1);r1=re.search(r'\(property "Reference" "([^"]+)"',rows[1]).group(1);negatives.append(txt.replace(rows[1],rows[1].replace('"Reference" "'+r1+'"','"Reference" "'+r0+'"',1),1))
for mutation in negatives:
 try:raw(mutation)
 except RuntimeError:pass
 else:raise RuntimeError('nonempty/unique guard accepted mutation')
print(json.dumps({'status':'PASS','source_hashes':96,'native_files':54,'raw_inputs_each':103,'negative_cases':3,'scope':'Source integrity only, NOT DRC, MCAD or finite-copper verification.'}))
