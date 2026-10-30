"""Embed pixel-only packed RLE, with reproducible manifest/source binding."""
from pathlib import Path
import hashlib,json,itertools
p=Path(__file__).resolve().parents[1];raw=(p/'fixtures/manifest.json').read_bytes();rows=json.loads(raw)['fixtures']
paths=sorted([*p.glob('vision/*'),*p.glob('legacy/vision/*'),*p.glob('codec/*'),p/'main/bench_main.c',p/'main/CMakeLists.txt',p/'main/Kconfig.projbuild',p/'CMakeLists.txt',p/'sdkconfig.defaults',p/'profiles/enabled.defaults'])
source_hashes={str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in paths};source_sha=hashlib.sha256(json.dumps(source_hashes,sort_keys=True,separators=(',',':')).encode()).hexdigest()
(p/'verification/build-inputs.json').write_text(json.dumps(dict(source_bundle_sha256=source_sha,files=source_hashes),indent=2)+'\n')
s=['/* Generated from frozen raw pixels. No oracle in decode inputs. */','#include <stdint.h>','#include <stddef.h>',f'#define BENCH_MANIFEST_SHA256 "{hashlib.sha256(raw).hexdigest()}"',f'#define BENCH_SOURCE_SHA256 "{source_sha}"','typedef struct {const char *name;const uint8_t *packed;size_t packed_size;} bench_fixture;']
for i,r in enumerate(rows):
 b=(p/'fixtures'/r['file']).read_bytes();assert hashlib.sha256(b).hexdigest()==r['pgm_sha256'];header,data=b.split(b'\n255\n',1);assert header.split()==[b'P5',b'200',b'200'];assert len(data)==40000 and hashlib.sha256(data).hexdigest()==r['pixel_sha256']
 packed=bytearray();check=bytearray()
 for v,g in itertools.groupby(data):
  n=sum(1 for _ in g)
  while n:
   k=min(n,65535);packed.extend([k&255,k>>8,v]);check.extend(bytes([v])*k);n-=k
 assert check==data
 s.append(f'static const uint8_t packed_{i}[]={{'+','.join(map(str,packed))+'};')
s.append('static const bench_fixture fixtures[]={')
for i,r in enumerate(rows): s.append('{"%s",packed_%d,sizeof(packed_%d)},'%(r['file'],i,i))
s.append('};');(p/'main/fixtures.h').write_text('\n'.join(s)+'\n');print(f'{len(rows)} fixture hashes and RLE round trips passed')
