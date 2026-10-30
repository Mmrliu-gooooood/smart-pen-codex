from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E
O=Path(__file__).resolve().parent;D=O/'mirror/smart_pen_next_20261028/hardware/camera_schmitt_native_0745';R=O.parent/'smart_pen_next_20261028';checks={}
for name in ['verify','physical_native','native_negative','replay_rollback']:
 a=json.loads((O/f'raw/{name}_normal.json').read_text());b=json.loads((O/f'raw/{name}_optimized.json').read_text());checks[name+'_modes_equal']=a==b
 if a!=b:raise RuntimeError(name)
n=json.loads((O/'raw/native_negative_normal.json').read_text());checks['negative_counts']={x['case']:x['actual_DRC_unconnected_parity']for x in n};checks['negative_count']=len(n)
for label in ['base','candidate']:
 d=json.load(open(D/'checks'/label/'drc.json'));checks[label+'_drc']=[len(d[k])for k in ['violations','unconnected_items','schematic_parity']];e=json.load(open(D/'checks'/label/'erc.json'));checks[label+'_erc']=[(v['severity'],v['type'])for s in e['sheets']for v in s['violations']]
rows=json.load(open(O/'raw/frozen_hashes.json'));checks['frozen_unchanged']=all(hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']for x in rows)
if not checks['frozen_unchanged']or len(n)!=14:raise RuntimeError(checks)
x=E.parse(D/'checks/candidate/netlist.xml');checks['source_MPN_candidate']={c.get('ref'):c.find('fields/field[@name="MPN_candidate"]').text for c in x.findall('.//components/comp')if c.get('ref')in ['U205','C209','R202']}
(O/'raw/completion.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2))
