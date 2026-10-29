from pathlib import Path
import pcbnew as p,json,math
D=Path(__file__).resolve().parents[1];SOURCE=D.parent/'xclk_frontier_study';seed=p.LoadBoard(str(SOURCE/'vio_inner_detour.kicad_pcb'));b=p.LoadBoard(str(D/'mainboard_revD.kicad_pcb'));base=p.LoadBoard(str(SOURCE/'channel_v2.kicad_pcb'))
def sig(t):return [t.GetClass(),t.GetNetname(),t.GetLayer(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetWidth(p.F_Cu) if t.GetClass()=='PCB_VIA' else t.GetWidth(),t.GetDrillValue() if t.GetClass()=='PCB_VIA' else 0]
x={t.m_Uuid.AsString():sig(t) for t in seed.GetTracks()};y={t.m_Uuid.AsString():sig(t) for t in b.GetTracks()};assert all(y.get(k)==v for k,v in x.items());added={k:v for k,v in y.items() if k not in x};assert all(v[1]=='CAM_XCLK' for v in added.values()),'STOP unexpected new net after reload'
assert all(v[2] in [p.F_Cu,p.B_Cu] for v in added.values());assert all((v[7],v[8])==((600000,300000) if v[0]=='PCB_VIA' else (127000,0)) for v in added.values())
w={t.m_Uuid.AsString():sig(t) for t in base.GetTracks()};vr={k:v for k,v in w.items() if k not in x};va={k:v for k,v in x.items() if k not in w};assert len(vr)==10 and len(va)==5;assert all(v[0]=='PCB_TRACK' and v[1]=='SENS_VIO_1V8' and v[7]==150000 for v in [*vr.values(),*va.values()]);assert all(x.get(k)==v for k,v in w.items() if k not in vr)
b.BuildConnectivity();c=b.GetConnectivity();pad=next(a for f in b.GetFootprints() if f.GetReference()=='U101' for a in f.Pads() if a.GetNumber()=='43');q=[pad];seen=set();pads=set()
while q:
 o=q.pop();uid=o.m_Uuid.AsString()
 if uid in seen:continue
 seen.add(uid)
 if o.GetClass()=='PAD':pads.add(o.GetParentFootprint().GetReference()+'.'+o.GetNumber())
 q.extend(c.GetConnectedTracks(o));q.extend(c.GetConnectedPads(o))
assert pads=={'U101.43','U203.4','R221.1'}
def lengths(items):
 r={}
 for v in items:
  if v[0]=='PCB_TRACK':
   layer=b.GetLayerName(v[2]);r[layer]=r.get(layer,0)+math.hypot(v[5]-v[3],v[6]-v[4])/1e6
 return r
polys=[z.GetFilledPolysList(p.In1_Cu) for z in b.Zones() if z.GetLayer()==p.In1_Cu and z.GetNetname()=='GND'];returnrows=[]
for uid,v in added.items():
 if v[0]!='PCB_TRACK':continue
 ax,ay,zx,zy=[q/1e6 for q in v[3:7]];dx=zx-ax;dy=zy-ay;L=math.hypot(dx,dy);N=max(1,math.ceil(L/.05));miss=0;total=0
 for i in range(N+1):
  for off in [-v[7]/2e6,0,v[7]/2e6]:
   xx=ax+dx*i/N-off*dy/L;yy=ay+dy*i/N+off*dx/L;point=p.VECTOR2I(p.FromMM(xx),p.FromMM(yy));total+=1;miss+=not any(pp.Contains(point) for pp in polys)
 returnrows.append({'uuid':uid,'layer':b.GetLayerName(v[2]),'length_mm':L,'sample_count':total,'missing_direct_In1_projection_samples':miss})
gvias=[(p.ToMM(t.GetPosition().x),p.ToMM(t.GetPosition().y)) for t in b.GetTracks() if t.GetClass()=='PCB_VIA' and t.GetNetname()=='GND'];viareport=[]
for uid,v in added.items():
 if v[0]=='PCB_VIA':
  pos=[v[3]/1e6,v[4]/1e6];near=min(gvias,key=lambda a:math.dist(a,pos));viareport.append({'uuid':uid,'xy_mm':pos,'nearest_ground_via_mm':near,'distance_mm':math.dist(near,pos)})
out={'new_XCLK_items':added,'new_XCLK_track_lengths_mm':lengths(added.values()),'all_XCLK_track_lengths_mm':lengths(v for v in y.values() if v[1]=='CAM_XCLK'),'new_clock_vias':viareport,'actual_clock_connected_pads':sorted(pads),'preserved_existing_copper_items_vs_vio_detour':len(x),'VIO_removed_B_segments':vr,'VIO_added_In2_segments':va,'VIO_old_segment_length_mm':lengths(vr.values()),'VIO_new_segment_length_mm':lengths(va.values()),'clock_In1_projection':{'method':'actual filled SHAPE_POLY_SET.Contains, center and +/-half-width every <=0.05mm. Not exact area fraction, field solver, impedance or current-loop validation. B Cu nearest reference is In2 power, not automatically In1; actual stackup/return coupling remains unresolved.','per_segment':returnrows,'total_samples':sum(r['sample_count'] for r in returnrows),'missing_samples':sum(r['missing_direct_In1_projection_samples'] for r in returnrows)}}
(D/'xclk_candidate_checks.json').write_text(json.dumps(out,indent=2));print({k:out[k] for k in ['new_XCLK_track_lengths_mm','all_XCLK_track_lengths_mm','VIO_old_segment_length_mm','VIO_new_segment_length_mm']});print('new clock vias',len(viareport),'return samples missing',out['clock_In1_projection']['missing_samples'],'/',out['clock_In1_projection']['total_samples'])
