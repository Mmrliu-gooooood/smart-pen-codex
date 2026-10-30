from pathlib import Path
import os,json,re,shutil,subprocess,hashlib,sys
os.environ['XDG_CONFIG_HOME']='/tmp/trans-negative0130'
import pcbnew as p
D=Path(__file__).resolve().parent;N=D/'native';m=json.loads((D/'materialization.json').read_text());plan=json.loads((D/'plan_v2.json').read_text());rows=[]
for tag,typ in [('C201.1_localvia','via'),('U204.4_localvia','via'),('TCA_SENS_local','track')]:
 if tag!=sys.argv[1]:continue
 i=next(i for i,t in enumerate(plan['objects'])if t['tag']==tag and t['type']==typ);u=m['added'][i];out=D/'native_negative'/tag;shutil.copytree(N,out,dirs_exist_ok=True);f=out/'mainboard_revD.kicad_pcb';s=f.read_text();found=[]
 def cut(x):
  q=x.group(0)
  if u in q:found.append(u);return ''
  return q
 s=re.sub(r'\t\((?:segment|via)\n.*?\n\t\)\n',cut,s,flags=re.S)
 if found!=[u]:raise RuntimeError('cut once')
 f.write_text(s);b=p.LoadBoard(str(f));b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
 r=subprocess.run(['kicad-cli','pcb','drc','--format','json','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','-o',str(out/'drc.json'),str(f)],capture_output=True,text=True);(out/'drc.log').write_text(r.stdout+r.stderr);j=json.loads((out/'drc.json').read_text());counts=[len(j[k])for k in['violations','unconnected_items','schematic_parity']]
 if counts[1]<=149 or counts[2]!=0 or r.returncode!=5:raise RuntimeError('negative failed')
 rows.append(dict(tag=tag,removed_uuid=u,counts=counts,exit=r.returncode,sha=hashlib.sha256(f.read_bytes()).hexdigest()))
print(json.dumps(rows,indent=2))
