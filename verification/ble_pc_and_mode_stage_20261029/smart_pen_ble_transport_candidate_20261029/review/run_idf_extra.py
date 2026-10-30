"""Independent review: source/frozen/output paths may be overridden via environment."""
from pathlib import Path
import os, subprocess, hashlib, json
R=Path(__file__).resolve().parent
S=Path(os.environ.get('PEN_BLE_REVIEW_SOURCE',R.parent/'smart_pen_ble_transport_candidate_20261029')).resolve()
# This is the firmware tree itself, e.g. candidate/frozen, not a repo parent.
F=Path(os.environ.get('PEN_BLE_FROZEN_SOURCE',S/'frozen')).resolve()
O=Path(os.environ.get('PEN_BLE_REVIEW_OUTPUT',R/'run_output')).resolve();O.mkdir(parents=True,exist_ok=True)
source=[S/'src/pen_ble_core.c',S/'src/pen_ble_actor.c',R/'test_idf_extra.c']+[F/p for p in ['application/pipeline.c','portable/pen.c','storage/store.c','runtime/recorder.c','runtime/contact_power.c','vision/roi_opt.c','codec/anoto.c']]
inc=([R/"stubs"])+[S/'include']+[F/d for d in ['application','runtime','vision','codec','storage','portable']]
base=['cc','-std=c11','-Wall','-Wextra','-Werror','-pedantic']+['-I'+str(p) for p in inc]
base+=['-pthread','-DPEN_BLE_IDF_SOURCE=\"'+str(S/'src/pen_ble_idf.c')+'\"']
for variant,flags in [('normal',[]),('ndebug',['-DNDEBUG','-O2']),('asan',['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g'])]:
    binary=O/('idf_'+variant)
    subprocess.run(base+flags+[str(p) for p in source]+['-lm','-o',str(binary)],check=True)
    for args in [[]]+[[c] for c in ['init_fail', 'nvs_fail', 'weak_write', 'expired_write']]:
        p=subprocess.run([str(binary)]+args,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0'),text=True,capture_output=True)
        (O/('idf_'+variant+('_'+args[0] if args else '')+'.log')).write_text(p.stdout+p.stderr)
        print(variant,*args,p.stdout,p.stderr,sep='\n');p.check_returncode()
tracked=source+list((S/'include').glob('*.h'))+list(F.rglob('*.h'))
tracked+=[S/'src/pen_ble_idf.c']+list((R/'stubs').rglob('*.h'))
(O/'IDF_TESTED_MANIFEST.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in tracked},indent=2)+'\n')
