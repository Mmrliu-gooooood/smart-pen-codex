from pathlib import Path
import json,hashlib,sys,collections
D=Path(__file__).resolve().parent;H=D.parent;S=H/'gate_cam_on_path_maintenance';B=H/'gate_control_output_candidate'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def req(v,m):
 if not v:raise RuntimeError(m)
inputs={}
for folder,want in [(S,'691382b1d07926ef4430f8aaa98f64f5cf04006f5bd2dd0726adeb657c548de1'),(B,'70f161b643809f8c930c2b32bf82725be6ba742d52635171442646c5bfd6cf52')]:
 req(sha(folder/'manifest.json')==want,'Manifest drift');m=json.loads((folder/'manifest.json').read_text());fs=m.get('files',m)
 for n,h in fs.items():req(sha(folder/n)==(h['sha256'] if isinstance(h,dict) else h),'Frozen input drift '+n)
 inputs[folder.name]={'sha256':want,'files':len(fs)}
req(sha(D/'native/mainboard_revD.kicad_pcb')=='1c4907d04a2bf2dea3a53f89266bc49c0cb96a0683b4898b58cd36b6525ec16d','PCB drift')
sys.path.insert(0,str(D));import pcb_preflight as pf
lock=json.loads((D/'preflight_lock.json').read_text());cfg=pf.verify(D/'native/mainboard_revD.kicad_pcb',lock);cfg.pop('checked_utc',None);req(not cfg['manufacturing_approved'],'Unexpected manufacture approval')
m=json.loads((D/'maintenance.json').read_text());req(m['violation_multiset_identical'] and m['all90_net_pad_partitions_identical'] and m['all_five_native_zone_layer_polygon_serializations_identical'],'Native topology/fill evidence')
for layer,r in m['reference_coverage'].items():req(r['after_CAM_ON_copper_not_over_filled_GND_mm2']<=r['before_CAM_ON_copper_not_over_filled_GND_mm2'],'Adjacent GND projection degraded '+layer)
# Exact branch endpoint degree and via preservation measured from native integer geometry.
import os
os.environ['XDG_CONFIG_HOME']='/tmp/rf-independent/config'
import pcbnew as p
summary={}
for label,file in [('baseline',B/'mainboard_revD.kicad_pcb'),('candidate',D/'native/mainboard_revD.kicad_pcb')]:
 b=p.LoadBoard(str(file));tracks=[t for t in b.GetTracks() if t.GetNetname()=='CAM_ON' and not isinstance(t,p.PCB_VIA)];vias=[t for t in b.GetTracks() if t.GetNetname()=='CAM_ON' and isinstance(t,p.PCB_VIA)];degree=collections.Counter()
 for t in tracks:
  for q in [t.GetStart(),t.GetEnd()]:degree[(q.x,q.y,t.GetLayer())]+=1
 physical=0
 for t in tracks:
  if t.GetLayer()!=p.F_Cu:continue
  a,z=t.GetStart(),t.GetEnd();qx,qy=8400000,67950000
  if (z.x-a.x)*(qy-a.y)!=(z.y-a.y)*(qx-a.x):continue
  if min(a.x,z.x)<=qx<=max(a.x,z.x) and min(a.y,z.y)<=qy<=max(a.y,z.y):physical+=1 if (qx,qy) in [(a.x,a.y),(z.x,z.y)] else 2
 summary[label]={'physical_T_degree':physical,'tracks':len(tracks),'vias':len(vias),'trace_mm':sum(p.ToMM(t.GetLength()) for t in tracks),'F_T_branch_degree':degree[(8400000,67950000,p.F_Cu)],'widths_mm':sorted({p.ToMM(t.GetWidth()) for t in tracks})}
req(summary['baseline']['physical_T_degree']==summary['candidate']['physical_T_degree']==3,'T branch degree')
req(summary['baseline']['vias']==summary['candidate']['vias']==3 and summary['candidate']['widths_mm']==[.15],'Via count/width')
req(summary['baseline']['tracks']==44 and summary['candidate']['tracks']==9,'CAM_ON count')
print(json.dumps({'decision':'SUITABLE_NEXT_ROUTING_BASELINE_ONLY_NOFAB','inputs':inputs,'configuration':cfg,'actual_branch_statistics':summary,'adjacent_GND_projection_not_worse':True,'static_dynamic_gates_unchanged':True},indent=2))
