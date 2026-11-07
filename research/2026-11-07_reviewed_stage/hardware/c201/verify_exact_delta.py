#!/usr/bin/env python3
"""Read-only byte check of the two-line C201 delta, not an electrical test."""
import argparse
import hashlib
import json
from pathlib import Path

def digest(data):
    return hashlib.sha256(data).hexdigest()

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', required=True, type=Path)
parser.add_argument('--candidate', type=Path)
args = parser.parse_args()
here = Path(__file__).resolve().parent
facts = json.loads((here / 'EXACT_DELTA.json').read_text())
for p in [args.source] + ([args.candidate] if args.candidate else []):
    if p.is_symlink() or not p.is_file():
        raise SystemExit('Expected a regular, explicitly supplied board file')
source = args.source.read_bytes()
if digest(source) != facts['source']['sha256'] or len(source) != facts['source']['bytes']:
    raise SystemExit('Source identity mismatch; do not apply by net number')
delta = (here / 'ADDED_SEGMENTS.sexpr').read_bytes()
if digest(delta) != facts['added_segments_sha256'] or not source.endswith(facts['insertion']['required_source_suffix'].encode()):
    raise SystemExit('Delta or terminal byte mismatch')
lines = delta.splitlines(keepends=True)
if len(lines) != 2 or not all(x.startswith(b'  (segment ') and x.endswith(b'\n') for x in lines):
    raise SystemExit('Expected exactly two segment lines')
terminal = facts['insertion']['before_exact_terminal_bytes'].encode()
if terminal != b')\n' or not source.endswith(terminal):
    raise SystemExit('Unexpected insertion point')
candidate = source[:-len(terminal)] + delta + source[-len(terminal):]
if digest(candidate) != facts['candidate']['sha256'] or len(candidate) != facts['candidate']['bytes']:
    raise SystemExit('Reconstructed byte identity mismatch')
if args.candidate and args.candidate.read_bytes() != candidate:
    raise SystemExit('Supplied candidate differs from the exact two-line delta')
print(json.dumps({'status':'EXACT_TWO_LINE_DELTA_PASS','source_sha256':digest(source),
 'candidate_sha256':digest(candidate),'writes':False,'engineering_rerun':False,
 'standalone_project':False,'NOFAB':True,'NOPOWER':True,'commission':'OPEN',
 'qualification':None,'current_rating_A':None,'effective_C':None}, sort_keys=True))
