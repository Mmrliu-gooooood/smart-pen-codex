#!/usr/bin/env python3
"""Build real portable C with a memory NOR model; no BLE/device operations."""
from pathlib import Path
import os,subprocess,tempfile,struct,zlib
root=Path(__file__).resolve().parents[1]
sources=[root/'src/pen_ble_core.c',root/'src/pen_ble_actor.c',root/'tests/transport_test.c']+[root/'frozen'/p for p in ('application/pipeline.c','runtime/recorder.c','runtime/contact_power.c','vision/roi_opt.c','codec/anoto.c','portable/pen.c','storage/store.c')]
includes=[root/'include']+[root/'frozen'/p for p in ('application','runtime','vision','codec','portable','storage')]
for name,flags in [('normal',[]),('ndebug',['-O2','-DNDEBUG']),('asan_ubsan',['-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'])]:
 with tempfile.TemporaryDirectory() as temp:
  exe=Path(temp)/'transport-test'
  subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-pedantic',*flags,*['-I'+str(x) for x in includes],*map(str,sources),'-lm','-o',str(exe)],check=True)
  r=subprocess.run([str(exe)],check=True,capture_output=True,text=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0'))
  wire=bytes.fromhex(next(x[5:] for x in r.stdout.splitlines() if x.startswith('WIRE=')))
  assert len(wire)==60
  fragments=[wire[i:i+20] for i in range(0,60,20)]
  assert all(f[:4]==struct.pack('<BBH',0xb1,i,0) for i,f in enumerate(fragments))
  raw=b''.join(f[4:] for f in fragments)
  assert len(raw)==48 and zlib.crc32(raw[:44])==int.from_bytes(raw[44:],'little')
  log=root/'verification'/f'host_{name}.log';log.write_text(r.stdout+r.stderr+'Python independent wire/CRC check PASS\n')
  print(name,r.stdout.splitlines()[0],'+ wire/CRC PASS')
