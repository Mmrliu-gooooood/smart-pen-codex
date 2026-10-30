"""Read-only frozen source input; all compiler output goes to a temporary directory."""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pen_receiver.protocol import Record, Reassembler, encode_ack, fragments


def main():
    root=Path(__file__).resolve().parents[1]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ble-source',type=Path,default=root.parent/'smart_pen_ble_transport_candidate_20261029')
    args=parser.parse_args();source=args.ble_source.resolve()
    record=Record(7,42,2**64-1,65536,10,9,-1234,5678,1000)
    includes=[source/'include']+[source/'frozen'/name for name in ['application','runtime','storage','portable','vision','codec']]
    with tempfile.TemporaryDirectory() as tmp:
        binary=Path(tmp)/'crosswire'
        subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-pedantic',
                        *['-I'+str(p) for p in includes],str(root/'tools/crosswire.c'),
                        str(source/'src/pen_ble_core.c'),str(source/'frozen/portable/pen.c'),'-o',str(binary)],check=True)
        output=subprocess.run([str(binary),encode_ack(record.session,record.seq).hex()],check=True,capture_output=True,text=True).stdout.splitlines()
    if bytes.fromhex(output[0])!=record.encode():raise RuntimeError('C/Python record mismatch')
    wire=[bytes.fromhex(x) for x in output[1:4]]
    if wire!=fragments(record.encode()):raise RuntimeError('C/Python fragment mismatch')
    a=Reassembler();decoded=None
    for fragment in wire:decoded=a.accept(fragment)
    if decoded!=record.encode():raise RuntimeError('C notification reassembly failed')
    print('PASS: frozen C encode/three notifications -> real Python reassembly, Python exact ACK -> frozen C offered-ticket receive; no radio')

if __name__=='__main__':main()
