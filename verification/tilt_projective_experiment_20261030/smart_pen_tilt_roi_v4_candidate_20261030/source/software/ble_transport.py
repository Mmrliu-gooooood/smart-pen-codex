"""Test-only BLE framing; actual radio requires explicit approved paired peer."""
import struct
import time
import zlib
from pen_bridge import Packet
SERVICE='7c3f0001-7ad1-4d6f-963a-72b30000beef'
TX=SERVICE.replace('0001-','0002-',1)
ACK=SERVICE.replace('0001-','0003-',1)
INFO=SERVICE.replace('0001-','0004-',1)

def fragment(raw, transfer):
    Packet.decode(raw)
    if not 0 <= transfer <= 65535: raise ValueError('transfer ID')
    return [struct.pack('<BBH',0xB1,i,transfer)+raw[i*16:(i+1)*16] for i in range(3)]

class Reassembler:
    def __init__(self, timeout=2.0):
        self.timeout=timeout
        self.reset()
    def reset(self):
        self.transfer=None;self.index=0;self.data=b'';self.started=0
    def accept(self, data, now=None):
        now=time.monotonic() if now is None else now
        if len(data)!=20 or data[0]!=0xB1 or data[1]>2:
            self.reset();raise ValueError('invalid BLE fragment')
        _,index,transfer=struct.unpack('<BBH',data[:4])
        if index==0:
            self.reset();self.transfer=transfer;self.started=now
        if transfer!=self.transfer or index!=self.index or not 0<=now-self.started<=self.timeout:
            self.reset();raise ValueError('BLE fragment lost/reordered/expired')
        self.data+=bytes(data[4:]);self.index+=1
        if self.index!=3:return None
        raw=self.data;self.reset();packet=Packet.decode(raw)
        if transfer!=packet.seq&65535:raise ValueError('transfer/packet sequence mismatch')
        return raw

def encode_ack(session,seq):
    if not 1<=session<2**64 or not 0<=seq<2**32:raise ValueError('ACK range')
    body=struct.pack('<2sBBQI',b'AK',1,0,session,seq)
    return body+struct.pack('<I',zlib.crc32(body))

def decode_ack(raw):
    if len(raw)!=20 or zlib.crc32(raw[:16])!=struct.unpack('<I',raw[16:])[0]:raise ValueError('ACK CRC')
    magic,version,reserved,session,seq=struct.unpack('<2sBBQI',raw[:16])
    if magic!=b'AK' or version!=1 or reserved or not session:raise ValueError('ACK header')
    return session,seq
