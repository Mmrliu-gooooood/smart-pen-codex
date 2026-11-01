# Replay in a new writable reconstruction

Prerequisites: Python3 with NumPy and a C11 compiler; native ASan/UBSan support for the sanitizer configurations. No physical hardware/SDK implied.

1. From repository root: `python3 verification/optics_fullroi_20261031/reconstruct.py /absolute/new/empty/workspace`.
2. In reconstructed `optics_paper_screen_20261031_1752`: run `python3 -B -m unittest -v`, `python3 -B -O -m unittest -v`, `sweep.py`, `compare_crops.py`; in `decoder_probe`, run `sweep_active.py` and `controls_active.py`.
3. In reconstructed `optics_v3_comparison_20261031_1759/replay`: run `python3 -B replay_v3.py`; in `legacy408`, run `python3 -B run.py`. Preserve original frozen results separately; compare semantic records excluding host wall-clock durations. Legacy408 uses the historical oracle, not a new transform or physical-support guarantee.
4. In reconstructed `orthogonal_refine_fullroi_candidate_20261031_1806`: run `python3 -B test_candidate.py`, `python3 -B -O test_candidate.py`, `python3 -B check_default.py`, and `python3 -B run_native.py`. In `regression`, run `python3 -B run.py --enabled 0` and `python3 -B run.py --enabled 1`. Both must retain all required negative rejections. `--enabled 1 --targeted` is a bounded diagnostic subset, not a substitute for478 cases.

Do not modify frozen repository files to collect new outputs. Native scripts generate binaries in temporary directories, not committed deliverables. Compare every input/source hash against its frozen manifest before and after. Historical reports containing temporary absolute paths record their original environment; use the module's relative replay entrypoint rather than assuming old workspace exists.

Expected finite synthetic results: active70 22/0/48; cropV3 70 29/0/41; legacy408 254/0/154; fullROI OFF478 23/0/455, ON478 32/0/446. Counts are correct/invalid/reject, not physical accuracy or false-accept probabilities. Production remains defaultOFF/NULL; no continuous-paper, camera, MCU timing, optical or manufacturing qualification.
