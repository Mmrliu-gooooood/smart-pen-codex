from pathlib import Path
import pcbnew as p,json,hashlib,sys,re,math
D=Path(__file__).resolve().parent;S=D/'parent';C=Path(sys.argv[1])if len(sys.argv)>1 else D/'candidate';sys.path.insert(0,str(D/'review_dependencies'))
from finite_copper import build,components
from native_polygon import native_fractured_once
from native_blocks import blocks
c=json.loads((D/'native_contract.json').read_text());A=S/'mainboard_revD.kicad_pcb';B=C/A.name;a=p.LoadBoard(str(A));b=p.LoadBoard(str(B));removed=set(c['removed']);added={r['uuid']for r in c['objects']};ck={}
def raw(f):return{re.search(r'\(uuid "([^"]+)"\)',v).group(1):v for _,_,v in blocks(f.read_text())if v.startswith(('(segment','(via'))}
x,y=raw(A),raw(B);old={t.m_Uuid.AsString():t for t in a.GetTracks()};new={t.m_Uuid.AsString():t for t in b.GetTracks()};ck['exact_23_removals_20_additions']=set(x)-set(y)==removed and set(y)-set(x)==added and len(removed)==23 and len(added)==20;ck['all_retained_copper_raw_exact']=all(y.get(u)==v for u,v in x.items()if u not in removed)
def baseblocks(f):return[v for _,_,v in blocks(f.read_text())if not v.startswith(('(segment','(via','(zone')) and not (v.startswith('(footprint') and '(property \"Reference\" \"J107\"' in v)]
ck['all_nonrouting_except_declared_J107_raw_exact']=baseblocks(A)==baseblocks(B)
def zones(f):
 out=[]
 for _,_,v in blocks(f.read_text()):
  if v.startswith('(zone'):out.append([z for _,_,z in blocks(v)if not z.startswith(('(filled_polygon','(fill_segments'))])
 return out
ck['zone_definitions_exact']=zones(A)==zones(B);ck['all_retained_dependencies_except_declared_schematic_exact']=all((C/f.relative_to(S)).exists()and(C/f.relative_to(S)).read_bytes()==f.read_bytes()for f in S.rglob('*')if f.is_file()and f.suffix not in['.kicad_pcb','.kicad_prl'] and str(f.relative_to(S))!='schematic/usb_entry.kicad_sch')
ck['all_added_exact']=True;V=lambda xy:p.VECTOR2I(round(xy[0]*1e6),round(xy[1]*1e6))
for row in c['objects']:
 q=new.get(row['uuid']);v=row['type']=='via'
 ok=q is not None and q.GetNetname()==row['net']and q.GetStart()==V(row['start'])and q.GetEnd()==V(row['end'])and(q.GetWidth(p.F_Cu)if v else q.GetWidth())==round(row['width']*1e6)
 ok=ok and(q.GetDrillValue()==round(row['drill']*1e6)if v else q.GetLayer()==b.GetLayerID(row['layer']))
 ck['all_added_exact'] &= ok
af=next(f for f in a.GetFootprints()if f.GetReference()=='J107');bf=next(f for f in b.GetFootprints()if f.GetReference()=='J107');ap={q.GetNumber():q for q in af.Pads()};bp={q.GetNumber():q for q in bf.Pads()}
ck['J107_exact_three_owned_terminals']=set(ap)==set(bp)=={'1','2','3'}
ck['J107_custom_identity_and_origin']=str(bf.GetFPID().GetLibItemName())=='J107_DistributedWireLands3_NOFAB'and bf.GetPosition()==p.VECTOR2I(6400000,31660000)and bf.GetOrientationDegrees()==0
ck['J107_pad_sizes_shapes_masks_nets_unchanged']=all(bp[n].GetNetname()==q.GetNetname()and bp[n].GetSize()==q.GetSize()and bp[n].GetShape()==q.GetShape()and bp[n].GetLocalSolderMaskMargin()==q.GetLocalSolderMaskMargin()and bp[n].IsOnLayer(p.B_Cu)and not bp[n].IsOnLayer(p.F_Cu)for n,q in ap.items())
ck['J107_all_three_exact_new_poses']=all(bp[n].GetPosition()==p.VECTOR2I(round(xy[0]*1e6),round(xy[1]*1e6))and bp[n].GetOrientationDegrees()==ang for n,xy,ang,_ in c['pads'])
oldsch=(S/'schematic/usb_entry.kicad_sch').read_text();newsch=(C/'schematic/usb_entry.kicad_sch').read_text();ck['schematic_only_declared_footprint_association']=oldsch.count('GateStudy:J107_Wirebank_PRELAYOUT')==1 and newsch==oldsch.replace('GateStudy:J107_Wirebank_PRELAYOUT','GateStudy:J107_DistributedWireLands3_NOFAB')
oldfiles={str(f.relative_to(S))for f in S.rglob('*')if f.is_file()};newfiles={str(f.relative_to(C))for f in C.rglob('*')if f.is_file()};ck['only_declared_custom_library_file_added']=newfiles-oldfiles=={'GateStudy.pretty/J107_DistributedWireLands3_NOFAB.kicad_mod'}and not(oldfiles-newfiles)
if not all(ck.values()):raise RuntimeError('raw contract '+str(ck))
print('raw PASS',flush=True)
av,bv=build(a),build(b);oa={n:components(v)for n,v in av.items()};nb={n:components(v)for n,v in bv.items()};changes={n:{'old':v,'new':nb[n]}for n,v in oa.items()if v!=nb[n]};ck['all92_partitions_only_USB_EN2_merge']=len(oa)==92 and changes==c['expected_partition_merge'];cores={n:len(next(z for z in nb[n]if t in z))for n,t in [('GND','J106.3'),('3V3_AON','J106.2'),('SENS_VIO_1V8','J202.23')]};ck['cores_103_41_12']=cores=={'GND':103,'3V3_AON':41,'SENS_VIO_1V8':12}
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
r={'source_sha256':hashlib.sha256(A.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(B.read_bytes()).hexdigest(),'checks':ck,'old_copper_count':len(old),'new_copper_count':len(new),'retained_copper_count':len(old)-23,'partition_changes':changes,'cores':cores,'planes':pd,'new_via_drill_checks':nearest,'footprints':len(list(b.GetFootprints()))};(D/('verify_candidate_O.json'if not __debug__ else 'verify_candidate.json')).write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
if not all(ck.values()):raise RuntimeError('candidate invariant failure')
