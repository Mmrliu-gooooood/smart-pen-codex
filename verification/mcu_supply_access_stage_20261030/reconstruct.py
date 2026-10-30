"""Reconstruct exact archived sources in a NEW local workspace. Never execute tests."""
from pathlib import Path
import argparse,json,hashlib,shutil
p=argparse.ArgumentParser();p.add_argument('--repo-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
D=Path(__file__).resolve().parent;J=json.loads((D/'SOURCE_AND_DEPENDENCY_MAP.json').read_text());root=a.repo_root.resolve();out=a.output.resolve()
if out.exists():raise SystemExit('Output must not exist; refusing overwrite')
def safe(base,rel):
 r=Path(rel)
 if r.is_absolute()or '..'in r.parts:raise ValueError('unsafe path')
 q=(base/r).resolve()
 if not q.is_relative_to(base):raise ValueError('path escape')
 return q
rows=[x for x in J['files']if x['original_path']]+J['prior_reuse'];resolved=[]
for x in rows:
 src=safe(root,x['repo_path']);b=src.read_bytes()
 if len(b)!=x['bytes']or hashlib.sha256(b).hexdigest()!=x['sha256']:raise ValueError('source drift '+str(src))
 resolved.append((x,b))
out.mkdir(parents=True)
# Copy all original author/inputs first. Review overlay is done afterwards.
reviews={r for _,r in J['review_overlays']}
for x,b in resolved:
 if any(x['original_path'].startswith(r+'/')for r in reviews):continue
 dest=safe(out,x['original_path']);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
for author,review in J['review_overlays']:
 src=safe(out,author);dest=safe(out,review)
 if not src.is_dir():raise ValueError('missing author source')
 shutil.copytree(src,dest)
for x,b in resolved:
 if not any(x['original_path'].startswith(r+'/')for r in reviews):continue
 dest=safe(out,x['original_path']);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
print(json.dumps({'copied_sources':len(rows),'review_author_overlays':len(reviews),'workspace':str(out),'executed_tests':False}))
