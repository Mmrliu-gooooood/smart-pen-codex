"""Record frozen-core behavior on identical fixed images; no runtime answers input."""
from host_api import *
import json,tempfile
p=ROOT;manifest=json.loads((p/'fixtures/manifest.json').read_text())
with tempfile.TemporaryDirectory() as tmp:
 lib=build(tmp);ws=(C.c_double*((lib.ws_size()+7)//8))();cfg=Config(710,1000,10,2)
 for f in manifest['fixtures']:
  raw=(p/'fixtures'/f['file']).read_bytes().split(b'\n255\n',1)[1];im=(C.c_uint8*len(raw)).from_buffer_copy(raw);out=Opt();C.memset(C.byref(out),165,C.sizeof(out));before=bytes(out)
  rc=lib.pen_roi_decode_opt_frozen(im,len(raw),200,200,200,C.byref(cfg),ws,None,C.byref(out))
  assert rc!=0,'This comparison set expects original full-frame rejection';assert bytes(out)==before
  f['legacy_expected_status']=rc
(p/'fixtures/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print([(f['file'],f['legacy_expected_status'],f['expected_status']) for f in manifest['fixtures']])
