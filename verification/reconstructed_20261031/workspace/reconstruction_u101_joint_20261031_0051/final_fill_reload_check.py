from pathlib import Path
import os,hashlib,json,tempfile
os.environ.update(XDG_CONFIG_HOME='/tmp/newreconstruct/config',XDG_CACHE_HOME='/tmp/newreconstruct/cache',XDG_DATA_HOME='/tmp/newreconstruct/data')
import pcbnew as p
D=Path(__file__).resolve().parent;f=D/'data8_review_native/mainboard_revD.kicad_pcb';before=f.read_bytes();b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());tmp=D/'final_validation/refill_replay.kicad_pcb';p.SaveBoard(str(tmp),b);same=before==tmp.read_bytes();r={'sha256':hashlib.sha256(before).hexdigest(),'native_refill_reload_bytes_equal':same,'source_untouched':f.read_bytes()==before};(D/'final_fill_reload.json').write_text(json.dumps(r,indent=2));print(r)
if not all([same,r['source_untouched']]):raise RuntimeError('refill not stable')
