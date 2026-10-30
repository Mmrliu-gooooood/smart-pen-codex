from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
roots=['hardware/gate_input_local_routing','hardware/gate_input_independent_review','hardware/imu_compact_0402_placement','hardware/gate_supply_native_mpn_source']
packages={}
for n in roots:
 p=R/n;raw=json.loads((p/'manifest.json').read_text());m=raw.get('files',raw)
 for rel,h in m.items():
  expected=h['sha256'] if isinstance(h,dict) else h
  if not isinstance(expected,str) or len(expected)!=64:raise RuntimeError('unsupported manifest member '+rel)
  if sha(p/rel)!=expected:raise RuntimeError('bad frozen member '+n+'/'+rel)
 packages[n]={'manifest_sha256':sha(p/'manifest.json'),'members':len(m),'mode':'complete manifest plus all listed members; no recursive ancestor builders executed'}
extras=['hardware/camera_power_gate_placement_study/bom_candidates.json','hardware/imu_decoupling_c503_source_fix/manufacturer_basis_snapshot.md','hardware/imu_decoupling_c503_source_fix/manifest.json']
for package in ['docs/electronics/imu_decoupling_correction','docs/electronics/imu_0402_decoupling_candidate']:
 extras.append(package+'/manifest.json');extras += [package+'/'+n for n in json.loads((R/package/'manifest.json').read_text())]
old='hardware/imu_decoupling_c503_source_fix/manufacturer_basis_snapshot.md';bom=json.loads((R/'hardware/gate_supply_native_mpn_source/C503_BOM_candidate.json').read_text())
if sha(R/old)!=bom['dimension_evidence']['source_sha256']:raise RuntimeError('missing original C503 evidence')
omitted={n:sha(R/n) for n in extras if Path(n).suffix in ['.pdf','.png']};extras=[n for n in extras if n not in omitted]
c={'status':'NOFAB_135_54_0_JP301_OPEN','complete_current_verification_packages':packages,'external_evidence_not_in_publication':omitted,'external_omission_policy':'Vendor PDF/page images kept local only; public bundle uses original SHA, official URL and summary. Text-only provenance packages are partial, not falsely complete.','external_provenance_allowlist':{n:sha(R/n) for n in extras},'historical_path_resolution':[{'contract':'hardware/gate_supply_native_mpn_source/C503_BOM_candidate.json','field':'dimension_evidence','original_recorded_path':bom['dimension_evidence']['source_path'],'sha256':bom['dimension_evidence']['source_sha256'],'immutable_content_at':old,'note':'Old README version preserved byte-for-byte here; current README is later supplemented with actual bias graph. Do not overwrite either or equate hashes.'}],'reproduction_scope':'Fresh native current-board ERC/DRC, gate audit/negative/config checks and frozen source_rules checks. Not recursive regeneration of all ancestors or bit-identical random-UUID route generation.','do_not_collect':['hardware/gate_control_output_routing','unlisted prl/cache/failed trials'],'tools_required':['KiCad 9.0.2 CLI, pcbnew and installed standard libraries','Python 3; native package same-basename pro/dru/source and custom libraries','writable isolated XDG dirs'],'historical_manifest_partial_collection':'Only old C503 manifest plus specified snapshot are provenance evidence, not claimed as a complete old source package.'}
(D/'closure.json').write_text(json.dumps(c,indent=2)+'\n')
print(sum(v['members'] for v in packages.values()),len(extras))
