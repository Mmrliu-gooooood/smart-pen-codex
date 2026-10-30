from pathlib import Path
import re,json,hashlib
p=Path(__file__).resolve().parents[1];cfg=(p/'build-enabled.config').read_text();sym=(p/'verification/symbols-enabled.txt').read_text();image=(p/'verification/image-info-enabled.txt').read_text();link=(p/'build-enabled/smartpen_continuous_bench.map').read_text()
for k in ['CONFIG_APP_BUILD_TYPE_RAM=y','CONFIG_APP_BUILD_TYPE_PURE_RAM_APP=y','CONFIG_PEN_DECODER_BENCH_RUN=y','# CONFIG_NEWLIB_NANO_FORMAT is not set']:assert k in cfg,k
for k in ['CONFIG_SPIRAM=y','CONFIG_BT_ENABLED=y','CONFIG_ESP_WIFI_ENABLED=y','CONFIG_NEWLIB_NANO_FORMAT=y']:assert k not in cfg,k
banned=r'\b(?:nvs_(?:flash_init|flash_erase|set_\w+|commit)|esp_wifi_init|esp_bt_controller_init|gpio_(?:config|set_level)|ledc_(?:timer_config|channel_config)|esp_camera_init|esp_partition_(?:write|erase_range)|esp_flash_(?:write|erase_region)|esp_ota_begin|esp_efuse_write_\w+)\b'
assert not re.findall(banned,sym),re.findall(banned,sym)
for f in [p/'main/bench_main.c',*p.glob('vision/*.c'),*p.glob('legacy/vision/*.c')]:assert not re.findall(banned,f.read_text())
assert 'IROM' not in image and 'DROM' not in image
for name in ['pen_roi_decode_continuous','pen_roi_decode_opt_transform','pen_roi_decode_opt_frozen','_vfprintf_r','_dtoa_r','snprintf']:assert re.search(r'^403[0-9a-f]+ T '+name+r'$',sym,re.M),name
assert 'libc.a(libc_a-vfprintf.o)' in link
assert 'libc_nano.a' not in link
origin=json.loads((p/'verification/CANDIDATE_SNAPSHOT.json').read_text());hashes={x['path']:x['sha256'] for x in origin['files']}
for f in (p/'vision').glob('*'):assert hashlib.sha256(f.read_bytes()).hexdigest()==hashes['firmware/vision/'+f.name]
legacy=json.loads((p/'verification/LEGACY_SOURCE_SNAPSHOT.json').read_text())['files']
for f in (p/'legacy/vision').glob('*'):assert hashlib.sha256(f.read_bytes()).hexdigest()==legacy['vision/'+f.name]
for folder in ['codec','legacy/codec']:
 for f in (p/folder).glob('*'):assert hashlib.sha256(f.read_bytes()).hexdigest()==legacy['codec/'+f.name]
print(json.dumps(dict(scope='Compile/link only; no device execution or timing',pure_ram=True,radio_storage_gpio_providers_absent=True,nano_format=False,full_printf_vfprintf_and_dtoa_linked_in_iram=True,candidate_snapshot_match=True,frozen_legacy_match=True,flash_mapped_image_segments_absent=True,console_exception='UART0 and secondary USB console pads are not inert',binary_sha256=hashlib.sha256((p/'build-enabled/smartpen_continuous_bench.bin').read_bytes()).hexdigest()),indent=2))
