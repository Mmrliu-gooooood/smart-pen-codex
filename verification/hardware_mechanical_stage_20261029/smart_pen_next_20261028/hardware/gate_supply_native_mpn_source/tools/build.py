from pathlib import Path
import json,hashlib,shutil,sys
from sexpr import *
D=Path(__file__).resolve().parents[1];R=D.parents[1];OLD=D.parent/'imu_decoupling_0402_source_fix'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for n,h in json.loads((OLD/'manifest.json').read_text()).items():
 if sha(OLD/n)!=h:raise RuntimeError('source changed '+n)
if (D/'mainboard_projection').exists():raise RuntimeError('no overwrite')
parts={r:{'manufacturer':'KEMET','mpn':m,'status':'CONDITIONAL_NOT_APPROVED_FOR_PROCUREMENT'} for r,m in [('C501','C0402C104K4RACTU'),('C502','C0402C104K4RACTU'),('C503','C0805C106K8RACTU')]}
gate=R/'hardware/camera_power_gate_placement_study/bom_candidates.json'
for row in json.loads(gate.read_text())['parts']:
 ref=row['ref']
 if not ref[1:].isdigit() or not row.get('mpn'):continue
 new=ref[0]+str(300+int(ref[1:]))
 parts[new]={'manufacturer':row['manufacturer'],'mpn':row['mpn'],'status':'GEOMETRY_CANDIDATE_ELECTRICAL_AND_PROCUREMENT_UNQUALIFIED','inherited_restriction':row.get('restriction','')}
seen={}
for folder in ['system_master','mainboard_projection','fixture_projection']:
 shutil.copytree(OLD/folder,D/folder);seen[folder]=[]
 for f in (D/folder).rglob('*.kicad_sch'):
  s=parse(f.read_text());changed=False
  for c in children(s,'symbol'):
   ref=val(prop(c,'Reference')[2])
   if ref not in parts:continue
   row=parts[ref];at=child(c,'at');a=at[1:]
   for key,value in [('Manufacturer',row['manufacturer']),('MPN',row['mpn']),('ProcurementStatus',row['status'])]:
    if any(val(v[1])==key for v in children(c,'property')):raise RuntimeError('existing field review required '+ref+key)
    c.append(['property',q(key),q(value),['at',*a],['effects',['font',['size','1','1']],['hide','yes']]])
   seen[folder].append(ref);changed=True
  if changed:f.write_text(dump(s)+'\n')
 for n in ['mainboard_revD.xml','erc.rpt','erc.log','erc.exit']:
  p=D/folder/n
  if p.exists():p.unlink()
for folder in ['system_master','mainboard_projection']:
 if set(seen[folder])!=set(parts):raise RuntimeError('missing annotated refs '+folder+str(seen))
for name in ['system_ownership.json','C501_C502_BOM_candidate.json','C503_BOM_candidate.json']:shutil.copy2(OLD/name,D/name)
(D/'native_mpn_contract.json').write_text(json.dumps({'status':'NOFAB','parent_manifest_sha256':sha(OLD/'manifest.json'),'gate_candidate_source':str(gate.relative_to(R)),'gate_candidate_sha256':sha(gate),'parts':parts,'net_value_footprint_changes':False},indent=2)+'\n')
print(seen)
