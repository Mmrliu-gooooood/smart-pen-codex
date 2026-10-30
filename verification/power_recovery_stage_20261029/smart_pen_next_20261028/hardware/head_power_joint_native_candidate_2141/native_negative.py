from pathlib import Path
import os,json,shutil,subprocess,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/pen-joint2141-negative';os.environ['XDG_CACHE_HOME']='/tmp/pen-joint2141-cache';os.environ['XDG_DATA_HOME']='/tmp/pen-joint2141-data'
D=Path(__file__).resolve().parent;N=D/'native';v=json.loads((D/'verify_normal.json').read_text());out=[]
for case in v['fourteen_single_object_negatives']:
 net=case['net'];w=Path('/tmp/pen-joint2141-negatives')/net
 if w.exists():raise RuntimeError('REFUSE OVERWRITE')
 shutil.copytree(N,w,ignore=shutil.ignore_patterns('*.kicad_prl'));target=case['removed_uuid'];file=w/'mainboard_revD.kicad_pcb';lines=file.read_text().splitlines(keepends=True);blocks=[];i=0;removed=0
 while i<len(lines):
  if lines[i].startswith('\t(segment\n')or lines[i].startswith('\t(via\n')or lines[i].startswith('\t(arc\n'):
   j=i+1
   while j<len(lines)and lines[j]!='\t)\n':j+=1
   block=''.join(lines[i:j+1])
   if target in block:removed+=1
   else:blocks.append(block)
   i=j+1
  else:blocks.append(lines[i]);i+=1
 if removed!=1:raise RuntimeError('EXACT REMOVAL')
 file.write_text(''.join(blocks));report=D/('negative_'+net+'.json');cmd=['kicad-cli','pcb','drc','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','--format','json','-o',str(report),str(file)];q=subprocess.run(cmd,capture_output=True,text=True);(D/('negative_'+net+'.log')).write_text(q.stdout+q.stderr)
 if q.returncode!=5:raise RuntimeError('CLI expected nonpassing')
 r=json.loads(report.read_text());found=[x for x in r['unconnected_items']if any('['+net+']'in i['description']for i in x['items'])]
 if not found or len(r['unconnected_items'])<=232:raise RuntimeError('NATIVE OPEN NOT FOUND '+net)
 out.append(dict(net=net,removed_uuid=target,strict_drc=[len(r[x])for x in ['violations','unconnected_items','schematic_parity']],exit_code=q.returncode,matching_unconnected_findings=found))
if hashlib.sha256((N/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest()!=v['pcb_sha']:raise RuntimeError('FINAL MUTATED')
print(json.dumps({'status':'FOURTEEN_REAL_NATIVE_SINGLE_DELETIONS_REJECTED','cases':out,'original_unchanged':True},indent=2))
