from pathlib import Path
import json,hashlib,shutil
P=Path(__file__).resolve().parent;F=P.parent/'smart_pen_tilt_roi_v4_candidate_20261030';R=P.parent/'smart_pen_tilt_v4_review_run_20261030'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pre=json.loads((P/'pre_snapshot.json').read_text());post={str(q.relative_to(F)):sha(q) for q in F.rglob('*') if q.is_file()};assert pre==post
(P/'post_snapshot.json').write_text(json.dumps(post,indent=2)+'\n')
m=json.loads((F/'MANIFEST.json').read_text());assert all(sha(F/x['path'])==x['sha256'] and (F/x['path']).stat().st_size==x['bytes'] for x in m['files'])
v3=P.parent/'smart_pen_continuous_roi_v3_candidate_20261029';vm=json.loads((v3/'verification/V3_SNAPSHOT.json').read_text());assert all(sha(root/x['path'])==x['sha256'] for x in vm['files'] for root in (v3,F/'source'))
def norm(v):
 if isinstance(v,dict):return {k:norm(x) for k,x in v.items() if k not in ('host_seconds','seconds')}
 if isinstance(v,list):return [norm(x) for x in v]
 return v
files=['candidate_eight.json','candidate_eight_oracle.json','heldout_results.json','regression_results.json','regression_summary.json','legacy44_results.json','heldout_oracle_selftest.json','support_oracle_selftest.json']
comparisons={}
(P/'reproduced').mkdir(exist_ok=True)
for f in files:
 comparisons[f]=norm(json.loads((F/f).read_text()))==norm(json.loads((R/f).read_text()))
 shutil.copyfile(R/f,P/'reproduced'/f)
assert all(comparisons.values()),comparisons
held=json.loads((R/'heldout_results.json').read_text())['cases'];reg=json.loads((R/'regression_results.json').read_text())['cases'];eight=json.loads((R/'candidate_eight.json').read_text());legacy=json.loads((R/'legacy44_results.json').read_text())
log=(P/'reproduce.log').read_text();exitcode=int((P/'reproduce.exit').read_text());assert exitcode==1 and log.count('EXIT 1:')==1 and 'EXIT 1: ../smart_pen_host_venv_20261028/bin/python run_regression.py' in log and 'Ran 85 tests' in log and '\nOK\n' in log and 'skipped=' not in log
summary=dict(decision='NOT_ADOPTED',freeze_manifest_sha256=sha(F/'MANIFEST.json'),manifest_files_checked=len(m['files']),all_actual_files_unchanged=len(post),legacy_files_checked=len(vm['files']),semantic_reproduction=comparisons,eight=dict(n=len(eight),accepted=sum(r['status']==0 for r in eight)),heldout=dict(n=len(held),correct=sum(r.get('correct',False) for r in held),rejected=sum(r['status']!=0 for r in held)),regression=dict(n=len(reg),correct=sum(r.get('correct',False) for r in reg),quality_contract_violations=sum(r['status']==0 and not r['correct'] for r in reg),rejected=sum(r['status']!=0 for r in reg)),old_abi_cold=len(legacy),old_abi_warm=sum(r['warm_tested'] for r in legacy),host_tests=85,host_skips=0,reproduce_exit=exitcode,expected_red_gate='three original must_reject edge_stroke accepts; coordinate/symbol/orientation correct',independent_numerical_checks=39,asan_ubsan_pass=True,lsan_tested=False,hardware_sdk_performance_tested=False)
(P/'verification_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
