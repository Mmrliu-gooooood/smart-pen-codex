from pathlib import Path
import json,math,hashlib
R=Path(__file__).resolve().parent;d=json.loads((R/'results.json').read_text());prior=R.parent/'width14_gate';inp=json.loads((prior/'input.json').read_text())
def req(ok,msg):
 if not ok:raise RuntimeError(msg)
req(hashlib.sha256(Path(inp['source']).read_bytes()).hexdigest()==d['source_sha256'],'Original native changed')
req(d['left_refs_count']==13 and len(set(d['left_refs']))==13,'Ref count')
for c in d['curves']:
 edge=c['absolute_X_edge_limit'];top=c['Bdatum']+.93+c['height_above_F_including_solder'];req(math.isclose(math.hypot(edge,top),7.9,abs_tol=1e-9),'Radial curve')
 req(math.isclose(c['source_right_outer_edge_limit']-.9,c['J109_center_limit_for1p8wide'],abs_tol=1e-9),'Wire halfwidth')
for r in d['rows']:
 req(r['J109_wire_XY']==[1.8,2.2],'WireXY assumption changed')
 expect=r['left_column_shift']>=.35 and r['J109_center_x']==12.
 req(r['optimized']['passes0p1_screen']==expect,'Threshold regression')
 req(not r['new_same_side_envelope_intersections'],'New envelope intersection')
for f in json.loads((prior/'manifest.json').read_text())['files']:req(hashlib.sha256((prior/f['path']).read_bytes()).hexdigest()==f['sha256'],'Prior gate changed')
print('PASS: source unchanged,13refs, radial equations,1.8mm wirewidth,12-case thresholds and prior10-filefreeze unchanged. NOT electrical/routing approval.')
