from pathlib import Path
import json,hashlib,shutil,pcbnew as p,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent;H=D.parent;S=H/'rf_width14_selected_board_candidate';I=H/'physical_interface_study'
expected='016d963f764430b6122da29039a5573792e3f0c78078180b18582af69b044c7e'
if hashlib.sha256((S/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest()!=expected:raise ValueError('Baseline changed')
c=json.loads((I/'pin_contract.json').read_text());b=p.LoadBoard(str(S/'mainboard_revD.kicad_pcb'))
# Placement-only branch: copy project rules to expose real copper clearance conflicts.
for name in ['mainboard_revD.kicad_pro','mainboard_revD.kicad_dru']:
 if (S/name).exists():shutil.copyfile(S/name,D/name)
oldrefs={f.GetReference() for f in b.GetFootprints()}
if any(ref in oldrefs for ref in c['ports']):raise ValueError('Expected unimplemented footprint refs')
placements={'J103':(10.25,81.5),'J104':(10,53),'J105':(2,83.5),'J202':(7,90.5),'J110':(1.5,80.25)}
rows=[]
for ref,pt in placements.items():
 v=c['ports'][ref];f=p.FootprintLoad(str(I/'SmartPenInterfaces.pretty'),v['fp']);b.Add(f);f.SetReference(ref);f.SetValue(v['value']);f.SetFPID(p.LIB_ID('SmartPenInterfaces',v['fp']));f.SetPosition(p.VECTOR2I(*(round(z*1e6) for z in pt)));f.Flip(f.GetPosition(),False)
 if ref in ['J105','J110']:
  f.Rotate(f.GetPosition(),p.EDA_ANGLE(90,p.DEGREES_T));f.Reference().SetLayer(p.B_Fab)
 for a in f.Pads():
  if a.GetNumber():
   name=v['nets'][int(a.GetNumber())-1];net=b.FindNet(name)
   if not net or net.GetNetCode()==0:raise ValueError('No existing source net '+name)
   a.SetNet(net)
 rows.append({'ref':ref,'side':'B.Cu','signal_origin_mm':pt,'native_orientation_deg':f.GetOrientationDegrees(),'pads':[{'pin':a.GetNumber(),'net':a.GetNetname(),'xy':[a.GetPosition().x/1e6,a.GetPosition().y/1e6]} for a in f.Pads()]})
V=H/'mainboard_interface_allocation_v4/mainboard_projection'
for file in V.rglob('*'):
 if file.is_file() and (file.suffix in ['.kicad_sch','.kicad_sym','.kicad_mod'] or file.name in ['sym-lib-table','fp-lib-table','mainboard_revD.xml'] or 'schematic' in file.relative_to(V).parts):
  dest=D/file.relative_to(V);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(file,dest)
x=E.parse(D/'mainboard_revD.xml');cs={z.get('ref'):z for z in x.findall('./components/comp')}
root='cebe562b-54ce-58d7-a4f0-094e70dd7d0a'
for f in b.GetFootprints():
 z=cs[f.GetReference()];f.SetPath(p.KIID_PATH('/'+root+z.find('sheetpath').get('tstamps')+z.findtext('tstamps')))
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(D/'mainboard_revD.kicad_pcb'),b)
(D/'placement_delta.json').write_text(json.dumps({'status':'PRELAYOUT_WITH_V4_SOURCE_NOT_ROUTED','source_board_sha256':expected,'new_footprints':rows,'old_copper_modified':False,'old_components_modified':False,'source_v4_pending':False},indent=2)+'\n')
