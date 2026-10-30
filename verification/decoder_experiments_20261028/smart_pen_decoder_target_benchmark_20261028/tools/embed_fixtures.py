"""Rebuild header solely from frozen pixels; oracle is comparison-only metadata."""
from pathlib import Path
import json,hashlib,itertools
p=Path(__file__).resolve().parents[1]
rows=json.loads((p/'fixtures/manifest.json').read_text())
s=['/* Generated from frozen PGM pixels, do not edit. */','#include <stdint.h>','#include <stddef.h>','typedef struct { uint16_t count; uint8_t value; } bench_run;','typedef struct { const char *name; unsigned w,h; const bench_run *runs; size_t nruns; int status; unsigned x,y; } bench_fixture;']
for i,r in enumerate(rows):
 b=(p/'fixtures'/r['file']).read_bytes(); assert hashlib.sha256(b).hexdigest()==r['sha256_pgm']
 header,data=b.split(b'\n255\n',1); assert header.split()==[b'P5',str(r['width']).encode(),str(r['height']).encode()]; assert len(data)==r['width']*r['height']
 runs=[]
 for v,g in itertools.groupby(data):
  n=sum(1 for _ in g)
  while n: k=min(n,65535);runs.append((k,v));n-=k
 assert bytes(v for n,v in runs for _ in range(n))==data
 s.append(f'static const bench_run runs_{i}[] = {{'+','.join('{%d,%d}'%x for x in runs)+'};')
s.append('static const bench_fixture fixtures[] = {')
for i,r in enumerate(rows):
 s.append('{"%s",%d,%d,runs_%d,sizeof(runs_%d)/sizeof(runs_%d[0]),%d,%d,%d},'%(r['file'],r['width'],r['height'],i,i,i,r['expected_status'],r['expected_x'],r['expected_y']))
s.append('};')
(p/'main/fixtures.h').write_text('\n'.join(s)+'\n')
print('Embedded',len(rows),'fixtures; pixel SHA verified; RLE round-trip verified')
