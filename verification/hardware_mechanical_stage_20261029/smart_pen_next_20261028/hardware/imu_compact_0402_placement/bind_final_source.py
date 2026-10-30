from pathlib import Path
import pcbnew as p,xml.etree.ElementTree as E,shutil,json,hashlib
D=Path(__file__).resolve().parent;S=D.parent/'imu_decoupling_0402_source_fix/mainboard_projection'
for f in S.rglob('*'):
 if f.is_file()and(f.suffix in ['.kicad_sch','.kicad_sym','.kicad_mod']or f.name=='sym-lib-table'):
  q=D/f.relative_to(S);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,q)
r=E.parse(S/'mainboard_revD.xml');cs={c.get('ref'):c for c in r.findall('./components/comp')};b=p.LoadBoard(str(D/'mainboard_revD.kicad_pcb'))
for f in b.GetFootprints():
 c=cs[f.GetReference()];f.SetValue(c.findtext('value'));f.SetPath(p.KIID_PATH('/cebe562b-54ce-58d7-a4f0-094e70dd7d0a'+c.find('sheetpath').get('tstamps')+c.findtext('tstamps')))
p.SaveBoard(str(D/'mainboard_revD.kicad_pcb'),b)
(D/'source_binding.json').write_text(json.dumps({'source':'hardware/imu_decoupling_0402_source_fix/mainboard_projection','manifest_sha256':hashlib.sha256((S.parent/'manifest.json').read_bytes()).hexdigest(),'C501_C502':'KEMET C0402C104K4RACTU','C503':'KEMET C0805C106K8RACTU','manufacturing_approved':False,'effective_capacitance_guaranteed':False},indent=2))
