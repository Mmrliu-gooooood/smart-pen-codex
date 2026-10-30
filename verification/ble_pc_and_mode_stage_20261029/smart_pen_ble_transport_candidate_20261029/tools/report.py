#!/usr/bin/env python3
"""Bind this build's vendor artifacts to exact source; never touches hardware."""
from pathlib import Path
import hashlib,json,os,subprocess
R=Path(__file__).resolve().parents[1]
SDK=Path(os.getenv('PEN_SDK_ROOT',str(R.parent/'smart_pen_sdk_20261028')))
OUT=Path(os.getenv('PEN_BLE_BUILD_ROOT',str(R.parent/'smart_pen_ble_build_20261029')))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source={str(p.relative_to(R)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(R.rglob('*')) if p.is_file() and p.relative_to(R).parts[0] not in ('verification','review') and '__pycache__' not in p.parts}
manifest=R/'verification/source_manifest.json';manifest.write_text(json.dumps(source,indent=2)+'\n')
nm=next((SDK/'tools/tools/xtensa-esp-elf').glob('*/xtensa-esp-elf/bin/xtensa-esp32s3-elf-nm'))
required=['pen_ble_dev_start','pen_ble_dev_advertise','pen_ble_dev_peer','pen_ble_dev_approve','pen_ble_quiesce','pen_ble_resume','pen_ble_transport_backend','pen_ble_actor_init','pen_ble_actor_turn','pen_get_board_provider']
report={'sdk_commit':subprocess.check_output(['git','-C',str(SDK/'esp-idf'),'rev-parse','HEAD'],text=True).strip(),'source_manifest_sha256':sha(manifest),'hardware_run':False,'configurations':{}}
assert report['sdk_commit']=='67c1de1eebe095d554d281952fde63c16ee2dca0'
for mode in ('disabled','enabled'):
 b=OUT/mode;elf=b/'smartpen_ble_compile.elf';sym=subprocess.check_output([str(nm),str(elf)],text=True)
 assert all(any(line.endswith(' '+name) for line in sym.splitlines()) for name in required)
 cfg=(OUT/(mode+'.config')).read_text();log=(R/'verification'/('idf-'+mode+'.log')).read_text()
 assert 'Project build complete.' in log and 'error:' not in log and 'warning:' not in log
 assert ('CONFIG_PEN_BLE_TRANSPORT=y' in cfg)==(mode=='enabled')
 if mode=='enabled':
  for s in ('CONFIG_BT_NIMBLE_SM_LVL=4','CONFIG_BT_NIMBLE_MAX_CONNECTIONS=1','CONFIG_BT_NIMBLE_NVS_PERSIST=y','CONFIG_BT_NIMBLE_SM_SC=y','# CONFIG_BT_NIMBLE_SM_LEGACY is not set','# CONFIG_BT_NIMBLE_SM_SC_DEBUG_KEYS is not set'):assert s in cfg,s
  assert ' ble_gap_adv_start' in sym
 else:assert ' ble_gap_adv_start' not in sym
 files={str(p.relative_to(b)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in (elf,b/'smartpen_ble_compile.bin',b/'partition_table/partition-table.bin')}
 report['configurations'][mode]={'files':files,'retained_symbols':required,'sdkconfig_sha256':sha(OUT/(mode+'.config')),'config':[s for s in cfg.splitlines() if any(k in s for k in ('CONFIG_PEN_BLE','CONFIG_BT_NIMBLE_SM_','CONFIG_BT_NIMBLE_NVS_PERSIST','CONFIG_BT_NIMBLE_MAX_CONNECTIONS','CONFIG_BT_NIMBLE_MAX_BONDS','CONFIG_ESPTOOLPY_FLASHSIZE'))]}
(R/'verification/build_report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({m:report['configurations'][m]['files']['smartpen_ble_compile.bin'] for m in report['configurations']},indent=2))
# Optional unchanged frozen baseline check, separate from compact vendored copies.
B=R.parent/'smart_pen_app_pipeline_20261028'
if B.exists():
 old=json.loads((B/'verification/application_source_manifest.json').read_text())
 mismatches=[p for p,h in old.items() if sha(B/p)!=h]
 assert not mismatches,mismatches
 deps=json.loads((R/'verification/frozen_dependencies.json').read_text())
 assert all(sha(R/x['path'])==x['sha256'] and sha(R.parent/x['source'])==x['sha256'] for x in deps)
 (R/'verification/frozen_unchanged.json').write_text(json.dumps({'original_manifest_files':len(old),'mismatches':mismatches,'copied_dependencies':len(deps),'all_exact':True},indent=2)+'\n')
