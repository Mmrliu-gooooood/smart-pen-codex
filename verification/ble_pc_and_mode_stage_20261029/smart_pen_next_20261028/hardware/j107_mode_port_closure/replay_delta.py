from pathlib import Path
import os,json,re,hashlib,shutil
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache';os.environ['XDG_DATA_HOME']='/tmp/rf-independent/data'
import pcbnew as p
D=Path(__file__).resolve().parent;S=D.parent/'gate_cam_on_path_maintenance/native/mainboard_revD.kicad_pcb';C=D/'native/mainboard_revD.kicad_pcb';delta=json.loads((D/'j107_delta.json').read_text())
if hashlib.sha256(S.read_bytes()).hexdigest()!=delta['input_pcb_sha256']or hashlib.sha256(C.read_bytes()).hexdigest()!=delta['candidate_pcb_sha256']:raise RuntimeError('Replay dependency hash mismatch')
removed={r['uuid']for r in delta['removed']};added={r['uuid']for r in delta['added']};blocks=[]
for block in re.findall(r'\n\t\((?:segment|via)\n.*?\n\t\)',C.read_text(),re.S):
 if any(u in block for u in added):blocks.append(block)
if len(blocks)!=len(added):raise RuntimeError('Exact added native block missing')
raw=re.sub(r'\n\t\((?:segment|via)\n.*?\n\t\)',lambda m:''if any(u in m[0]for u in removed)else m[0],S.read_text(),flags=re.S);i=raw.rfind(')');raw=raw[:i]+''.join(blocks)+'\n'+raw[i:]
O=D/'guard_boards/replay_native';shutil.copytree(D/'native',O,dirs_exist_ok=True);f=O/'mainboard_revD.kicad_pcb';f.write_text(raw);b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
print(json.dumps({'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(C.read_bytes()).hexdigest(),'replayed_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'method':'Remove exactly3 obsolete GND conductors, insert7 exact native J107 track/via blocks; preserve all other source/copper then fresh fill. Run verify_j107.py on this file; serialization order is not geometry proof.'},indent=2))
