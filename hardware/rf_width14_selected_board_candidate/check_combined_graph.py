from pathlib import Path
import sys,json,hashlib,pcbnew as p
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D/'tools'));from physical_graph import graph
b=p.LoadBoard(str(D/'mainboard_revD.kicad_pcb'));g=graph(b);bad=[x for x in g if len(x['components'])!=1]
if bad:raise RuntimeError('Unconnected pad partitions: '+str(bad))
r={'status':'ALL_PRESENT_NATIVE_PADS_CONNECTED_NOT_ALL_SYSTEM_COMPONENTS_PLACED','pcb_sha256':hashlib.sha256((D/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'nets':g};print(json.dumps(r,indent=2))
