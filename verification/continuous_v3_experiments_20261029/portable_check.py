"""Offline V3 capsule verification in temporary working copies.
Default: installed Python3.9+/cc/nm/libm; targeted tests, diagnostic pixel hashes.
--independent: also installed NumPy and the pinned r6 dependency subset.
No installation/network/target SDK/device actions or modifications to originals.
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
CANDIDATE = 'smart_pen_continuous_roi_v3_candidate_20261029'
DIAGNOSTIC = 'smart_pen_continuous_fit_diagnostic_20261029'
REVIEW = 'smart_pen_continuous_v3_independent_review_20261029'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def verify_rows(root, rows, key='path'):
    for row in rows:
        relative = Path(row[key])
        require(not relative.is_absolute() and '..' not in relative.parts, 'unsafe relative path')
        path = root / relative
        require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(root.resolve()), str(path))
        b = path.read_bytes()
        require(len(b) == row['bytes'] and hashlib.sha256(b).hexdigest() == row['sha256'], str(path))


def compare(old, new, label):
    if isinstance(old, bool) or old is None or isinstance(old, str):
        require(old == new, label)
    elif isinstance(old, (int, float)):
        require(isinstance(new, (int, float)) and abs(old-new) <= 1e-9*max(1, abs(old)), label)
    elif isinstance(old, list):
        require(isinstance(new, list) and len(old) == len(new), label)
        for i, (a, b) in enumerate(zip(old, new)):
            compare(a, b, label + '/' + str(i))
    elif isinstance(old, dict):
        require(isinstance(new, dict) and old.keys() == new.keys(), label)
        for key in old:
            compare(old[key], new[key], label + '/' + key)
    else:
        raise TypeError(label)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--independent', action='store_true')
    parser.add_argument('--dependency-root', type=Path, help='r6 continuous_roi_experiments_20261029 directory')
    args = parser.parse_args()
    originals = json.loads((HERE / 'SOURCE_SUBSET_SHA256.json').read_text())['files']
    verify_rows(HERE, originals)
    deps = json.loads((HERE / 'DEPENDENCY_LINKS.json').read_text())['files']
    dep_root = None
    if args.independent:
        try:
            import numpy  # installed already; never download/install automatically
        except ImportError as error:
            raise RuntimeError('--independent requires trusted Python with installed NumPy') from error
        candidates = [args.dependency_root] if args.dependency_root else [
            HERE.parent / 'continuous_roi_experiments_20261029',
            HERE.parents[2] / 'verified_revisions_r6/verification/continuous_roi_experiments_20261029']
        dep_root = next((p.resolve() for p in candidates if p and p.is_dir()), None)
        require(dep_root is not None, 'Provide --dependency-root pointing to the exact r6 experiment directory')
        verify_rows(dep_root, deps, 'capsule_path')
    diagnostic = json.loads((HERE / DIAGNOSTIC / 'results.json').read_text())
    require(len(diagnostic) == 132, 'diagnostic case count')
    missing = []
    for row in diagnostic:
        pgm = (HERE / DIAGNOSTIC / 'pixels' / f'case_{row["index"]:03d}.pgm').read_bytes()
        magic, dimensions, maximum, pixels = pgm.split(b'\n', 3)
        require(magic == b'P5' and dimensions == b'200 200' and maximum == b'255' and len(pixels) == 40000, 'PGM framing')
        require(hashlib.sha256(pixels).hexdigest() == row['image_sha256'] == row['source']['sha256'], 'diagnostic frozen pixels')
        if row['status'] != 0 and row['oracle_diagnosis_only']['complete_true_windows'] == 0:
            missing.append(row['index'])
    require(len(missing) == 20, 'diagnostic no-window count')
    report = {'scope': 'local synthetic host verification, no target execution or real-time claim',
              'copied_original_files_verified': len(originals),
              'diagnostic_raw_pixel_hashes_verified': 132,
              'diagnostic_truth_usage': 'post-hoc diagnosis only, never C inputs',
              'diagnostic_no_complete_window_count': 20,
              'target_sdk_rebuilt': False, 'device_measured': False,
              'original_85_host_gate_rerun': False, 'original_340_sweep_rerun': False,
              'full_diagnostic_experiments_rerun': False, 'sanitizer_rerun': False}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    with tempfile.TemporaryDirectory(prefix='smartpen-r8-check-') as directory:
        work = Path(directory)
        for name in (CANDIDATE, DIAGNOSTIC, REVIEW):
            shutil.copytree(HERE / name, work / name)
        if dep_root:
            for row in deps:
                source, target = dep_root / row['capsule_path'], work / row['capsule_path']
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
        test = subprocess.run([sys.executable, '-m', 'unittest', '-v', 'test_roi_continuous',
                               'test_roi_continuous_safety', 'test_roi_refine_v3_safety'],
                              cwd=work / CANDIDATE / 'tests', env=env, text=True, capture_output=True)
        log = test.stdout + test.stderr
        require(test.returncode == 0 and re.search(r'Ran 13 tests\b', log) and '\nOK\n' in log, log)
        report['targeted_host_tests_passed'] = 13
        report['targeted_host_tests_skipped'] = 0
        report['default64_and_cap1_native_tests'] = 'passed, non-sanitized host build'
        if dep_root:
            for script in ('review.py', 'verify_observed_support.py', 'overflow_probe.py'):
                process = subprocess.run([sys.executable, str(work / REVIEW / script)],
                                         cwd=work, env=env, text=True, capture_output=True)
                require(process.returncode == 0, script + '\n' + process.stdout + process.stderr)
            names = ('legacy44.json', 'replay72.json', 'phase48.json', 'fragments6.json',
                     'missing_window20.json', 'observed_support54.json', 'overflow_probe.json', 'summary.json')
            for name in names:
                compare(json.loads((HERE / REVIEW / name).read_text()),
                        json.loads((work / REVIEW / name).read_text()), name)
            require((HERE / REVIEW / 'overflow_pitch3.pgm').read_bytes() ==
                    (work / REVIEW / 'overflow_pitch3.pgm').read_bytes(), 'actual default overflow pixels')
            summary = json.loads((work / REVIEW / 'summary.json').read_text())
            overflow = json.loads((work / REVIEW / 'overflow_probe.json').read_text())[0]
            require(overflow == {'pitch': 3, 'status': -4, 'cold': 864, 'seeds': 65, 'iterations': 0, 'refined': 0}, 'real 65th seed reject')
            report['independent_reproduction'] = {'passed': True, 'reused_r6_files_verified': len(deps),
                'compared_frozen_jsons': list(names), 'summary': summary,
                'actual_default65_overflow': overflow, 'overflow_pgm_byte_exact': True,
                'v3_result_bytes': 192, 'v2_result_bytes': 184,
                'original_opt_cold_warm_result_prior_bytes_match_v2': True}
    verify_rows(HERE, originals)
    if dep_root:
        verify_rows(dep_root, deps, 'capsule_path')
    report['frozen_originals_and_reused_dependencies_unchanged'] = True
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
