from pathlib import Path
import os,json,sys,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/court0949ref'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'hardware/translator_domain_candidate_0130'));from finite_copper import shape
A=D.parent/'tail100_routing_native_0927/native/mainboard_revD.kicad_pcb';B=D/'native/mainboard_revD.kicad_pcb';a=p.LoadBoard(str(A));b=p.LoadBoard(str(B));pts=[(4.325,87.806350),(4.299435,87.799500),(4.275500,87.799500),(4.325,87.778996)];poly=p.SHAPE_POLY_SET();poly.NewOutline()
for x,y in pts:poly.Append(round(x*1e6),round(y*1e6))
rows=[]
for board in [a,b]:
 sh=p.SHAPE_POLY_SET()
 for t in board.GetTracks():
  if t.GetNetname()=='SENS_EXTCLK'and not isinstance(t,p.PCB_VIA)and t.GetLayer()==p.In3_Cu:sh.BooleanAdd(shape(t,p.In3_Cu))
 sh.BooleanIntersection(poly);rows.append(sh.Area()/1e12)
if rows[1]!=0:raise RuntimeError('new clock still traverses independently localized adjacent gap')
uid='e2b8a441-8174-5053-9c1f-9663c07c93d3';va=next(t for t in a.GetTracks()if t.m_Uuid.AsString()==uid);vb=next(t for t in b.GetTracks()if t.m_Uuid.AsString()==uid)
if va.GetPosition()!=vb.GetPosition()or va.GetWidth(p.F_Cu)!=vb.GetWidth(p.F_Cu)or va.GetDrillValue()!=vb.GetDrillValue():raise RuntimeError('adjacent SDA via unchanged')
lengths=[]
for board in [a,b]:
 out={}
 for net in ['GND','SENS_VIO_1V8','SENS_EXTCLK']:
  tracks=[t for t in board.GetTracks()if t.GetNetname()==net and not isinstance(t,p.PCB_VIA)];out[net]={'planar_length_mm':sum(t.GetLength()/1e6 for t in tracks),'segments':len(tracks),'vias':sum(t.GetNetname()==net and isinstance(t,p.PCB_VIA)for t in board.GetTracks()),'per_layer_mm':{board.GetLayerName(l):sum(t.GetLength()/1e6 for t in tracks if t.GetLayer()==l)for l in[p.F_Cu,p.In3_Cu,p.B_Cu]}}
 lengths.append(out)
print(json.dumps({'independently_localized_adjacent_clearance_gap_vertices_mm':pts,'old_clock_projection_in_gap_mm2':rows[0],'new_clock_projection_in_gap_mm2':rows[1],'adjacent_AON_SDA_via_raw_geometry_unchanged':True,'clock_avoids_gap_not_claim_gap_filled':True,'parent_and_candidate_total_net_lengths':lengths,'limits':['Route length changes require whole-clock timing/return qualification; geometry is not timing approval','Own-antipad and all residual uncovered areas remain fully reported in verify.json','Existing local supply vias retain diameter/drill; no current/thermal qualification']},indent=2))
