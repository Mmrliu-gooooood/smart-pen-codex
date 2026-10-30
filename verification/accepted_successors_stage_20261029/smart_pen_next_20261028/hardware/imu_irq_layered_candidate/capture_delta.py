from pathlib import Path
import os,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config';os.environ['XDG_CACHE_HOME']='/tmp/rf-independent/cache'
import pcbnew as p
D=Path(__file__).resolve().parent;a=p.LoadBoard(str(D.parent/'j107_mode_port_closure/native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'))
def tg(t):return[t.GetClass(),t.GetNetname(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetLayer(),t.GetWidth(p.F_Cu)if isinstance(t,p.PCB_VIA)else t.GetWidth(),t.GetDrillValue()if isinstance(t,p.PCB_VIA)else None]
aa={t.m_Uuid.AsString():tg(t)for t in a.GetTracks()};bb={t.m_Uuid.AsString():tg(t)for t in b.GetTracks()};r={'base_sha256':hashlib.sha256((D.parent/'j107_mode_port_closure/native/mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256((D/'native/mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'removed':{u:aa[u]for u in sorted(aa.keys()-bb.keys())},'modified':{u:{'before':aa[u],'after':bb[u]}for u in sorted(aa.keys()&bb.keys())if aa[u]!=bb[u]},'added':{u:bb[u]for u in sorted(bb.keys()-aa.keys())},'changed_rule_uuid':'2a715b0e-d7bf-49ab-b132-f7f180326c33','added_rule_uuid':'c59d76d7-4fe7-4475-8382-e1c75d7f8d6c'};(D/'routing_delta.json').write_text(json.dumps(r,indent=2))
