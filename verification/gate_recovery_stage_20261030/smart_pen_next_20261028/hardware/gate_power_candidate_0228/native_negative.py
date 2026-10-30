from pathlib import Path
import os,json,re,shutil,subprocess,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/gate-neg0228';os.environ['XDG_CACHE_HOME']='/tmp/gate-cache0228'
import pcbnew as p
from finite_copper import build,components
D=Path(__file__).resolve().parent;N=D/'native';m=json.loads((D/'materialization.json').read_text());rows=[]
for tag,inds,net,st,pads in [('AON',[0,1],'3V3_AON','J106.2',['U301.1','C301.1']),('switch_ground',[3],'GND','J106.3',['U301.2']),('outputcap_ground',[4],'GND','J106.3',['C302.2']),('timingcap_ground',[5],'GND','J106.3',['C303.2']),('pulldown_ground',[6],'GND','J106.3',['R301.2'])]:
 us={m['added'][i]for i in inds};out=D/'native_negative'/tag;shutil.copytree(N,out,dirs_exist_ok=True);f=out/'mainboard_revD.kicad_pcb';s=f.read_text();found=[]
 def cut(x):
  q=x.group(0)
  for u in us:
   if u in q:found.append(u);return ''
  return q
 s=re.sub(r'\t\((?:segment|via)\n.*?\n\t\)\n',cut,s,flags=re.S)
 if set(found)!=us or len(found)!=len(us):raise RuntimeError('cut once')
 f.write_text(s);b=p.LoadBoard(str(f));b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
 r=subprocess.run(['kicad-cli','pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','-o',str(out/'drc.json'),str(f)],capture_output=True,text=True);(out/'drc.log').write_text(r.stdout+r.stderr);j=json.loads((out/'drc.json').read_text());counts=[len(j[k])for k in['violations','unconnected_items','schematic_parity']]
 cs=components(build(b)[net]);core=next(c for c in cs if st in c)
 if counts[1]<=137 or counts[2]!=0 or r.returncode!=5 or any(x in core for x in pads):raise RuntimeError('negative failed')
 rows.append(dict(tag=tag,removed_uuid=sorted(us),counts=counts,exit=r.returncode,disconnected_from_core=pads,sha=hashlib.sha256(f.read_bytes()).hexdigest()))
print(json.dumps(rows,indent=2))
