from pathlib import Path
import json
D=Path(__file__).resolve().parent
for s in ['check','config_and_drc','source_check','independent']:
 a=json.loads((D/(s+'_normal.json')).read_text());b=json.loads((D/(s+'_optimized.json')).read_text())
 if a!=b:raise RuntimeError('Normal/-O mismatch '+s)
x=json.loads((D/'negative_results.json').read_text())
if len(x)!=10 or any(v.get('exit')!=1 for v in x[:8])or any(v.get('native_exit')!=5 or v.get('expected_keepout_hits',0)<1 for v in x[8:]):raise RuntimeError('Negative evidence')
print(json.dumps({'normal_optimized_pairs_equal':4,'rule_mutation_expected_rejections':8,'native_rule_enforcement_cases':2,'decision':'CONDITIONAL_IRQ_REFERENCE_RULE_BASELINE_ONLY_NOFAB'},indent=2))
