from pathlib import Path
import os,shutil,json,hashlib,uuid
os.environ['XDG_CONFIG_HOME']='/tmp/pen-aon2156';os.environ['XDG_CACHE_HOME']='/tmp/pen-aon2156-cache';os.environ['XDG_DATA_HOME']='/tmp/pen-aon2156-data'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];B=R/'hardware/power_zone_freshfill_candidate_2150/native';N=D/'native';shutil.copytree(B,N,dirs_exist_ok=True);f=N/'mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f))
t=p.PCB_TRACK(b);t.SetNetCode(b.FindNet('3V3_AON').GetNetCode());t.SetLayer(p.In2_Cu);t.SetWidth(500000);t.SetStart(p.VECTOR2I(11900000,83900000));t.SetEnd(p.VECTOR2I(11000000,83900000));b.Add(t);generated=t.m_Uuid.AsString();wanted=str(uuid.uuid5(uuid.NAMESPACE_URL,'smart-pen/aon-entry-2156'))
p.SaveBoard(str(f),b);s=f.read_text();
if s.count(generated)!=1:raise RuntimeError('UUID')
f.write_text(s.replace(generated,wanted));b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b);first=f.read_bytes();b=p.LoadBoard(str(f));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
if f.read_bytes()!=first:raise RuntimeError('refill nondeterministic')
print(json.dumps(dict(base_sha=hashlib.sha256((B/f.name).read_bytes()).hexdigest(),pcb_sha=hashlib.sha256(f.read_bytes()).hexdigest(),added_uuid=wanted,net='3V3_AON',layer='In2.Cu',start_mm=[11.9,83.9],end_mm=[11,83.9],width_mm=.5,via_unchanged=True,zone_boundaries_unchanged=True,reload_refill_same=True),indent=2))
