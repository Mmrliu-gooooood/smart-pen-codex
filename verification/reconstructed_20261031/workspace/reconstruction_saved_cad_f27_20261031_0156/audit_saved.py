from pathlib import Path
import json,hashlib,sys
sys.path.append('/usr/lib/freecad-python3/lib');import FreeCAD as A
O=Path(__file__).resolve().parent;W=O.parent;E=json.load(open(W/'reconstruction_data8_fullscreen_20261031_0135/proposed_full104.json'));expected={r['entity']:r for r in E['all_static_rectangles']};N=json.load(open(O/'native_pose_evidence.json'));PCB=N['sha256'];rows=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,msg):
 if not v:raise RuntimeError(msg)
for ctx in ['RevC','RevD_BENCH','ACCESS19','ACCESS20']:
 q=O/f'{ctx}_NEW_f27_RESEARCH_NOFAB.FCStd';d=A.openDocument(str(q));S={o.Label:o for o in d.Objects if hasattr(o,'Shape')and not o.Shape.isNull()};body={k:o for k,o in S.items()if k.startswith('INSTALL_')};need(set(body)==set(expected),'full104 identity')
 for k,o in body.items():
  r=expected[k];b=o.Shape.BoundBox;got=[b.XMin+7,127-b.ZMax,b.XMax+7,127-b.ZMin,b.YLength];want=r['xy_bounds']+[r['height']];need(max(abs(x-y)for x,y in zip(got,want))<1e-7,'full saved body budget '+k)
  if r['ref']in ['R101','R503']:
   p=N['rows'][r['ref']];need(max(abs(x-y)for x,y in zip([(b.XMin+b.XMax)/2+7,127-(b.ZMin+b.ZMax)/2],p['xy']))<1e-7,'saved/native pose');need(p['angle_deg']==0 and p['side']==r['side'],'pose orientation/face')
 board=next(o for k,o in S.items()if k.startswith('Native_outline'));need(board.CurrentPCB_SHA256==PCB and d.getObject('NativeBinding').PCB_SHA256==PCB,'saved native metadata');bb=board.Shape.BoundBox;need(max(abs(a-z)for a,z in zip([bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax],[-7,7,2.264793176328504,3.194793176328504,33.7,133.5]))<1e-7,'exact board datum/outline budget');need(abs(board.Shape.Volume-1276.146)<1e-6,'actual stepped outline volume')
 ops=[o.Label.removeprefix('UNQUALIFIED_OPERATION_')for o in d.Objects if o.Label.startswith('UNQUALIFIED_OPERATION_')];need(set(ops)==set(E['unqualified_operation_refs']),'six operational gates')
 rows.append({'context':ctx,'FCStd_sha256':sha(q),'STEP_sha256':sha(q.with_suffix('.step')),'saved_native_sha256':PCB,'all104_bounds_heights_match_exact_overlay':True,'saved_R101_R503_poses_match_actual_native':True,'saved_exact_board_datum_99p8_thickness_budget_0p93':True,'unqualified_operations':sorted(ops)});A.closeDocument(d.Name)
(O/'saved_identity_audit.json').write_text(json.dumps(rows,indent=2)+'\n')
