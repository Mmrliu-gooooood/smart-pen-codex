#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SDK="${PEN_SDK_ROOT:-$(dirname "$ROOT")/smart_pen_sdk_20261028}"
OUT="${PEN_CAMERA_BUILD_ROOT:-$(dirname "$ROOT")/smart_pen_camera_capture_v2_build_20261029}"
export IDF_TOOLS_PATH="$SDK/tools"
. "$SDK/esp-idf/export.sh" >/dev/null
export PATH="$IDF_TOOLS_PATH/python_env/idf5.4_py3.12_env/bin:$PATH"
export IDF_COMPONENT_MANAGER=0
mkdir -p "$OUT"
cd "$ROOT/idf"
for mode in disabled enabled; do
 defaults="$PWD/sdkconfig.defaults"
 if [[ "$mode" == enabled ]]; then defaults="$PWD/sdkconfig.enabled_compile.defaults"; fi
 idf.py -B "$OUT/$mode" -D SDKCONFIG="$OUT/$mode.config" -D SDKCONFIG_DEFAULTS="$defaults" \
 -D IDF_TARGET=esp32s3 -D CMAKE_MAKE_PROGRAM="$IDF_TOOLS_PATH/python_env/idf5.4_py3.12_env/bin/ninja" build > "$ROOT/verification/idf-$mode.log" 2>&1
 echo "$mode compile/link PASS"
done
