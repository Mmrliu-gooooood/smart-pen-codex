from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parents[3];p=r/'hardware/j202_low_speed_reference_candidate/plane_reference_audit.json'
h='eee07162e165719a0b9e76d2b722c80377667401a05bf3f4b616fc348805eb1d'
if hashlib.sha256(p.read_bytes()).hexdigest()!=h:raise RuntimeError('audit identity')
j=json.loads(p.read_text());u=j['old_track_new_reference_unique_union_mm2']
if set(u)!={'USB_EN1','CAM_SCL','SENS_VIO_1V8','SENS_SCL'}:raise RuntimeError('four net identity')
if not 1e-8 < u['CAM_SCL'] < 1e-6:raise RuntimeError('threshold relation')
print(json.dumps({'status':'FOUR_RECORDED_NETS_NOT_EXACTLY_THREE','audit_sha256':h,'unique_union_mm2':u,'report_record_threshold_mm2':1e-8,'nonallowed_fail_threshold_mm2':1e-6,'meaning':'recording and rejection thresholds differ; small CAM_SCL area is reported, not exact zero'},indent=2))
