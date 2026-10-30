from pathlib import Path
import csv,json
D=Path(__file__).resolve().parent;rows=list(csv.DictReader((D/'checks/candidate/bom.csv').open()))
for r in rows:
 r['qualification_status']='SOURCE_CANDIDATE_NOT_PROCUREMENT_OR_MANUFACTURING_QUALIFIED'if r.get('MPN_candidate')else'SOURCE_IDENTIFIER_ONLY_NOT_MANUFACTURING_RELEASE'if r.get('MPN')else'UNSPECIFIED_MPN_NOT_READY_TO_ORDER'
 r['release_status']='NOFAB / NOPOWER'
with(D/'bom_qualification.csv').open('w')as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
selected={r['Reference']:r for r in rows if r['Reference']in['U205','C209','R202']}
if set(selected)!={'U205','C209','R202'}or not all(r['MPN_candidate']for r in selected.values()):raise RuntimeError('candidate fields lost')
(D/'bom_policy.json').write_text(json.dumps({'raw_export':'checks/candidate/bom.csv','derived_export':'bom_qualification.csv','rule':'MPN and MPN_candidate exported separately; neither auto-promoted or filled from PCB properties; qualification column is a conservative derived label, not a changed source field','source_changes':False,'candidate_rows':selected},indent=2)+'\n')
