"""Executable protocol model, not flash driver or hardware durability proof."""
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class State:
    nor: frozenset = frozenset({0, 1})
    external: frozenset = frozenset()
    staged: frozenset = frozenset()  # may disappear on reset; never counts as durable
    ack: frozenset = frozenset()     # abstract crash-valid ACK metadata
    offered: int | None = None
    receipt: int | None = None  # volatile authenticated matching peer response
    delivered: frozenset = frozenset()  # oracle: authenticated peer accepted exact record

    def pending(self):
        return (self.nor | self.external) - self.ack

    def step(self, action, record=None):
        r = record
        if action == 'reset':
            return replace(self, staged=frozenset(), offered=None, receipt=None)
        if action == 'offer':
            if self.offered is not None or r not in self.pending():
                raise ValueError('not offerable')
            return replace(self, offered=r)
        if action == 'peer_accept':
            if self.offered != r:
                raise ValueError('ACK must match exact current offer')
            return replace(self, delivered=self.delivered | {r}, receipt=r)
        if action == 'ack_commit':
            if self.offered != r or self.receipt != r or r not in self.delivered:
                raise ValueError('no matching authenticated ACK')
            return replace(self, ack=self.ack | {r}, offered=None, receipt=None)
        if action == 'copy_stage':
            if r not in self.nor:
                raise ValueError('no source')
            return replace(self, staged=self.staged | {r})
        if action == 'copy_commit':
            if r not in self.staged or r not in self.nor:
                raise ValueError('no verified copy')
            return replace(self, external=self.external | {r}, staged=self.staged - {r})
        if action == 'erase_nor':
            # Whole modeled NOR erase unit: migration is NOT a host ACK.
            if self.offered is not None or not self.nor <= self.external:
                raise ValueError('retain all records until external durable handoff')
            return replace(self, nor=frozenset(), staged=frozenset())
        if action == 'erase_external':
            # Whole modeled external erase unit, only after every stored record ACKed.
            if self.offered is not None or not self.external <= self.ack:
                raise ValueError('unacknowledged external records')
            return replace(self, external=frozenset())
        if action == 'forget_ack':
            # ACK tombstone may disappear only after *every* old copy is gone.
            if r not in self.ack or r in self.nor | self.external | self.staged:
                raise ValueError('old copy could resurrect')
            return replace(self, ack=self.ack - {r})
        raise ValueError('unknown action')


def check(s):
    original = frozenset({0, 1})
    if not original - s.delivered <= s.pending():
        raise RuntimeError('unacknowledged durable input lost')
    if not s.ack <= s.delivered:
        raise RuntimeError('migration fabricated host ACK')
    if not s.pending() <= original:
        raise RuntimeError('invented input')
    if s.offered is not None and s.offered not in s.pending():
        raise RuntimeError('offer changed or reclaimed')


def recover_payloads(nor, external, ack):
    """Inputs contain only independently validated committed records.
    Key is (device, session, sequence); bytes must be exactly original 48 bytes.
    A bad checksum must be detected by adapter before this function, not ignored.
    """
    merged = {}
    for key, payload in list(nor) + list(external):
        if len(key) != 3 or len(payload) != 48:
            raise ValueError('invalid record')
        if key in merged and merged[key] != payload:
            raise ValueError('conflicting durable copies: fail closed')
        merged[key] = payload
    return {key: value for key, value in merged.items() if key not in ack}
