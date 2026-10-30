"""Frozen SP v1 wire codec; CRC is corruption detection, NOT authentication."""
from dataclasses import dataclass
import math
import struct
import time
import zlib

SERVICE = "7c3f0001-7ad1-4d6f-963a-72b30000beef"
TX = "7c3f0002-7ad1-4d6f-963a-72b30000beef"
ACK = "7c3f0003-7ad1-4d6f-963a-72b30000beef"
INFO = "7c3f0004-7ad1-4d6f-963a-72b30000beef"
EXPECTED_INFO = b"PEN/1 RECORD48 FRAG3 ACK20 DEV_USB; NO_SENSOR"
BODY = struct.Struct("<2sBBIQIQIiiHH")
CONTACT, VALID, GAP = 1, 2, 4


@dataclass(frozen=True)
class Record:
    flags: int
    device: int
    session: int
    seq: int
    timestamp_us: int
    page: int
    x_um: int
    y_um: int
    confidence: int

    def validate(self):
        for field, lo, hi in (("flags", 0, 7), ("device", 0, 2**32-1),
                              ("session", 1, 2**64-1), ("seq", 0, 2**32-1),
                              ("timestamp_us", 0, 2**64-1), ("page", 0, 2**32-1),
                              ("x_um", -2**31, 2**31-1), ("y_um", -2**31, 2**31-1),
                              ("confidence", 0, 1000)):
            value = getattr(self, field)
            if type(value) is not int or not lo <= value <= hi:
                raise ValueError(f"invalid {field}")
        if self.flags & VALID and not self.page:
            raise ValueError("VALID requires nonzero page")

    def encode(self):
        self.validate()
        body = BODY.pack(b"SP", 1, self.flags, self.device, self.session, self.seq,
                         self.timestamp_us, self.page, self.x_um, self.y_um, self.confidence, 0)
        return body + struct.pack("<I", zlib.crc32(body))

    @classmethod
    def decode(cls, raw):
        if len(raw) != 48:
            raise ValueError("record must be exactly 48 bytes")
        if zlib.crc32(raw[:44]) != struct.unpack("<I", raw[44:])[0]:
            raise ValueError("record CRC mismatch")
        magic, version, flags, device, session, seq, stamp, page, x, y, conf, reserved = BODY.unpack(raw[:44])
        if magic != b"SP" or version != 1 or reserved:
            raise ValueError("record header/version/reserved mismatch")
        record = cls(flags, device, session, seq, stamp, page, x, y, conf)
        record.validate()
        return record


def fragments(raw):
    record = Record.decode(raw)
    return [struct.pack("<BBH", 0xB1, i, record.seq & 65535) + raw[16*i:16*(i+1)]
            for i in range(3)]


class Reassembler:
    """One ordered transfer; fragment 0 always restarts, including same seq16.

    No cached journal identity can replace a missing fragment. Never combine
    partial transfers across disconnects. seq16 alone is not a record identity.
    """
    def __init__(self, timeout=2.0):
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("positive finite timeout required")
        self.timeout = timeout
        self.last_observed = None  # connection lifetime; fragment reset must not erase it
        self.reset()

    def reset(self):
        self.transfer = None
        self.index = 0
        self.data = b""
        self.started = 0.0

    def accept(self, data, now=None):
        now = time.monotonic() if now is None else now
        if not math.isfinite(now) or self.last_observed is not None and now < self.last_observed:
            self.reset()
            raise ValueError("non-finite/backward observation clock")
        self.last_observed = now
        if len(data) != 20 or data[0] != 0xB1 or data[1] > 2:
            self.reset()
            raise ValueError("invalid fragment/time")
        _, index, transfer = struct.unpack("<BBH", data[:4])
        if index == 0:
            self.reset()
            self.transfer, self.started = transfer, now
        if transfer != self.transfer or index != self.index or not 0 <= now-self.started <= self.timeout:
            self.reset()
            raise ValueError("fragment lost/reordered/expired")
        self.data += bytes(data[4:])
        self.index += 1
        if self.index < 3:
            return None
        raw = self.data
        self.reset()
        record = Record.decode(raw)
        if transfer != record.seq & 65535:
            raise ValueError("fragment/record sequence mismatch")
        return raw


def encode_ack(session, seq):
    if type(session) is not int or type(seq) is not int or not 1 <= session < 2**64 or not 0 <= seq < 2**32:
        raise ValueError("ACK range")
    body = struct.pack("<2sBBQI", b"AK", 1, 0, session, seq)
    return body + struct.pack("<I", zlib.crc32(body))


def decode_ack(raw):
    if len(raw) != 20 or zlib.crc32(raw[:16]) != struct.unpack("<I", raw[16:])[0]:
        raise ValueError("ACK length/CRC")
    magic, version, reserved, session, seq = struct.unpack("<2sBBQI", raw[:16])
    if magic != b"AK" or version != 1 or reserved or not session:
        raise ValueError("ACK header")
    return session, seq
