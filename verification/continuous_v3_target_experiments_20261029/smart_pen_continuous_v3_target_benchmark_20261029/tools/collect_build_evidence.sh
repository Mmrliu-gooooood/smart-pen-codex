#!/usr/bin/env bash
# Local build artifact inspection only. No device connection or execution.
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$root"
elf=build-enabled/smartpen_continuous_v3_bench.elf
python -m esptool --chip esp32s3 image_info build-enabled/smartpen_continuous_v3_bench.bin > verification/image-info-enabled.txt
xtensa-esp32s3-elf-nm "$elf" > verification/symbols-enabled.txt
xtensa-esp32s3-elf-size "$elf" > verification/size-enabled.txt
xtensa-esp32s3-elf-objdump -h "$elf" > verification/sections-enabled.txt
xtensa-esp32s3-elf-objdump -d "$elf" | python -c '
import re,sys
from pathlib import Path
s=sys.stdin.read();parts=[]
for name in ["pen_roi_decode_continuous","__wrap_pen_roi_decode_refined_transform"]:
 m=re.search(r"^[0-9a-f]+ <"+name+r">:\n(.*?)(?=^[0-9a-f]+ <|\Z)",s,re.M|re.S)
 assert m,name
 parts.append(m.group(0))
Path("verification/target-callgraph.txt").write_text("\n".join(parts))
'
find build-enabled/esp-idf/main -name '*.su' -exec cat {} + > verification/compiler-stack-usage.txt
grep -E 'NEWLIB_NANO_FORMAT|APP_BUILD_TYPE|PEN_DECODER|ESP_MAIN_TASK_STACK_SIZE' build-enabled.config > verification/effective-config-excerpt.txt
grep -n -E 'libc_a-(vfprintf|dtoa|snprintf)' build-enabled/smartpen_continuous_v3_bench.map > verification/full-libc-link-excerpt.txt
xtensa-esp32s3-elf-gcc -std=c11 -Wall -Wextra -Werror -Ivision -c verification/abi_assert.c -o build-enabled/abi_assert.o
printf 'Xtensa ABI PASS: core21888 + seeds1536 + crop9216 = workspace32640B, production limit64\n' > verification/abi-assert.log
python tools/check_static.py > verification/static-check.json
