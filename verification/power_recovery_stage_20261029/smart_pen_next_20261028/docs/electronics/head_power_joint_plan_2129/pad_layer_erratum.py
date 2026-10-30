from pathlib import Path
import json,os,hashlib
os.environ['XDG_CONFIG_HOME']='/tmp/pen-pad-layer-erratum'
import pcbnew as p
D=Path(__file__).resolve().parent;R=D.parents[2];S=R/'hardware/complete_net_restore_candidate_2014/native/mainboard_revD.kicad_pcb';b=p.LoadBoard(str(S));L=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]
rows=[]
for f in b.GetFootprints():
 for q in f.Pads():rows.append(dict(uuid=q.m_Uuid.AsString(),ref=f.GetReference(),pin=q.GetNumber(),net=q.GetNetname(),xy=[q.GetPosition().x/1e6,q.GetPosition().y/1e6],footprint_side=b.GetLayerName(f.GetLayer()),copper_layers=[b.GetLayerName(l)for l in L if q.IsOnLayer(l)],raw_PAD_GetLayer=b.GetLayerName(q.GetLayer())))
byid={r['uuid']:r for r in rows};old=json.loads((R/'docs/electronics/power_backbone_recovery_2124/plan.json').read_text())['pad_contract'];bad=[]
for o in old:
 r=byid[o['uuid']]
 if o['side']not in r['copper_layers']:bad.append(dict(ref=r['ref'],pin=r['pin'],net=r['net'],old_side=o['side'],correct_copper_layers=r['copper_layers'],correct_footprint_side=r['footprint_side']))
result=dict(input_sha=hashlib.sha256(S.read_bytes()).hexdigest(),all_actual_pads=rows,affected_2124_contract_entries=bad,affected_fields=['power_backbone_plan_2022/plan.json:pad_contract.side','power_backbone_recovery_2124/plan.json:pad_contract.side','power_backbone_recovery_2124/plan_normal.json:pad_contract.side','power_backbone_recovery_2124/power_pad_contract.csv:side'],unchanged=['pad UUID','pad count','ref and pin','net name','physical xy','physical size'],geometry_evidence={'power_backbone_plan_2022/plan.py':'check uses t.IsOnLayer/q.IsOnLayer before all copper intersection and pad drill tests','power_backbone_recovery_2124/plan.py':'same IsOnLayer filtering; side exported only in pad_contract','power_backbone_recovery_2124/verify.py':'pad source identity/count via net and UUID; geometry IsOnLayer','copper_recovery_plan_2005/analyze.py':'IsOnLayer at lines36/46/56; native GetConnectedPads graph','hardware/complete_net_restore_candidate_2014/verify.py':'GetLayerSet.FmtHex pad source signature and native connectivity','hardware/complete_net_restore_independent_review_2020/finite_copper.py':'IsOnLayer finite copper graph','hardware/dvp_joint_native_candidate_1950/verify.py':'IsOnLayer for source and target pads','hardware/dvp_joint_native_independent_review_1955/finite_copper.py':'IsOnLayer finite copper graph'},limits='Targeted provenance audit only, not global proof of every historical script; current visual uses IsOnLayer actual copper_layers, no native geometry changed.')
(D/'pad_layer_erratum.json').write_text(json.dumps(result,indent=2)+'\n');print(len(rows),len(bad));print(bad)
