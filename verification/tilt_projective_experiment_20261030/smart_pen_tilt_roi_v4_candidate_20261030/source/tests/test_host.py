import struct
import zlib
import sqlite3
import tempfile
import unittest
from pathlib import Path
from software.pen_bridge import Packet, Journal, stroke_events


def p(seq=0, **kw):
    values = dict(flags=3, device=1, session=2**64-1, seq=seq,
                  timestamp_us=seq*10000, page=1, x_um=100, y_um=200, confidence=900)
    values.update(kw)
    return Packet(**values)


class HostTests(unittest.TestCase):
    def test_roundtrip_and_crc(self):
        raw = p().encode()
        self.assertEqual(len(raw), 48)
        self.assertEqual(Packet.decode(raw), p())
        for offset in range(48):
            corrupt = bytearray(raw); corrupt[offset] ^= 1
            with self.assertRaises(ValueError): Packet.decode(corrupt)
        with self.assertRaises(ValueError): Packet.decode(raw[:-1])

    def test_reserved_fields_with_valid_crc(self):
        for offset,value in [(2,2),(3,8),(42,1)]:
            raw=bytearray(p().encode()); raw[offset]=value
            raw[44:]=struct.pack("<I",zlib.crc32(raw[:44]))
            with self.assertRaises(ValueError): Packet.decode(raw)

    def test_semantics(self):
        for changes in [dict(flags=8),dict(session=0),dict(page=0),dict(confidence=1001),dict(seq=-1)]:
            with self.assertRaises(ValueError): p(**changes).encode()
        self.assertEqual(Packet.decode(p(flags=0,page=0).encode()).page,0)

    def test_durable_contiguous_reconnect(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'pen.sqlite'
            with Journal(path) as j:
                self.assertIsNone(j.accept(p(2).encode()))
                self.assertEqual(j.accept(p(0).encode()), 0)
                with sqlite3.connect(path) as observer:
                    self.assertEqual(observer.execute("SELECT through_seq FROM frontiers").fetchone()[0],0)
                    self.assertEqual(observer.execute("SELECT COUNT(*) FROM packets").fetchone()[0],2)
                self.assertEqual(j.accept(p(0).encode()), 0)
                with self.assertRaises(ValueError): j.accept(p(0,x_um=999).encode())
            with Journal(path) as j:
                self.assertEqual(j.accept(p(1).encode()), 2)
                self.assertEqual([q.seq for q in j.replay(1,2**64-1)], [0,1,2])
                self.assertEqual(j.accept(p(0,session=9).encode()), 0)
                self.assertEqual(len(list(j.replay(1,2**64-1))),3)

    def test_commit_failure_has_no_ack_or_row(self):
        with tempfile.TemporaryDirectory() as d:
            with Journal(Path(d)/'pen.sqlite') as j:
                j.db.execute('PRAGMA query_only=ON')
                with self.assertRaises(sqlite3.OperationalError): j.accept(p().encode())
                self.assertEqual(list(j.replay(1,2**64-1)), [])

    def test_safe_boundaries(self):
        cases = [p(2),p(1,page=2),p(1,session=3),p(1,flags=7),
                 p(1,timestamp_us=200001),p(1,timestamp_us=0),p(1,confidence=100)]
        for other in cases:
            events=list(stroke_events([p(0,timestamp_us=1000),other]))
            points=[e for e in events if e['type']=='point']
            if len(points)>1: self.assertNotEqual(points[0]['stroke'], points[1]['stroke'])
            self.assertEqual(events[-1]['type'],'end')
        for flags in [0,1,2]:
            events=list(stroke_events([p(),p(1,flags=flags),p(2)]))
            points=[e for e in events if e['type']=='point']
            self.assertEqual(len(points),2)
            self.assertNotEqual(points[0]['stroke'], points[1]['stroke'])

    def test_sequence_rollover_and_clock_reset_are_boundaries(self):
        for pair in [
            [p(2**32-1,timestamp_us=100),p(0,timestamp_us=101)],
            [p(10,timestamp_us=100),p(11,timestamp_us=1)],
            [p(10,timestamp_us=100),p(11,timestamp_us=100)],
        ]:
            points=[e for e in stroke_events(pair) if e['type']=='point']
            self.assertEqual(len(points),2)
            self.assertNotEqual(points[0]['stroke'],points[1]['stroke'])

    def test_continuity_and_duplicate(self):
        events=list(stroke_events([p(),p(1),p(1),p(2)]))
        points=[e for e in events if e['type']=='point']
        self.assertEqual(points[0]['stroke'],points[1]['stroke'])
        self.assertNotEqual(points[1]['stroke'],points[2]['stroke'])

if __name__ == '__main__': unittest.main()
