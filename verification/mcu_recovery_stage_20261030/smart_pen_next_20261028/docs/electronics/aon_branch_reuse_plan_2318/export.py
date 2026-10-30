from pathlib import Path
import csv,json,re,hashlib
D=Path(__file__).resolve().parent;R=D.parents[2];e=json.loads((D/'evaluation.json').read_text());a=json.loads((R/'hardware/gnd_conservative_recovery_2305/analysis.json').read_text());src=R/'hardware/gnd_conservative_recovery_2305/native/schematic/MCU.kicad_sym'
tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',src.read_text());stack=[];root=None
for t in tokens:
 if t=='(':stack.append([])
 elif t==')':
  q=stack.pop()
  if stack:stack[-1].append(q)
  else:root=q
 else:stack[-1].append(json.loads(t)if t.startswith('"')else t)
symbol=next(x for x in root if isinstance(x,list)and x[:2]==['symbol','ESP32-S3-PICO-1-N8R8']);pins={}
def walk(x):
 if not isinstance(x,list):return
 if x and x[0]=='pin':
  d={z[0]:z[1]for z in x if isinstance(z,list)and len(z)>1};pins[d['number']]=d['name']
 for z in x:walk(z)
walk(symbol)
roles={k:pins[k]for k in ['2','3','20','46','55','56']}
returns=[]
for ref in ['U101','C104','C105','C102','C207']:
 pads=[x for x in a['pads']if x['net']=='GND'and x['pad'].startswith(ref+'.')]
 returns.append(dict(ref=ref,current_GND_physical_pads=len(pads),current_GND_core_connected=sum(x['connected_to_core']for x in pads),pads=[dict(pad=x['pad'],connected=x['connected_to_core'])for x in pads]))
(D/'role_and_return_limits.json').write_text(json.dumps(dict(source=str(src.relative_to(R)),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),U101_pin_functions_from_frozen_symbol=roles,actual_return_status=returns,note='Restoring a supply branch does not power or qualify an entire device when other supply/ground pins remain open.'),indent=2)+'\n')
with(D/'proposed_groups.csv').open('w')as f:
 w=csv.writer(f);w.writerow(['old_group_id','pads','objects','min_track_width_mm','max_track_width_mm','via_count','via_diameter_drill_mm','hypothetical_core_reach','qualifications'])
 for g in e['geometrically_screened_groups']:
  if not g['proposed_for_bounded_native_trial']:continue
  widths=[x['width_mm']for x in g['geometry']if x['type']=='track'];vs=[x for x in g['geometry']if x['type']=='via']
  w.writerow([g['id'],';'.join(g['pads']),len(g['objects']),min(widths),max(widths),len(vs),';'.join(f"{x['width_mm']}/{x['drill_mm']}"for x in vs),True,'NOFAB; native full DRC/freshfill/return/current not verified'])
print(json.dumps({'selected_groups':e['proposed_group_ids'],'U101_pin_roles':roles,'return_summary':[(x['ref'],x['current_GND_core_connected'],x['current_GND_physical_pads'])for x in returns]},indent=2))
