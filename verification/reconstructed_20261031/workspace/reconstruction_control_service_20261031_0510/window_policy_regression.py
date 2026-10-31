from pathlib import Path
import json
D=Path(__file__).resolve().parent
def outside(pt,box):return {'left':pt[0]<box[0],'bottom':pt[1]<box[1],'right':pt[0]>box[2],'top':pt[1]>box[3]}
point=[11.125,46.625];initial=[11.2,47,13.6,58.6];intermediate=[11.2,46.3,13.6,58.6];selected=[11,46.3,13.6,58.6]
checks={'initial_excludes_two_boundaries':outside(point,initial)=={'left':True,'bottom':True,'right':False,'top':False},'y_expansion_still_left_exclusion':outside(point,intermediate)=={'left':True,'bottom':False,'right':False,'top':False},'selected_contains_actual_gateway':not any(outside(point,selected).values()),'outside_negative_detected':any(outside([10.99,46.625],selected).values())}
if not all(checks.values()):raise RuntimeError(checks)
(D/('window_policy_optimized.json'if not __debug__ else'window_policy.json')).write_text(json.dumps({'checks':checks,'actual_selected_gateway_mm':point,'initial_window':initial,'intermediate_window':intermediate,'selected_window':selected,'scope':'Explicit artificial-layer-window exclusion diagnostic. Bounds are search policy, not manufacturer copper rules. The selected native final independently checks exact finite copper/body/rules and plane changes; no global path impossibility from prior bounded masks.'},indent=2))
