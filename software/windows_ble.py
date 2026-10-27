"""Explicit SYNTHETIC BENCH receiver. Never auto-connect arbitrary discovered pens."""
import argparse
import asyncio
import json
from pen_bridge import Journal,Packet
from ble_transport import TX,ACK,INFO,Reassembler,encode_ack

async def receive(address, device, db, allow_synthetic=False, client_factory=None):
    if not allow_synthetic:raise ValueError('test UUIDs require explicit --allow-synthetic-bench')
    if client_factory is None:
        from bleak import BleakClient
        client_factory=BleakClient
    queue=asyncio.Queue(maxsize=96)
    disconnected=asyncio.Event();overflow=asyncio.Event()
    def on_data(_,data):
        try:queue.put_nowait(bytes(data))
        except asyncio.QueueFull:overflow.set()
    def on_disconnect(_):disconnected.set()
    reassembly=Reassembler()
    async with client_factory(address,pair=True,timeout=60,disconnected_callback=on_disconnect) as client:
        info=bytes(await client.read_gatt_char(INFO))
        if b'SYNTHETIC' not in info:raise ValueError('expected explicitly synthetic bench INFO')
        with Journal(db) as journal:
            await client.start_notify(TX,on_data)
            try:
                while not disconnected.is_set():
                    if overflow.is_set():raise RuntimeError('notification overflow; reconnect/replay required')
                    try:data=await asyncio.wait_for(queue.get(),timeout=0.5)
                    except asyncio.TimeoutError:continue
                    try:raw=reassembly.accept(data)
                    except ValueError:
                        # No ACK; stop-and-wait device must retransmit same record.
                        continue
                    if raw is None:continue
                    p=Packet.decode(raw)
                    if p.device!=device:raise ValueError('unapproved device identity')
                    through=journal.accept(raw) # durable FULL commit precedes ACK
                    if through is not None:
                        await client.write_gatt_char(ACK,encode_ack(p.session,through),response=True)
                    print(json.dumps({'synthetic_bench':True,'session':str(p.session),'through_seq':through}),flush=True)
            finally:
                reassembly.reset()
                if client.is_connected:await client.stop_notify(TX)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--address',required=True);p.add_argument('--device',type=int,required=True)
    p.add_argument('--db',required=True);p.add_argument('--allow-synthetic-bench',action='store_true')
    a=p.parse_args();asyncio.run(receive(a.address,a.device,a.db,a.allow_synthetic_bench))
if __name__=='__main__':main()
