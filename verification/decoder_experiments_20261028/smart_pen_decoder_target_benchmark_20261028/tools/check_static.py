"""Local static evidence; does not prove an uninspected board safe."""
from pathlib import Path
import re,json,hashlib
p=Path(__file__).resolve().parents[1]
cfg=(p/'build-enabled.config').read_text();sym=(p/'verification/symbols-enabled.txt').read_text();image=(p/'verification/image-info-enabled.txt').read_text()
required=['CONFIG_APP_BUILD_TYPE_RAM=y','CONFIG_APP_BUILD_TYPE_PURE_RAM_APP=y','CONFIG_PEN_DECODER_BENCH_RUN=y']
for x in required: assert x in cfg,x
for x in ['CONFIG_SPIRAM=y','CONFIG_BT_ENABLED=y','CONFIG_ESP_WIFI_ENABLED=y']: assert x not in cfg,x
banned=r'\b(?:nvs_(?:flash_init|flash_erase|set_\w+|commit)|esp_wifi_init|esp_bt_controller_init|gpio_(?:config|set_level)|ledc_(?:timer_config|channel_config)|esp_camera_init|esp_partition_(?:write|erase_range)|esp_flash_(?:write|erase_region)|esp_ota_begin|esp_efuse_write_\w+)\b'
assert not re.findall(banned,sym),re.findall(banned,sym)
for f in [p/'main/bench_main.c',p/'vision/roi_opt.c',p/'codec/anoto.c']: assert not re.findall(banned,f.read_text())
assert 'IROM' not in image and 'DROM' not in image
assert 'pen_roi_decode_opt' in sym
hashes={str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(p.glob('vision/*'))+sorted(p.glob('codec/*'))+[p/'build-enabled/smartpen_decoder_bench.bin']}
print(json.dumps({'scope':'compile/link/static only; not physical safety proof','required_configs':required,'radio_storage_board_mutators_absent':True,'flash_mapped_segments_absent':True,'console':'SDK UART0 115200 and secondary USB serial/JTAG; these console pads are not inert','hashes':hashes},indent=2))
