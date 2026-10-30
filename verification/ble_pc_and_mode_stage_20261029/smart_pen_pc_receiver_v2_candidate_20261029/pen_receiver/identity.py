"""Local source namespaces and a fail-closed event merge seam; not authentication."""
import hashlib
import json
import re


def source_namespace(binding):
    body = json.dumps({'profile': 'SP1-DEV_USB-NO_SENSOR', 'binding': binding},
                      sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')
    return 'pen-source-v2:' + hashlib.sha256(body).hexdigest()


def record_digest(record):
    return hashlib.sha256(record.encode()).hexdigest()


class EventIdentityGuard:
    """Bounded by caller's selected replay set. No storage/ACK/security authority.

    Feed every DIAGNOSTIC (or DURABLE_RECORD) before merging a selected export.
    Returns False for same record replay; different bytes at same identity raise.
    Boundary events must NOT be merged as ink or independently reassembled here.
    """
    def __init__(self):
        self.seen = {}

    def accept(self, event):
        if event.get('type') not in ('DIAGNOSTIC', 'DURABLE_RECORD'):
            raise ValueError('identity guard accepts record events only, not boundaries')
        namespace = event.get('source_namespace', '')
        digest = event.get('record_sha256', '')
        if not isinstance(namespace, str) or not re.fullmatch(r'pen-source-v2:[0-9a-f]{64}', namespace):
            raise ValueError('missing/invalid v2 source namespace')
        if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
            raise ValueError('missing/invalid record digest')
        device, session, seq = event.get('device'), event.get('session'), event.get('seq')
        if (type(device) is not int or not 0 <= device < 2**32 or type(seq) is not int
                or not 0 <= seq < 2**32 or not isinstance(session, str)
                or not re.fullmatch(r'[1-9][0-9]*', session) or not int(session) < 2**64):
            raise ValueError('invalid record identity')
        key = (namespace, device, session, seq)
        old = self.seen.get(key)
        if old is not None and old != digest:
            raise ValueError('conflicting merged record: same source/session/seq, different bytes')
        self.seen[key] = digest
        return old is None
