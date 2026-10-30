from pathlib import Path
import os,json,tempfile,shutil,re,subprocess,hashlib
os.environ.update(XDG_CONFIG_HOME='/tmp/restore-review2020-config',XDG_CACHE_HOME='/tmp/restore-review2020-cache',XDG_DATA_HOME='/tmp/restore-review2020-data')
D=Path(__file__).resolve().parent;v=json.loads((D/'verify_normal.json').read_text());out=[]
for n in ['RF_ANT','USB_DM_MCU','CAM_QOD']:
 u=next(x['removed_uuid']for x in v['nineteen_single_object_removal_negatives']if x['net']==n)
 with tempfile.TemporaryDirectory(prefix='restore2020negative-',dir='/tmp')as td:
  d=Path(td)/'native';shutil.copytree(D/'native',d);f=d/'mainboard_revD.kicad_pcb';raw=f.read_text();found=[]
  def filt(m):
   if u in m[0]:found.append(m[0]);return ''
   return m[0]
  raw=re.sub(r'\n\t\((?:segment|via|arc)\n.*?\n\t\)',filt,raw,flags=re.S)
  if len(found)!=1:raise RuntimeError('REMOVE_EXACTLY_ONE')
  f.write_text(raw);report=D/('negative_independent_'+n+'.json');cmd=['/usr/bin/kicad-cli','pcb','drc','--all-track-errors','--severity-all','--schematic-parity','--exit-code-violations','--format','json','-o',str(report),str(f)];q=subprocess.run(cmd,capture_output=True,text=True);(D/('negative_independent_'+n+'.log')).write_text(q.stdout+q.stderr);r=json.loads(report.read_text());hits=[x for x in r['unconnected_items']if any('['+n+']'in x['description']for x in x['items'])]
  if q.returncode!=5 or len(r['unconnected_items'])!=234 or not hits:raise RuntimeError('NOT_DETECTED '+n)
  out.append({'net':n,'removed_uuid':u,'exit':q.returncode,'counts':[len(r[k])for k in ['violations','unconnected_items','schematic_parity']],'new_net_airwire':hits})
(D/'native_negative_independent_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
