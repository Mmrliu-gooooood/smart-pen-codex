"""Offline r6 checks in a disposable copy; never edit frozen source/evidence.
Quick: Python 3.9+, installed cc/nm/libm; eight candidate host tests.
--independent: additionally installed NumPy; regenerate V2 review using frozen
V1 pixels and the included V2 snapshot, plus isolated corner control.
No SDK, network, devices, downloads or target performance measurements.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
CANDIDATE = 'smart_pen_continuous_roi_candidate_20261028'
REVIEW = 'smart_pen_continuous_independent_review_20261029'


def check(value, message):
    if not value:
        raise RuntimeError(message)


def verify():
    rows = json.loads((HERE / 'SOURCE_SUBSET_SHA256.json').read_text())['files']
    for row in rows:
        rel = Path(row['path'])
        check(not rel.is_absolute() and '..' not in rel.parts, 'unsafe source path')
        p = HERE / rel
        check(p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(HERE), 'source outside capsule')
        data = p.read_bytes()
        check(len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'], str(rel))
    return len(rows)


def compare(old, new, label):
    # Review outputs contain no host times; retain exact image hashes/statuses and
    # tight float compatibility, allowing only final floating-point roundoff.
    if isinstance(old, bool) or old is None or isinstance(old, str):
        check(old == new, label)
    elif isinstance(old, (int, float)):
        check(isinstance(new, (int, float)) and abs(old-new) <= 1e-9*max(1, abs(old)), label)
    elif isinstance(old, list):
        check(isinstance(new, list) and len(old) == len(new), label)
        for i, (a, b) in enumerate(zip(old, new)):
            compare(a, b, label + '/' + str(i))
    elif isinstance(old, dict):
        check(isinstance(new, dict) and old.keys() == new.keys(), label)
        for key in old:
            compare(old[key], new[key], label + '/' + key)
    else:
        raise TypeError(label)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--independent', action='store_true')
    args = parser.parse_args()
    count = verify()
    if args.independent:
        try:
            import numpy  # already installed; never install/download automatically
        except ImportError as exc:
            raise RuntimeError('--independent requires a trusted interpreter with installed NumPy') from exc
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    report = {'scope': 'offline synthetic host checks only', 'source_files_verified': count,
              'device_measured': False, 'target_fps_claim': False,
              'application_record_chain_integrated': False, 'frozen_inputs_unchanged': True}
    with tempfile.TemporaryDirectory(prefix='smartpen-r6-check-') as directory:
        temporary = Path(directory)
        for name in (CANDIDATE, REVIEW, 'smart_pen_vision_opt_20261028', 'smart_pen_viewport_audit_20261028'):
            shutil.copytree(HERE / name, temporary / name)
        test = subprocess.run([sys.executable, '-m', 'unittest', '-v',
                               'test_roi_continuous', 'test_roi_continuous_safety'],
                              cwd=temporary / CANDIDATE / 'tests', env=environment,
                              text=True, capture_output=True)
        log = test.stdout + test.stderr
        check(test.returncode == 0 and re.search(r'Ran 8 tests\b', log) and '\nOK\n' in log, log)
        report['candidate_tests'] = {'passed': 8, 'skipped': 0, 'log': log,
                                     'full_original_80_test_gate_rerun': False}
        if args.independent:
            # These are the original reviewed scripts, not a replacement rasterizer.
            for script in ('v2_review.py', 'corner_control.py'):
                process = subprocess.run([sys.executable, str(temporary / REVIEW / script)],
                                         cwd=temporary, env=environment, text=True, capture_output=True)
                check(process.returncode == 0, script + '\n' + process.stdout + process.stderr)
            compared = []
            for name in ('replay_v1.json', 'phase.json', 'fragments.json', 'corner_control.json', 'summary.json'):
                old = json.loads((HERE / REVIEW / 'v2' / name).read_text())
                new = json.loads((temporary / REVIEW / 'v2' / name).read_text())
                compare(old, new, name)
                compared.append(name)
            for name in ('sliver1x4.pgm', 'half_disk.pgm', 'corner1x1.pgm', 'corner1x4.pgm', 'corner4x1.pgm', 'isolated_corner4x1.pgm'):
                check((HERE / REVIEW / 'v2' / name).read_bytes() == (temporary / REVIEW / 'v2' / name).read_bytes(), name)
                compared.append(name)
            summary = json.loads((temporary / REVIEW / 'v2/summary.json').read_text())
            report['independent_v2_reproduction'] = {'passed': True, 'frozen_v1_images_replayed': 72,
                'additional_phase_cases': 48, 'fragment_and_corner_images': 6,
                'compared_original_artifacts': compared, 'summary': summary,
                'original_v1_review_rerun': False, 'sanitizer_rerun': False}
    check(verify() == count, 'post-run frozen source verification')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
