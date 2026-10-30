from pathlib import Path
import os,json,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/junction1215';import pcbnew as p
O=Path(__file__).resolve().parent;W=O.parent;H=W/'smart_pen_next_20261028/hardware';q=H/'sccb_local_reference_1216/native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(q));old=p.LoadBoard(str(H/'control_envelope_native_1051/native/mainboard_revD.kicad_pcb'))
if hashlib.sha256(q.read_bytes()).hexdigest()!='dcbd2e6501c8294ece5ecf7b41ffcc86ccc7f58f7cb54ececfdf24962a50f697':raise RuntimeError('native changed')
def sh(t):
 s=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(s,p.B_Cu,0,50,p.ERROR_OUTSIDE);return s
parent=p.SHAPE_POLY_SET()
for t in old.GetTracks():
 if t.GetNetname()=='3V3_AON'and(isinstance(t,p.PCB_VIA)or t.GetLayer()==p.B_Cu):parent.BooleanAdd(sh(t))
keys={frozenset([(10.9,64.875),(11.125,65.025)]),frozenset([(11.125,65.025),(12.05,64.875)])};branch=p.SHAPE_POLY_SET();found=[]
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA)or t.GetLayer()!=p.B_Cu or t.GetNetname()!='3V3_AON':continue
 a=(t.GetStart().x/1e6,t.GetStart().y/1e6);c=(t.GetEnd().x/1e6,t.GetEnd().y/1e6)
 if frozenset([a,c])in keys:branch.BooleanAdd(sh(t));found.append([a,c,t.GetWidth()/1e6])
if len(found)!=2 or any(x[2]!=.5 for x in found):raise RuntimeError('corner path changed')
rows=[];L=json.load(open(W/'assembly_context_audit_0818_20261030/all103_sync.json'))['rows']
for ref in ['C301','U301']:
 r=next(x for x in L if x['ref']==ref);bb=r['contexts'][0]['entities'][0]['projected_current_bounds_not_final_assembly'];xy=[bb[0]+7,127-bb[5],bb[3]+7,127-bb[2]];rect=p.SHAPE_POLY_SET();rect.NewOutline()
 for x,y in [(xy[0],xy[1]),(xy[2],xy[1]),(xy[2],xy[3]),(xy[0],xy[3])]:rect.Append(round(x*1e6),round(y*1e6))
 inter=p.SHAPE_POLY_SET();inter.BooleanIntersection(branch,rect);delta=p.SHAPE_POLY_SET();delta.BooleanSubtract(inter,parent);rows.append({'ref':ref,'full_bounds':xy,'total_branch_projection_mm2':inter.Area()/1e12,'additional_projection_beyond_parent_same_net_B_copper_mm2':delta.Area()/1e12})
 if delta.Area()!=0:raise RuntimeError('new underbody projection remains')
result={'pcb_sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'exact_half_mm_corner_segments':found,'rows':rows,'scope':'zero newly occupied projection within these full budgets; no soldermask/process qualification; no expanded old-copper tolerance mask'};(O/'source_junction.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
