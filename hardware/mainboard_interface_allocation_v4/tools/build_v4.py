from pathlib import Path
import json,shutil,hashlib,uuid,copy,collections
from sexpr import *
D=Path(__file__).resolve().parents[1];H=D.parent;OLD=H/'mainboard_fixture_allocation_v3';I=H/'physical_interface_study';ROOT='cebe562b-54ce-58d7-a4f0-094e70dd7d0a';uid=lambda:str(uuid.uuid4())
for folder in [OLD,I]:
 manifest=json.loads((folder/'manifest.json').read_text())
 for k,v in manifest.get('files',manifest).items():
  if hashlib.sha256((folder/k).read_bytes()).hexdigest()!=v:raise RuntimeError('frozen input changed '+k)
if (D/'system_master').exists():raise RuntimeError('do not overwrite')
# Reuse audited connected-stub removal, without running the old builder.
code=(OLD/'tools/build_v3.py').read_text();exec(code[code.index('def xy('):code.index('source=parse(')])
for name in ['system_master','mainboard_projection','fixture_projection']:shutil.copytree(OLD/name,D/name)
original={};sheet_id=uid()
for name in ['system_master','mainboard_projection']:
 folder=D/name
 for file in (folder/'schematic').glob('*.kicad_sch'):
  s=parse(file.read_text());targets,nodes=drop_instances(s,{'J103','J104','J105','J202'})
  if targets:
   for c in targets:original[val(prop(c,'Reference')[2])]=val(child(c,'uuid')[1])
   file.write_text(dump(s)+'\n')
 new=parse((I/'physical_interfaces.kicad_sch').read_text());child(new,'uuid')[1]=sheet_id
 for c in children(new,'symbol'):
  ref=val(prop(c,'Reference')[2])
  if ref in original:child(c,'uuid')[1]=original[ref]
  child(c,'instances')[:]=['instances',['project',q('mainboard_revD'),['path',q('/'+ROOT+'/'+sheet_id),['reference',q(ref)],['unit','1']]]]
 (folder/'schematic/physical_interfaces.kicad_sch').write_text(dump(new)+'\n')
 r=parse((folder/'mainboard_revD.kicad_sch').read_text());sheet=copy.deepcopy(children(r,'sheet')[0]);child(sheet,'uuid')[1]=sheet_id
 oldx,oldy=xy(child(sheet,'at'));child(sheet,'at')[1:3]=['220','225'];prop(sheet,'Sheetname')[2]=q('physical_interfaces');prop(sheet,'Sheetfile')[2]=q('schematic/physical_interfaces.kicad_sch')
 for pr in children(sheet,'property'):
  a=child(pr,'at');a[1]=str(float(a[1])+220-oldx);a[2]=str(float(a[2])+225-oldy)
 r.append(sheet);(folder/'mainboard_revD.kicad_sch').write_text(dump(r)+'\n')
 shutil.copy2(I/'SmartPenInterfaces.kicad_sym',folder/'SmartPenInterfaces.kicad_sym');shutil.copytree(I/'SmartPenInterfaces.pretty',folder/'SmartPenInterfaces.pretty')
 for table in ['sym-lib-table','fp-lib-table']:
  t=parse((folder/table).read_text());it=parse((I/table).read_text());t.extend(copy.deepcopy(children(it,'lib')));(folder/table).write_text(dump(t)+'\n')
for name in ['system_master','mainboard_projection','fixture_projection']:
 folder=D/name
 for f in ['mainboard_revD.xml','erc.rpt','erc.exit','erc.log','schematic/unified_component_contract.json']:
  if (folder/f).exists():(folder/f).unlink()
(D/'pin_contract.json').write_bytes((I/'pin_contract.json').read_bytes())
(D/'design_change.json').write_text(json.dumps({'parent_v3_manifest_sha256':hashlib.sha256((OLD/'manifest.json').read_bytes()).hexdigest(),'interface_manifest_sha256':hashlib.sha256((I/'manifest.json').read_bytes()).hexdigest(),'changed_ports':['J103','J104','J105','J202'],'new_port':'J110','preserved_original_symbol_UUIDs':original,'new_sheet_uuid':sheet_id,'migration':'J202 by exact net identity:18 logical to24 physical, NOT numerical mapping','no_PCB_write':True,'unknown_custom30pin':'isolated; no direct connection; not replaced by this24pin contract','external_blocks':'existing standalone block identity retained; not merged/routed or claimed integrated'},indent=2))
print('v4 created')
