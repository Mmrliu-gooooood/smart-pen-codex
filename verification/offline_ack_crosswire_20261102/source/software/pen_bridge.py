"""Portable SP v1 receiver; no BLE driver or vision decoder is implied."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
import struct
import sys
import zlib

BODY = struct.Struct('<2sBBIQIQIiiHH')
SIZE = 48


@dataclass(frozen=True)
class Packet:
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
        bounds = {'flags': (0,7), 'device': (0,2**32-1),
                  'session': (1,2**64-1), 'seq': (0,2**32-1),
                  'timestamp_us': (0,2**64-1), 'page': (0,2**32-1),
                  'x_um': (-2**31,2**31-1), 'y_um': (-2**31,2**31-1),
                  'confidence': (0,1000)}
        for name,(lo,hi) in bounds.items():
            value=getattr(self,name)
            if type(value) is not int or not lo <= value <= hi:
                raise ValueError(f'invalid {name}')
        if self.flags & 2 and self.page == 0:
            raise ValueError('valid coordinate requires assigned page')

    def encode(self) -> bytes:
        self.validate()
        body=BODY.pack(b'SP',1,self.flags,self.device,self.session,self.seq,
                       self.timestamp_us,self.page,self.x_um,self.y_um,self.confidence,0)
        return body+struct.pack('<I',zlib.crc32(body))

    @classmethod
    def decode(cls, raw: bytes) -> Packet:
        if len(raw)!=SIZE: raise ValueError('packet must be exactly 48 bytes')
        if zlib.crc32(raw[:44]) != struct.unpack('<I',raw[44:])[0]:
            raise ValueError('CRC mismatch')
        magic,version,flags,device,session,seq,stamp,page,x,y,conf,reserved=BODY.unpack(raw[:44])
        if magic!=b'SP' or version!=1 or reserved!=0:
            raise ValueError('unsupported header or reserved bits')
        packet=cls(flags,device,session,seq,stamp,page,x,y,conf)
        packet.validate()
        return packet


class Journal:
    """ACK is cumulative per device/session, ONLY after SQLite FULL commit.

    SQLite/OS storage must honor fsync. This is not proof of physical flash
    durability. Host restart can derive ACK from stored rows; no in-memory ACK.
    Session is text because the wire permits unsigned 64-bit identifiers.
    """
    def __init__(self, path: str | Path):
        self.db=sqlite3.connect(path)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('''CREATE TABLE IF NOT EXISTS packets (
            device INTEGER NOT NULL, session TEXT NOT NULL, seq INTEGER NOT NULL,
            raw BLOB NOT NULL, PRIMARY KEY(device,session,seq))''')
        self.db.execute('''CREATE TABLE IF NOT EXISTS frontiers (
            device INTEGER NOT NULL, session TEXT NOT NULL, through_seq INTEGER NOT NULL,
            PRIMARY KEY(device,session))''')
        self.db.commit()

    def __enter__(self): return self
    def __exit__(self,*exc): self.db.close()

    def accept(self, raw: bytes) -> int | None:
        packet=Packet.decode(raw)
        key=(packet.device,str(packet.session),packet.seq)
        try:
            self.db.execute('BEGIN IMMEDIATE')
            existing=self.db.execute('SELECT raw FROM packets WHERE device=? AND session=? AND seq=?',key).fetchone()
            if existing and bytes(existing[0])!=bytes(raw):
                raise ValueError('conflicting duplicate: session reuse or corrupted sender')
            if not existing:
                self.db.execute('INSERT INTO packets VALUES(?,?,?,?)',(*key,bytes(raw)))
            old=self.db.execute('SELECT through_seq FROM frontiers WHERE device=? AND session=?',key[:2]).fetchone()
            next_seq=old[0]+1 if old else 0
            for (seq,) in self.db.execute('SELECT seq FROM packets WHERE device=? AND session=? AND seq>=? ORDER BY seq',(*key[:2],next_seq)):
                if seq!=next_seq: break
                next_seq+=1
            self.db.execute('INSERT OR REPLACE INTO frontiers VALUES(?,?,?)',(*key[:2],next_seq-1))
            self.db.commit()
        except BaseException:
            self.db.rollback()
            raise
        return self.ack(packet.device,packet.session)

    def ack(self,device:int,session:int) -> int | None:
        row=self.db.execute('SELECT through_seq FROM frontiers WHERE device=? AND session=?',(device,str(session))).fetchone()
        return row[0] if row and row[0]>=0 else None

    def replay(self,device:int,session:int):
        for (raw,) in self.db.execute('SELECT raw FROM packets WHERE device=? AND session=? ORDER BY seq',(device,str(session))):
            yield Packet.decode(raw)


def stroke_events(packets, min_confidence=750, max_gap_us=100000):
    """Safe point stream: never interpolate; every discontinuity ends a stroke.

    Coordinates are millimetres, paper +x right/+y up. App adapters must convert
    axes explicitly. A start point after a loss is not connected to old ink.
    """
    if not 0<=min_confidence<=1000 or max_gap_us<=0: raise ValueError('invalid gating')
    previous=None
    active=None
    stroke=0
    for p in packets:
        p.validate()
        eligible=p.flags & 3 == 3 and p.confidence>=min_confidence
        continuous=(previous is not None and eligible and active is not None
                    and not p.flags & 4
                    and (p.device,p.session,p.page)==(previous.device,previous.session,previous.page)
                    and p.seq==previous.seq+1
                    and 0<p.timestamp_us-previous.timestamp_us<=max_gap_us)
        if active is not None and not continuous:
            yield {'type':'end','stroke':active,'reason':'boundary'}
            active=None
        if eligible:
            if active is None:
                stroke+=1; active=stroke
                yield {'type':'start','stroke':active,'device':p.device,
                       'session':str(p.session),'page':p.page}
            yield {'type':'point','stroke':active,'seq':p.seq,'timestamp_us':p.timestamp_us,
                   'x_mm':p.x_um/1000,'y_mm':p.y_um/1000,'confidence':p.confidence/1000}
        previous=p
    if active is not None: yield {'type':'end','stroke':active,'reason':'end_of_replay'}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',required=True)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('ingest',help='fixed 48-byte records on stdin; durable JSON ACK on stdout')
    replay=sub.add_parser('replay',help='ordered journal -> JSONL stroke events')
    replay.add_argument('--device',type=int,required=True)
    replay.add_argument('--session',type=int,required=True)
    args=parser.parse_args(argv)
    with Journal(args.db) as journal:
        if args.command=='ingest':
            while True:
                raw=sys.stdin.buffer.read(SIZE)
                if not raw: break
                # Fail closed; do not silently resynchronize to potentially bogus frames.
                packet=Packet.decode(raw)
                ack=journal.accept(raw)
                print(json.dumps({'type':'durable_ack','device':packet.device,
                                  'session':str(packet.session),'through_seq':ack}),flush=True)
        else:
            for event in stroke_events(journal.replay(args.device,args.session)):
                print(json.dumps(event))

if __name__=='__main__': main()
