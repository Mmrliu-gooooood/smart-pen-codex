from pathlib import Path
import re,json,hashlib
p=Path(__file__).resolve().parents[1];cfg=(p/'build-enabled.config').read_text();sym=(p/'verification/symbols-enabled.txt').read_text();image=(p/'verification/image-info-enabled.txt').read_text();link=(p/'build-enabled/smartpen_continuous_v3_bench.map').read_text();asm=(p/'verification/target-callgraph.txt').read_text()
for k in ['CONFIG_APP_BUILD_TYPE_RAM=y','CONFIG_APP_BUILD_TYPE_PURE_RAM_APP=y','CONFIG_PEN_DECODER_BENCH_RUN=y','# CONFIG_NEWLIB_NANO_FORMAT is not set']:assert k in cfg,k
for k in ['CONFIG_SPIRAM=y','CONFIG_BT_ENABLED=y','CONFIG_ESP_WIFI_ENABLED=y','CONFIG_NEWLIB_NANO_FORMAT=y']:assert k not in cfg,k
banned=r'\b(?:nvs_(?:flash_init|flash_erase|set_\w+|commit)|esp_wifi_init|esp_bt_controller_init|gpio_(?:config|set_level)|ledc_(?:timer_config|channel_config)|esp_camera_init|esp_partition_(?:write|erase_range)|esp_flash_(?:write|erase_region)|esp_ota_begin|esp_efuse_write_\w+)\b'
assert not re.findall(banned,sym),re.findall(banned,sym)
assert 'IROM' not in image and 'DROM' not in image
for name in ['pen_roi_decode_continuous','pen_roi_decode_refined_transform','__wrap_pen_roi_decode_refined_transform','pen_roi_decode_opt_frozen','_vfprintf_r','_dtoa_r','snprintf']:assert re.search(r'^403[0-9a-f]+ T '+name+r'$',sym,re.M),name
assert 'libc.a(libc_a-vfprintf.o)' in link and 'libc_nano.a' not in link
# The actual Xtensa machine call must target wrapper, not merely a host trace mock.
def body(name):
 m=re.search(r'^[0-9a-f]+ <'+name+r'>:\n(.*?)(?=^[0-9a-f]+ <|\Z)',asm,re.M|re.S);assert m,name;return m.group(1)
assert re.search(r'call\d+.*<__wrap_pen_roi_decode_refined_transform>',body('pen_roi_decode_continuous'))
assert re.search(r'call\d+.*<pen_roi_decode_refined_transform>',body('__wrap_pen_roi_decode_refined_transform'))
commands=(p/'build-enabled/compile_commands.json').read_text();assert '-flto' not in commands
bindings=json.loads((p/'SOURCE_BINDINGS.json').read_text());assert bindings['v3_snapshot_sha256']=='1636084759c3ebfc358574f669ea5292b11ae4421145401e7c2ccaed12664ccf'
for name,r in bindings['files'].items():assert hashlib.sha256((p/name).read_bytes()).hexdigest()==r['sha256'],name
legacy=json.loads((p/'verification/LEGACY_SOURCE_SNAPSHOT.json').read_text())['files']
for f in (p/'legacy/vision').glob('*'):assert hashlib.sha256(f.read_bytes()).hexdigest()==legacy['vision/'+f.name]
for folder in ['codec','legacy/codec']:
 for f in (p/folder).glob('*'):assert hashlib.sha256(f.read_bytes()).hexdigest()==legacy['codec/'+f.name]
print(json.dumps(dict(scope='Compile/link/disassembly only; no device run',v3_source_binding=True,legacy_frozen=True,pure_ram=True,nano_format=False,full_printf_iram=True,target_disassembly_proves_wrap=True,production_seeds_limit=64,radio_storage_gpio_providers_absent=True,flash_mapped_segments_absent=True,binary_sha256=hashlib.sha256((p/'build-enabled/smartpen_continuous_v3_bench.bin').read_bytes()).hexdigest()),indent=2))
