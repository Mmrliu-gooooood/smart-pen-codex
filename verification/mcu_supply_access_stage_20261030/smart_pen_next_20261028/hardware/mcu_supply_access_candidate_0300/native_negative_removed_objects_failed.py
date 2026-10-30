from pathlib import Path
import os,json,shutil,subprocess,hashlib
os.environ.update(XDG_CONFIG_HOME='/tmp/mcu-neg0300/config',XDG_CACHE_HOME='/tmp/mcu-neg0300/cache',XDG_DATA_HOME='/tmp/mcu-neg0300/data')
import pcbnew as p
from finite_copper import build,components
D=Path(__file__).resolve().parent;N=D/'native';m=json.loads((D/'materialization.json').read_text());rows=[]
cases=[('pin2_escape',[0],['U101.2'],False),('pin3_escape',[1],['U101.3'],False),('both_power_vias',[5,8],['U101.2','U101.3','C103.1'],False),('ground_reinforcer_only',[6],['C103.2'],True),('rollback',list(range(9)),[],True)]
for tag,inds,pads,connected in cases:
 out=D/'native_negative'/tag;shutil.copytree(N,out,dirs_exist_ok=True);f=out/'mainboard_revD.kicad_pcb';b=p.LoadBoard(str(f));us={m['added'][i]for i in inds};found=[]
 for t in list(b.GetTracks()):
  if t.m_Uuid.AsString()in us:found.append(t.m_Uuid.AsString());b.Remove(t)
 if set(found)!=us:raise RuntimeError('cut once')
 if tag=='rollback':
  fps={f.GetReference():f for f in b.GetFootprints()};fps['C103'].SetPosition(p.VECTOR2I(1200000,7025000));fps['R503'].SetPosition(p.VECTOR2I(2500000,7500000))
 b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
 r=subprocess.run(['kicad-cli','pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','-o',str(out/'drc.json'),str(f)],capture_output=True,text=True);(out/'drc.log').write_text(r.stdout+r.stderr);j=json.loads((out/'drc.json').read_text());counts=[len(j[k])for k in['violations','unconnected_items','schematic_parity']]
 net='GND'if tag=='ground_reinforcer_only'else'3V3_AON';st='J106.3'if net=='GND'else'J106.2';cs=components(build(b)[net]);core=next(c for c in cs if st in c)
 if counts[0]!=0 or counts[2]!=0 or r.returncode!=5:raise RuntimeError('native negative DRC')
 if any((x in core)!=connected for x in pads):raise RuntimeError('native negative connectivity')
 if tag=='rollback' and counts!=[0,137,0]:raise RuntimeError('rollback counts')
 if not connected and counts[1]<=134:raise RuntimeError('negative count not increased')
 rows.append(dict(tag=tag,removed_uuid=sorted(us),counts=counts,exit=r.returncode,pads=pads,connected_to_core=connected,sha=hashlib.sha256(f.read_bytes()).hexdigest()))
print(json.dumps(rows,indent=2))
