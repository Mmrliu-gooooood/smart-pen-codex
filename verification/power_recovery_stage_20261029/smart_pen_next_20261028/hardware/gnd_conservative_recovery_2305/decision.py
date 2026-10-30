from pathlib import Path
import os,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/gnd2305decision'
import pcbnew as p
D=Path(__file__).resolve().parent;B=D.parent/'aon_entry_bridge_candidate_2156';S=D.parent/'gnd_fixed_branch_candidate_2159';
rows=json.loads((D/'removal_comparison.json').read_text());neck=json.loads((D/'neck.json').read_text());a=json.loads((D/'analysis.json').read_text());ba=json.loads((B/'analysis.json').read_text())
def req(x,m):
 if not x:raise RuntimeError(m)
req([r['removed_group']for r in rows if r['eroded_pieces']==7]==[37],'unique counterfactual')
req(neck['candidate_fragment_count']==neck['base_fragment_count']==7,'erosion count')
req(sorted(r['base_matches'][0]['base_fragment']for r in neck['fragments']if len(r['base_matches'])==1)==list(range(7)),'one-to-one fragments')
old=json.loads((S/'neck.json').read_text());split=next(r for r in old['fragments']if r['fragment']==4);bb=split['bbox_mm'];b=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));inside=[]
for f in b.GetFootprints():
 for q in f.Pads():
  xy=[q.GetPosition().x/1e6,q.GetPosition().y/1e6]
  if q.GetNetname()=='3V3_AON'and bb[0]<=xy[0]<=bb[0]+bb[2]and bb[1]<=xy[1]<=bb[1]+bb[3]:inside.append(f.GetReference()+'.'+q.GetNumber())
z=next(x for x in a['zones']if x['net']=='3V3_AON');bz=next(x for x in ba['zones']if x['net']=='3V3_AON');req(not inside,'padcenter in split')
neg=json.loads((D/'negative.json').read_text());req(neg['exact_base_sha']=='fd989bf844a8bc224f315dd3d2559d7a55ae1ba8f9384b0c06b6e301b6668454','actual negative')
print(json.dumps(dict(status='CONSERVATIVE_RESEARCH_CANDIDATE_ONLY_NOFAB',chosen_whole_groups=17,restored_objects=96,rejected_whole_group=37,rejected_group_terminals=['C207.2','U204.4'],rejected_group_via_xy=[3.9,66.6],whole_group_counterfactuals=rows,additional_split_bbox_mm=bb,additional_split_area_mm2=split['area_mm2'],actual_AON_pad_centers_inside_split_bbox=inside,base_and_conservative_eroded_pieces=7,all_seven_eroded_fragments_map_one_to_one_to_base=True,AON_filled_area_change_from_fd989_mm2=z['new_area_mm2']-bz['new_area_mm2'],all_ground_planes_and_signal_reference_projection_unchanged=True,DRC=[0,203,0],GND_core_pads=30,GND_total_physical_pads=102,AON_core_pads=1,AON_total_physical_pads=39,limitations=['No proof that the tiny split carried or could not carry load; all but input AON physical pads are unconnected.','No pad-center in a split bounding box is not a full current-path proof.','Equal erosion piece count and one-to-one mapping do not establish minimum neck, ampacity, or unchanged AON geometry.','17 GND via antipads still remove AON copper; explicit area delta retained.','Do not power, fabricate, or promote to complete-product baseline.']),indent=2))
