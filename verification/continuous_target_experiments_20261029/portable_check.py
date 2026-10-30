"""Recheck r7 in disposable local copies, using installed Python/cc/ASAN only.
No target SDK, device, network, installation or saved fake serial measurements.
Preserves frozen originals; prints a new host-only JSON report.
"""
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
BENCH = 'smart_pen_continuous_target_benchmark_20261029'
REVIEW = 'smart_pen_continuous_target_review_20261029'


def require(value, message):
    if not value:
        raise RuntimeError(message)


def verify():
    files = json.loads((HERE / 'SOURCE_SUBSET_SHA256.json').read_text())['files']
    for row in files:
        relative = Path(row['path'])
        require(not relative.is_absolute() and '..' not in relative.parts, 'unsafe path')
        p = HERE / relative
        require(p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(HERE), 'source path')
        b = p.read_bytes()
        require(len(b) == row['bytes'] and hashlib.sha256(b).hexdigest() == row['sha256'], str(relative))
    return len(files)


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
        for k in old:
            compare(old[k], new[k], label + '/' + k)
    else:
        raise TypeError(label)


def main():
    count = verify()
    report = {'scope': 'portable host-only checks; not target libc execution or FPS',
              'source_evidence_files_verified': count, 'device_measured': False,
              'target_sdk_rebuilt': False, 'frozen_files_unchanged': True,
              'format_runtime_on_actual_target': 'not run'}
    with tempfile.TemporaryDirectory(prefix='smartpen-r7-check-') as directory:
        work = Path(directory)
        for name in (BENCH, REVIEW):
            shutil.copytree(HERE / name, work / name)
        bench, review = work / BENCH, work / REVIEW
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PEN_BENCH_SOURCE=str(bench))

        def run(script):
            p = subprocess.run([sys.executable, str(script)], cwd=work, env=env, text=True, capture_output=True)
            require(p.returncode == 0, script.name + '\n' + p.stdout + p.stderr)
            return p

        # The review already contains the exact upstream generator manifest;
        # materialize only that one historical path in the disposable workspace.
        oracle_source = review / 'generator_oracles.json'
        expected = json.loads((bench / 'fixtures/independent_geometry.json').read_text())['source_manifest_sha256']
        require(hashlib.sha256(oracle_source.read_bytes()).hexdigest() == expected, 'generator manifest identity')
        alias = work / 'smart_pen_continuous_roi_candidate_20261028/tests/fixtures/continuous/manifest.json'
        alias.parent.mkdir(parents=True)
        alias.write_bytes(oracle_source.read_bytes())
        run(bench / 'tools/freeze_independent_geometry.py')
        require((bench / 'fixtures/independent_geometry.json').read_bytes() ==
                (HERE / BENCH / 'fixtures/independent_geometry.json').read_bytes(), 'geometry extraction bytes')
        run(bench / 'tools/freeze_legacy_oracles.py')
        require((bench / 'fixtures/manifest.json').read_bytes() ==
                (HERE / BENCH / 'fixtures/manifest.json').read_bytes(), 'legacy oracle bytes')
        report['geometry_extraction_from_included_review_manifest_byte_exact'] = True
        report['legacy_oracle_recalculation_byte_exact'] = True
        run(bench / 'tools/embed_fixtures.py')
        for relative in ('main/fixtures.h', 'verification/build-inputs.json'):
            require((bench / relative).read_bytes() == (HERE / BENCH / relative).read_bytes(), 'rebuilt ' + relative)
        report['packed_rle_and_source_binding_byte_exact'] = True
        host = json.loads(run(bench / 'tools/check_host.py').stdout)
        compare(json.loads((HERE / BENCH / 'verification/host-functional.json').read_text()), host, 'host_functional')
        require(len(host['records']) == 12, 'host record count')
        report['functional_records'] = 12
        geometry = json.loads(run(bench / 'tools/check_geometry.py').stdout)
        compare(json.loads((HERE / BENCH / 'verification/independent-geometry.json').read_text()), geometry, 'author_geometry')
        report['author_geometry_checked'] = True
        tests = run(bench / 'tools/test_serial_parser.py')
        test_log = tests.stdout + tests.stderr
        require(re.search(r'Ran 13 tests\b', test_log) and '\nOK\n' in test_log, test_log)
        report['author_parser_tests_passed'] = 13
        negatives = json.loads(run(review / 'run_parser_negatives.py').stdout)
        compare(json.loads((HERE / REVIEW / 'parser_negatives.log').read_text()), negatives, 'independent_parser')
        require(negatives['cases'] == 34, 'independent parser count')
        report['independent_parser_cases_passed'] = 34
        independent = json.loads(run(review / 'check_independent_geometry.py').stdout)
        compare(json.loads((HERE / REVIEW / 'independent_geometry.log').read_text()), independent, 'independent_geometry')
        report['independent_geometry_points'] = independent['points']
        mock = json.loads(run(review / 'run_actual_main.py').stdout)
        compare(json.loads((HERE / REVIEW / 'actual_main_mock.log').read_text()), mock, 'actual_main_host_mock')
        require(len(mock) == 6 and all(x['passed'] for x in mock), 'main mock count')
        report['actual_main_host_cases'] = mock
        report['mock_clock_warning'] = 'Artificial increments 123 only check timer boundaries; no fake target serial capture is published.'
        report['sanitizer_scope'] = 'Host ASAN+UBSAN only; LeakSanitizer disabled by original reviewed script.'
    require(verify() == count, 'post-run source recheck')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
