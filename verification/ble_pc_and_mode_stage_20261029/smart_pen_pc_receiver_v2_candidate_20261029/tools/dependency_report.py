"""Read installed metadata/source files only. Does not import or construct Bleak."""
import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import platform
import sqlite3
import sys

root=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'python':sys.version,'platform':platform.platform(),'sqlite':sqlite3.sqlite_version,
        'radio_executed':False,'packages':{},'frozen_inputs':{},'upstream_commit':'0f8b569176c77dad34aaf83bb008eb118c9f1208'}
for name in ['bleak','dbus-fast']:
    dist=metadata.distribution(name)
    paths=[p for p in dist.files if str(p).endswith(('/METADATA','/LICENSE')) or str(p) in ('bleak/__init__.py','bleak/exc.py')]
    report['packages'][name]={'version':dist.version,'license':dist.metadata.get('License-Expression') or dist.metadata.get('License'),
                             'files':{str(p):sha(Path(dist.locate_file(p))) for p in paths}}
ble=root.parent/'smart_pen_ble_transport_candidate_20261029'
for p in ['docs/INTEGRATION.zh-CN.md','docs/DEVICE_GATES.zh-CN.md','src/pen_ble_core.c','src/pen_ble_idf.c',
          'frozen/portable/pen.c','frozen/portable/pen.h','frozen/runtime/contact_power.c','review/FINAL_CODE_TESTED_MANIFEST.json']:
    report['frozen_inputs'][str(Path(ble.name)/p)]=sha(ble/p)
up=root.parent/'smart_pen_original_20261028/digital_pen_ov5640/pc/src/digital_pen/engine/session.py'
report['frozen_inputs'][str(up.relative_to(root.parent))]=sha(up)
print(json.dumps(report,indent=2,ensure_ascii=False))
