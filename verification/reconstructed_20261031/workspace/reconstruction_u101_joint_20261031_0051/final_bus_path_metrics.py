from pathlib import Path
import os,json,math
os.environ['XDG_CONFIG_HOME']='/tmp/newreconstruct/config'
import pcbnew as p
D=Path(__file__).resolve().parent;r=json.loads((D/'repack_paths.json').read_text());v=json.loads((D/'final_verification.json').read_text());a=p.LoadBoard(str(D/'native/mainboard_revD.kicad_pcb'));b=p.LoadBoard(str(D/'data8_review_native/mainboard_revD.kicad_pcb'));layers=['F.Cu','In2.Cu','In3.Cu','B.Cu'];rows={}
for i in range(8):
 n='CAM_D'+str(i);path=r['routes'][str(i)];seq=[path[0][0]];directions=[]
 for x,y in zip(path,path[1:]):
  if x[0]!=y[0]:seq.append(y[0]);continue
  d=(y[1]-x[1],y[2]-x[2]);g=math.gcd(abs(d[0]),abs(d[1]));d=(x[0],d[0]//g,d[1]//g)if g else(x[0],0,0)
  if not directions or directions[-1]!=d:directions.append(d)
 oldtracks=[t for t in a.GetTracks()if t.GetNetname()==n and not isinstance(t,p.PCB_VIA)];alltracks=[t for t in b.GetTracks()if t.GetNetname()==n and not isinstance(t,p.PCB_VIA)];m=v['metrics'][n]
 rows[n]={'U101_pad':str(12+i),'GPIO':str(7+i),'U201_A_pad':str(3+i),'bias_ref':'R'+str(210+i),'source_role':'U201 enabled B-to-A output, U101 must be input; 100k bias branch remains','new_join_layer_sequence':[layers[x]for x in seq],'new_join_layer_changes':len(seq)-1,'new_join_direction_runs':len(directions),'new_conductor_metrics':m,'retained_bias_network_track_total_mm':sum(t.GetLength()/1e6 for t in oldtracks),'whole_connected_net_track_total_mm':sum(t.GetLength()/1e6 for t in alltracks),'retained_bias_network_vias':sum(isinstance(t,p.PCB_VIA)for t in a.GetTracks()if t.GetNetname()==n)}
out={'status':'GEOMETRIC_ACCOUNTING_NOT_TIMING_MATCH','rows':rows,'scope':'New conductor totals measure added source-to-existing-net join, not complete pad-to-pad flight time. Retained network total includes both U201 feeder and 100k bias branch, not a claimed pure stub length. Grid layer sequence is reconciled to actual added layer totals; through-via barrel stubs/return transitions remain unqualified. PCLK/VSYNC/HREF and MCU SCCB are still disconnected. No camera rate, edge, loading or setup/hold qualification.','width_policy':'All added data/known signal tracks 0.15mm; native project/rules unchanged. Existing FineSignal127 class is not invoked to lower this group width.'};(D/'final_bus_path_metrics.json').write_text(json.dumps(out,indent=2));print(json.dumps({n:dict(layer_sequence=x['new_join_layer_sequence'],changes=x['new_join_layer_changes'],direction_runs=x['new_join_direction_runs'])for n,x in rows.items()},indent=2))
