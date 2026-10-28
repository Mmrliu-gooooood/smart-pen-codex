"""Re-encode every frozen vector with the ORIGINAL paper generator (not C).

Usage: python tools/verify_roi_fixture_source.py /path/to/py_microdots_develop
Needs upstream generator's numpy dependency. No internet/downloads required.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('generator_root', help='original py_microdots_develop directory')
source = Path(parser.parse_args().generator_root).resolve()
sys.path.insert(0, str(source))
from microdots import anoto_6x6_a4_fixed  # noqa: E402

fixture = root/'tests/fixtures/microdots_vectors.json'
vectors = json.loads(fixture.read_text())
sections = sorted({tuple(v['section']) for v in vectors})
for section in sections:
    bits = anoto_6x6_a4_fixed.encode_bitmatrix((1000, 710), section)
    for v in vectors:
        if tuple(v['section']) != section:
            continue
        x, y = v['xy']
        window = bits[y:y+6, x:x+6]
        actual = (window[:, :, 0] + 2*window[:, :, 1]).reshape(-1).tolist()
        assert actual == v['directions'], (section, x, y)
seven = json.loads((root/'tests/fixtures/roi_seven.json').read_text())
bits = anoto_6x6_a4_fixed.encode_bitmatrix((1000, 710), tuple(seven['section']))
x, y = seven['xy']
window = bits[y:y+7, x:x+7]
assert (window[:, :, 0] + 2*window[:, :, 1]).reshape(-1).tolist() == seven['directions']
print(json.dumps({
    'verified_seven_by_seven': True,
    'verified_windows': len(vectors), 'sections': sections,
    'fixture_sha256': hashlib.sha256(fixture.read_bytes()).hexdigest(),
    'generator_files_sha256': {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sorted((source/'microdots').glob('*.py'))},
    'method': 'original Python encode_bitmatrix; no firmware decoder/encoder used'
}, indent=2))
