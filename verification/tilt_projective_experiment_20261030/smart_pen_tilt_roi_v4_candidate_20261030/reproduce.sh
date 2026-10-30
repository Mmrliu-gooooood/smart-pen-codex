#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1
PY="${PYTHON:-python}"
fail=0
run(){ echo "+ $*"; "$@" || { rc=$?; echo "EXIT $rc: $*"; fail=1; }; }
run "$PY" verify_frozen_sources.py
run "$PY" diagnose_components.py
run "$PY" replay_eight.py baseline_eight.json
run "$PY" diagnose_model.py
run "$PY" probe_eight.py
if [[ -f verify_eight_oracle.py ]]; then run "$PY" verify_eight_oracle.py; fi
run "$PY" heldout_selftest.py
run "$PY" run_heldout.py
run "$PY" test_support_oracle.py
run "$PY" run_regression.py
run "$PY" replay_legacy44.py
run "$PY" safety_v4.py
run "$PY" seedcap_v4.py
# Full host suite needs cv2,numpy,fastapi,httpx,uvicorn,bleak and pinned upstream.
HOST_PY="${HOST_PYTHON:-../smart_pen_host_venv_20261028/bin/python}"
run "$HOST_PY" source/software/verify_host.py --upstream-pc-src ../smart_pen_original_20261028/digital_pen_ov5640/pc/src
# A rejected experimental gate returns nonzero on purpose: never mask failures.
exit "$fail"
