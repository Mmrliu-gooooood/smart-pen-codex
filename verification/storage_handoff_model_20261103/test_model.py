import json
import unittest
from dataclasses import replace
from model import State, check, recover_payloads

class ProtocolTests(unittest.TestCase):
    def test_exhaustive_reachable_states(self):
        actions = [(a, r) for a in ('offer','peer_accept','ack_commit','copy_stage','copy_commit','forget_ack') for r in (0,1)] + [(a,None) for a in ('reset','erase_nor','erase_external')]
        seen = {State()}; queue = [State()]; transitions = 0
        while queue:
            s = queue.pop()
            check(s)
            for a,r in actions:
                try: n = s.step(a,r)
                except ValueError: continue
                transitions += 1
                check(n)
                check(n.step('reset'))
                if n not in seen:
                    seen.add(n); queue.append(n)
        self.assertGreater(len(seen),100)
        print(json.dumps({'reachable_states':len(seen),'valid_transitions':transitions,'reset_checked_after_each_transition':True}))

    def test_staged_copy_does_not_allow_reclaim(self):
        s = State().step('copy_stage',0).step('copy_stage',1)
        with self.assertRaises(ValueError): s.step('erase_nor')
        self.assertEqual(s.step('reset').pending(),frozenset({0,1}))

    def test_copy_is_not_ack(self):
        s=State()
        for r in (0,1): s=s.step('copy_stage',r).step('copy_commit',r)
        s=s.step('erase_nor').step('reset')
        self.assertEqual(s.ack,frozenset())
        self.assertEqual(s.pending(),frozenset({0,1}))
        with self.assertRaises(ValueError): s.step('erase_external')

    def test_exact_offer_not_cumulative_ack(self):
        s=State().step('offer',1).step('peer_accept',1).step('ack_commit',1)
        self.assertEqual(s.pending(),frozenset({0}))
        with self.assertRaises(ValueError): s.step('ack_commit',0)

    def test_reset_between_peer_accept_and_ack_replays(self):
        s=State().step('offer',0).step('peer_accept',0).step('reset')
        self.assertIn(0,s.pending())
        with self.assertRaises(ValueError): s.step('ack_commit',0)
        s=s.step('offer',0)
        with self.assertRaises(ValueError): s.step('ack_commit',0)
        s=s.step('peer_accept',0).step('ack_commit',0)
        self.assertNotIn(0,s.pending())

    def test_tombstone_cannot_be_forgotten_with_old_copy(self):
        s=State().step('offer',0).step('peer_accept',0).step('ack_commit',0)
        with self.assertRaises(ValueError): s.step('forget_ack',0)

    def test_mutation_early_erase_detected(self):
        bad=replace(State().step('copy_stage',0),nor=frozenset())
        with self.assertRaises(RuntimeError): check(bad.step('reset'))

    def test_mutation_migration_as_ack_detected(self):
        with self.assertRaises(RuntimeError): check(replace(State(),ack=frozenset({0})))

    def test_payload_duplicate_and_conflict(self):
        k=(1,100,0); p=bytes(range(48))
        self.assertEqual(recover_payloads([(k,p)],[(k,p)],set()),{k:p})
        self.assertEqual(recover_payloads([(k,p)],[(k,p)],{k}),{})
        with self.assertRaises(ValueError): recover_payloads([(k,p)],[(k,b'x'*48)],set())
        with self.assertRaises(ValueError): recover_payloads([(k,p[:47])],[],set())

    def test_new_session_not_hidden_by_old_ack(self):
        old=(1,100,0); new=(1,101,0); p=bytes(48)
        self.assertEqual(recover_payloads([(old,p)],[(new,p)],{old}),{new:p})

if __name__ == '__main__': unittest.main(verbosity=2)
