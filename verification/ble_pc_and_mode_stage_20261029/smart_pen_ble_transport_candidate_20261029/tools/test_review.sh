#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PEN_BLE_REVIEW_SOURCE="$ROOT"
export PEN_BLE_FROZEN_SOURCE="$ROOT/frozen"
export PEN_BLE_REVIEW_OUTPUT="${PEN_BLE_REVIEW_OUTPUT:-$(mktemp -d /tmp/pen-ble-review.XXXXXX)}"
for suite in extra actor_extra idf_extra; do python "$ROOT/review/run_$suite.py"; done
echo "Independent review outputs: $PEN_BLE_REVIEW_OUTPUT"
