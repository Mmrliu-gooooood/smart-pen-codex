import dataclasses
import struct
import unittest
import zlib
from pen_receiver.protocol import Record, Reassembler, fragments, encode_ack, decode_ack

R = Record(7, 42, 2**64-1, 65536, 10, 9, -1234, 5678, 1000)


class ProtocolTests(unittest.TestCase):
    def test_roundtrip_boundaries(self):
        self.assertEqual(Record.decode(R.encode()), R)
        self.assertEqual(decode_ack(encode_ack(R.session, R.seq)), (R.session, R.seq))
        a = Reassembler()
        self.assertIsNone(a.accept(fragments(R.encode())[0], 0))
        self.assertIsNone(a.accept(fragments(R.encode())[1], .1))
        self.assertEqual(a.accept(fragments(R.encode())[2], .2), R.encode())

    def test_bad_record(self):
        for raw in [R.encode()[:-1], R.encode()+b'x', b'x'*48]:
            with self.assertRaises(ValueError): Record.decode(raw)
        for offset, value in [(0, 0), (2, 2), (3, 8), (42, 1), (8, 0)]:
            raw = bytearray(R.encode())
            if offset == 8: raw[8:16] = bytes(8)
            else: raw[offset] = value
            raw[44:] = struct.pack('<I', zlib.crc32(raw[:44]))
            with self.subTest(offset=offset), self.assertRaises(ValueError): Record.decode(raw)
        for record in [dataclasses.replace(R, page=0), dataclasses.replace(R, confidence=1001)]:
            with self.assertRaises(ValueError): record.encode()

    def test_loss_order_duplicate_expiry_and_reset(self):
        f = fragments(R.encode())
        for steps in [[(1, 0)], [(0, 0), (2, .1)], [(0, 0), (1, .1), (1, .2)],
                      [(0, 0), (1, 3)], [(0, 2), (1, 1)]]:
            a = Reassembler()
            with self.subTest(steps=steps), self.assertRaises(ValueError):
                for i, stamp in steps: a.accept(f[i], stamp)
            with self.assertRaises(ValueError): a.accept(f[2], 4)
        a = Reassembler()
        a.accept(f[0], 0); a.accept(f[1], .1); a.accept(f[0], .2)
        self.assertIsNone(a.accept(f[1], .3))
        self.assertEqual(a.accept(f[2], .4), R.encode())
        a.accept(f[0], 1); a.reset()
        with self.assertRaises(ValueError): a.accept(f[1], 1.1)

    def test_header_and_seq16(self):
        f = fragments(R.encode())
        for bad in [b'', f[0]+b'x', bytes([0, 0])+f[0][2:], bytes([0xb1,3])+f[0][2:]]:
            with self.assertRaises(ValueError): Reassembler().accept(bad, 0)
        a = Reassembler()
        with self.assertRaises(ValueError):
            for v in f: a.accept(v[:2]+b'\x01\x00'+v[4:], 0)
        a = Reassembler()
        a.accept(f[0], 0)
        with self.assertRaises(ValueError): a.accept(f[1][:2]+b'\x01\x00'+f[1][4:], .1)

    def test_bad_ack(self):
        for raw in [b'', encode_ack(1,0)[:-1], bytes(20)]:
            with self.assertRaises(ValueError): decode_ack(raw)
        for session, seq in [(0,0),(2**64,0),(1,-1),(1,2**32)]:
            with self.assertRaises(ValueError): encode_ack(session,seq)
