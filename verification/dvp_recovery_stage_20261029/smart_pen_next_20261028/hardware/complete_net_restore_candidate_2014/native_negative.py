from pathlib import Path
import os,json,shutil,subprocess,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/pen-restore2014-config';os.environ['XDG_CACHE_HOME']='/tmp/pen-native1950-cache';os.environ['XDG_DATA_HOME']='/tmp/pen-native1950-data'

D=Path(__file__).resolve().parent;N=D/'native';v=json.loads((D/'verify_normal.json').read_text());out=[]
for net in ['USB_DP','CAM_ON','CAM_3V3_PRELINK']:
 w=Path('/tmp/pen-restore2014-negative-v2')/net
 if w.exists():raise RuntimeError('REFUSE OVERWRITE')
 shutil.copytree(N,w,ignore=shutil.ignore_patterns('*.kicad_prl'));target=next(x['removed_uuid']for x in v['nineteen_single_object_removal_negatives']if x['net']==net)
 file=w/'mainboard_revD.kicad_pcb';lines=file.read_text().splitlines(keepends=True);blocks=[];i=0;removed=0
 while i<len(lines):
  if lines[i].startswith('\t(segment\n')or lines[i].startswith('\t(via\n')or lines[i].startswith('\t(arc\n'):
   j=i+1
   while j<len(lines)and lines[j]!='\t)\n':j+=1
   block=''.join(lines[i:j+1])
   if target in block:removed+=1
   else:blocks.append(block)
   i=j+1
  else:blocks.append(lines[i]);i+=1
 if removed!=1:raise RuntimeError('EXACT OBJECT NOT FOUND')
 file.write_text(''.join(blocks))
 cmd=['kicad-cli','pcb','drc','--all-track-errors','--format','json','--schematic-parity','-o',str(D/('negative_'+net+'.json')),str(w/'mainboard_revD.kicad_pcb')]
 q=subprocess.run(cmd,capture_output=True,text=True);(D/('negative_'+net+'.log')).write_text(q.stdout+q.stderr)
 if q.returncode:raise RuntimeError('CLI FAILURE')
 r=json.loads((D/('negative_'+net+'.json')).read_text());found=[x for x in r['unconnected_items']if any('['+net+']'in i['description']for i in x['items'])]
 if not found or len(r['unconnected_items'])<=233:raise RuntimeError('NATIVE OPEN NOT FOUND '+net)
 out.append({'net':net,'removed_uuid':target,'strict_drc':[len(r['violations']),len(r['unconnected_items']),len(r['schematic_parity'])],'matching_unconnected_findings':found})
if hashlib.sha256((N/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest()!=v['pcb_sha256']:raise RuntimeError('FROZEN INPUT CHANGED')
print(json.dumps({'status':'THREE_NATIVE_REMOVAL_CASES_REJECTED','cases':out,'final_native_unchanged':True},indent=2))
