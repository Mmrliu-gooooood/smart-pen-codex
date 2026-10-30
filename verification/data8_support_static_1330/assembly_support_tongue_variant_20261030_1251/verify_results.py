import json
from pathlib import Path
R=Path(__file__).resolve().parent/'corrected_connected'
a=json.loads((R/'exact_context_tests.json').read_text());c=json.loads((R/'contact_results.json').read_text());p=json.loads((R/'preservation.json').read_text())
if len(a)!=3 or len(c)!=3 or len(p)!=3:raise RuntimeError('incomplete contexts')
for row in a:
 if row['installation_count']!=104 or not all(row['valid'].values()) or any(v!=1 for v in row['solids'].values()) or row['full_envelope_hits']or row['part_intersections']:raise RuntimeError('candidate interference/validity gate failed')
for row in c:
 expected=.8
 if row['head_distance']>1e-8 or abs(row['head_contact_face_area']-expected)>1e-7 or row['head_common_volume']>1e-7:raise RuntimeError('head geometry failed')
 if row['context'].startswith('ACCESS'):
  if row['right_toe_distance']>1e-8 or row['right_toe_common_volume']>1e-7 or abs(row['secondary_catch_gap']-.1)>1e-8 or row['new_head_block_old_root_overlap_mm3']<.1:raise RuntimeError('ACCESS support geometry failed')
for row in p:
 if row['board_plus_installations']!=105 or any(abs(x['volume_symmetric_difference'])>1e-7 or not x['bounds_equal']or not x['valid']for x in row['checks']):raise RuntimeError('full shape preservation failed')
print('PASS narrow nominal support geometry; NOT material/preload/process/access qualification')

d=json.loads((R.parent/'clearances.json').read_text())
if len(d)!=7 or any(x['envelopes_checked']!=104 or x['touching'] for x in d):raise RuntimeError('full budget distance gate failed')
for x in d:
 if x['changed_part'] in ['Common_base','Lower_common_datum_STUDY']:
  q=next(v for v in x['all_distances'] if v['envelope']=='INSTALL_J202_91')
  if q['distance_mm']<.2-1e-9:raise RuntimeError('J202 nominal gap below .2')
print('PASS J202 full-budget nominal separation >=.2; no process waiver')
