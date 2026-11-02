from pathlib import Path
import pcbnew as p,json,hashlib,sys,re,math
D=Path(__file__).resolve().parent;S=D/'parent';C=Path(sys.argv[1])if len(sys.argv)>1 else D/'candidate';sys.path.insert(0,str(D/'review_dependencies'))
from finite_copper import build,components
from native_polygon import native_fractured_once
from native_blocks import blocks
c=json.loads((D/'native_contract.json').read_text());A=S/'mainboard_revD.kicad_pcb';B=C/A.name;a=p.LoadBoard(str(A));b=p.LoadBoard(str(B));removed=set(c['removed']);added={r['uuid']for r in c['objects']};ck={}
def raw(f):return{re.search(r'\(uuid "([^"]+)"\)',v).group(1):v for _,_,v in blocks(f.read_text())if v.startswith(('(segment','(via'))}
x,y=raw(A),raw(B);old={t.m_Uuid.AsString():t for t in a.GetTracks()};new={t.m_Uuid.AsString():t for t in b.GetTracks()};ck['exact_one_GNDleaf_removal_eight_additions']=set(x)-set(y)==removed and set(y)-set(x)==added and len(removed)==1 and len(added)==8;ck['all_retained_copper_raw_exact']=all(y.get(u)==v for u,v in x.items()if u not in removed)
def baseblocks(f):return[v for _,_,v in blocks(f.read_text())if not v.startswith(('(segment','(via','(zone')) and not(v.startswith('(footprint')and any('(property "Reference" "'+ref+'"'in v for ref in ['R230','J107']))]
ck['all_nonrouting_except_R230_raw_exact']=baseblocks(A)==baseblocks(B)
def zones(f):
 out=[]
 for _,_,v in blocks(f.read_text()):
  if v.startswith('(zone'):out.append([z for _,_,z in blocks(v)if not z.startswith(('(filled_polygon','(fill_segments'))])
 return out
ck['zone_definitions_exact']=zones(A)==zones(B);ck['all_retained_dependencies_except_declared_schematic_exact']=all((C/f.relative_to(S)).exists()and(C/f.relative_to(S)).read_bytes()==f.read_bytes()for f in S.rglob('*')if f.is_file()and f.suffix not in['.kicad_pcb','.kicad_prl'])
ck['all_added_exact']=True;V=lambda xy:p.VECTOR2I(round(xy[0]*1e6),round(xy[1]*1e6))
for row in c['objects']:
 q=new.get(row['uuid']);v=row['type']=='via'
 ok=q is not None and q.GetNetname()==row['net']and q.GetStart()==V(row['start'])and q.GetEnd()==V(row.get('end',row['start']))and(q.GetWidth(p.F_Cu)if v else q.GetWidth())==round(row['width']*1e6)
 ok=ok and(q.GetDrillValue()==round(row['drill']*1e6)if v else q.GetLayer()==b.GetLayerID(row['layer']))
 ck['all_added_exact'] &= ok
ck['all_existing_vias_raw_retained']=all(u in y and y[u]==x[u]for u,t in old.items()if t.GetClass()=='PCB_VIA')
if not all(ck.values()):raise RuntimeError('raw contract '+str(ck))
expected_fp=(D/'footprint_delta.sexpr').read_text().strip();actual_fp=next(v for _,_,v in blocks(B.read_text())if v.startswith('(footprint')and '(property \"Reference\" \"R230\"'in v);ck['R230_exact_native_rigid_transform']=actual_fp==expected_fp
if not ck['R230_exact_native_rigid_transform']:raise RuntimeError('R230 rigid transform mismatch')
label=next(v for _,_,v in blocks(B.read_text())if v.startswith('(footprint')and '(property "Reference" "J107"'in v)
ck['J107_exact_only_label_position_change']=label==(D/'label_footprint_delta.sexpr').read_text().strip()
if not ck['J107_exact_only_label_position_change']:raise RuntimeError('J107 label transform mismatch')
print('raw PASS',flush=True)
av,bv=build(a),build(b);oa={n:components(v)for n,v in av.items()};nb={n:components(v)for n,v in bv.items()};changes={n:{'old':v,'new':nb[n]}for n,v in oa.items()if v!=nb[n]};ck['all92_partitions_only_D6_bias_merge']=len(oa)==92 and len(oa['SENS_D6'])==2 and set(changes)=={'SENS_D6'} and nb['SENS_D6']==[sorted(t for part in oa['SENS_D6'] for t in part)];cores={n:len(next(z for z in nb[n]if t in z))for n,t in [('GND','J106.3'),('3V3_AON','J106.2'),('SENS_VIO_1V8','J202.23')]};ck['cores_103_41_12']=cores=={'GND':103,'3V3_AON':41,'SENS_VIO_1V8':12}
def planes(board):
 out={}
 for z in board.Zones():
  if not z.GetIsRuleArea():out.setdefault((z.GetLayer(),z.GetNetname()),p.SHAPE_POLY_SET()).BooleanAdd(native_fractured_once(z.GetFilledPolysList(z.GetLayer())))
 return out
def sub(x,y):q=p.SHAPE_POLY_SET(x);q.BooleanSubtract(y);return q
pa,pb=planes(a),planes(b);pd=[{'layer':a.GetLayerName(k[0]),'net':k[1],'lost_mm2':sub(z,pb[k]).Area()/1e12,'gained_mm2':sub(pb[k],z).Area()/1e12,'old_area_mm2':z.Area()/1e12,'new_area_mm2':pb[k].Area()/1e12,'old_islands':z.OutlineCount(),'new_islands':pb[k].OutlineCount()}for k,z in pa.items()];ck['all_saved_planes_one_island']=all(r['old_islands']==1 and r['new_islands']==1 for r in pd)
# Explicit same-net as well as foreign drill spacing (edge-to-edge), including all old holes.
newvias=[new[r['uuid']]for r in c['objects']if r['type']=='via'];allvias=[t for t in b.GetTracks()if t.GetClass()=='PCB_VIA'];nearest=[]
for q in newvias:
 m=(math.inf,None)
 for o in allvias:
  if q.m_Uuid==o.m_Uuid:continue
  gap=math.dist((q.GetPosition().x/1e6,q.GetPosition().y/1e6),(o.GetPosition().x/1e6,o.GetPosition().y/1e6))-(q.GetDrillValue()+o.GetDrillValue())/2e6
  if gap<m[0]:m=(gap,o.m_Uuid.AsString())
 nearest.append({'uuid':q.m_Uuid.AsString(),'net':q.GetNetname(),'nearest_drill_uuid':m[1],'edge_gap_mm':m[0]})
ck['new_via_drill_spacing_including_same_net']=all(x['edge_gap_mm']>=.25-1e-9 for x in nearest)
r={'source_sha256':hashlib.sha256(A.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(B.read_bytes()).hexdigest(),'checks':ck,'old_copper_count':len(old),'new_copper_count':len(new),'retained_copper_count':len(old)-1,'partition_changes':changes,'cores':cores,'planes':pd,'new_via_drill_checks':nearest,'footprints':len(list(b.GetFootprints()))};(D/('verify_candidate_O.json'if not __debug__ else 'verify_candidate.json')).write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
if not all(ck.values()):raise RuntimeError('candidate invariant failure')
