from pathlib import Path
import re,json,hashlib
D=Path(__file__).resolve().parent
s=(D/'audit.py').read_text();exec(compile(s[:s.index('na,nb=build')],__file__,'exec'))
protected={r['uuid']for r in json.loads((D.parent/'gate_control_output_candidate/u204_feed_delta.json').read_text())};rows=json.loads((D.parent/'gate_control_output_candidate/new_routes.json').read_text());mainvias={(11.175,61.0),(11.2,55.75)};remove={r['uuid']for r in rows if r['net']=='3V3_AON'and r['uuid']not in protected and(r['type']=='track'and r['width']<.5 or r['type']=='via'and tuple(r['xy'])not in mainvias)}
if not remove:raise RuntimeError('No explicit R203 pull-up branch removed')
raw=path.read_text();raw=re.sub(r'\n\t\((?:segment|via)\n.*?\n\t\)',lambda m:''if any(u in m[0]for u in remove)else m[0],raw,flags=re.S)
O=D/'guard_boards';O.mkdir(exist_ok=True);f=O/'without_R203_branch.kicad_pcb';f.write_text(raw)
import shutil
for ext in ['kicad_pro','kicad_dru','kicad_sch']:shutil.copyfile(D/'native_snapshot'/('mainboard_revD.'+ext),f.with_suffix('.'+ext))
test=p.LoadBoard(str(f));p.ZONE_FILLER(test).Fill(test.Zones());p.SaveBoard(str(f),test)
# Fresh read-back finite copper, not metadata or native ratsnest.
test=p.LoadBoard(str(f));before=components(build(old)['3V3_AON']);after=components(build(test)['3V3_AON']);core=next(c for c in after if 'C104.1'in c);need=set(next(c for c in before if 'C104.1'in c))-{'R203.2'}
(D/'main_feed_diagnostic.json').write_text(json.dumps({'before':before,'after':after,'missing':sorted(need-set(core))},indent=2))
require(need<=set(core),'Main AON needs the removed thin pull-up branch')
require('R203.2'not in core,'Unexpected alternate R203 contact: branch isolation proof invalid')
main=[r for r in rows if r['net']=='3V3_AON'and r['type']=='track'and r['width']==.5];require(main and all(r['layer']=='B.Cu'for r in main),'Dedicated main bridge identity')
print(json.dumps({'pcb_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'removed_pullup_conductors':sorted(remove),'fixture_fresh_refilled':True,'main_AON_all_old_pads_except_R203_preserved':True,'R203_isolated':True,'dedicated_new_main_bridge_width_mm':.5,'main_bridge_centerline_length_mm':sum(math.dist(r['a'],r['z'])for r in main),'main_vias':sorted(mainvias),'AON_components_without_R203_branch':after,'qualification':'DC topology proof only; no current/thermal/PI qualification'},indent=2))
