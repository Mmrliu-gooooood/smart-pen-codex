from pathlib import Path
import shutil,json,hashlib,uuid,copy,collections
from sexpr import *
D=Path(__file__).resolve().parents[1];H=D.parent;OLD=H/'mainboard_projection_rf_usb_v2/master_snapshot';M=D/'system_master';P=D/'mainboard_projection';F=D/'fixture_projection';ROOT='cebe562b-54ce-58d7-a4f0-094e70dd7d0a';uid=lambda:str(uuid.uuid4());fixture_sheet=uid()
if any(p.exists() for p in [M,P,F]):raise RuntimeError('v3 exists; do not overwrite')
manifest=json.loads((H/'mainboard_projection_rf_usb_v2/manifest.json').read_text())
for k,v in manifest.items():
 file=H/'mainboard_projection_rf_usb_v2'/k
 if hashlib.sha256(file.read_bytes()).hexdigest()!=v:raise RuntimeError('v2 frozen input altered '+k)
shutil.copytree(OLD,M)
def xy(a):return tuple(round(float(v),6) for v in a[1:3])
def pins(c,libs):
 at=child(c,'at')
 if float(at[3])!=0:raise RuntimeError('unsupported rotation')
 return [(round(float(at[1])+float(child(p,'at')[1]),6),round(float(at[2])-float(child(p,'at')[2]),6)) for g in children(libs[val(child(c,'lib_id')[1])],'symbol') for p in children(g,'pin')]
def drop_instances(s,refs):
 libs={val(c[1]):c for c in children(child(s,'lib_symbols') or [],'symbol')};syms=children(s,'symbol');target=[c for c in syms if val(prop(c,'Reference')[2]) in refs];edges=collections.defaultdict(set)
 for w in children(s,'wire'):
  points=[xy(v) for v in children(child(w,'pts'),'xy')]
  if len(points)!=2:raise RuntimeError('wire not segment')
  a,b=points;edges[a].add(b);edges[b].add(a)
 seen=set();queue=[p for c in target for p in pins(c,libs)]
 while queue:
  pt=queue.pop()
  if pt not in seen:seen.add(pt);queue.extend(edges[pt]-seen)
 for c in syms:
  if c not in target and set(pins(c,libs))&seen:raise RuntimeError('shared physical wire branch')
 removed=[]
 for c in s:
  if c in target or (tag(c)=='wire' and any(xy(a) in seen for a in children(child(c,'pts'),'xy'))) or (tag(c) in ['global_label','label','no_connect','junction'] and xy(child(c,'at')) in seen):removed.append(c)
 s[:]=[c for c in s if c not in removed]
 return target,removed
source=parse((M/'schematic/mcu_core.kicad_sch').read_text());defs={val(c[1]):c for c in children(child(source,'lib_symbols'),'symbol')};switches,removed=drop_instances(source,{'SW101','SW102'})
if {val(prop(c,'Reference')[2]) for c in switches}!={'SW101','SW102'}:raise RuntimeError('switch removal mismatch')
(M/'schematic/mcu_core.kicad_sch').write_text(dump(source)+'\n')
fixture=['kicad_sch',['version','20250114'],['generator',q('eeschema')],['uuid',fixture_sheet],['paper',q('A3')],['title_block',['title',q('SELECTED PASSIVE RECOVERY FIXTURE / IMPLEMENTATION CANDIDATE NOFAB')],['rev',q('F1_ALLOCATION_ONLY')]],['lib_symbols',copy.deepcopy(defs['MCU:SW_NO']),copy.deepcopy(defs['MCU:PORT3'])]]
for c,x,y in [(switches[0],63.5,50.8),(switches[1],139.7,50.8)]:
 c=copy.deepcopy(c);oldx,oldy=xy(child(c,'at'));child(c,'at')[1:3]=[str(x),str(y)]
 for pr in children(c,'property'):
  a=child(pr,'at');a[1:3]=[str(float(a[1])+x-oldx),str(float(a[2])+y-oldy)]
 path=child(child(child(c,'instances'),'project'),'path');path[1]=q('/'+ROOT+'/'+fixture_sheet);fixture.append(c)
port=copy.deepcopy(next(c for c in children(source,'symbol') if val(prop(c,'Reference')[2])=='J108'));ref='JF1';x,y=101.6,101.6;oldx,oldy=xy(child(port,'at'));child(port,'uuid')[1]=uid();child(port,'at')[1:3]=[str(x),str(y)]
for pr in children(port,'property'):
 a=child(pr,'at');a[1:3]=[str(float(a[1])+x-oldx),str(float(a[2])+y-oldy)]
prop(port,'Reference')[2]=q(ref);prop(port,'Value')[2]=q('J108_PASSIVE_PROBE_MATE_UNQUALIFIED');prop(port,'Footprint')[2]=q('')
for pin in children(port,'pin'):child(pin,'uuid')[1]=uid()
path=child(child(child(port,'instances'),'project'),'path');path[1]=q('/'+ROOT+'/'+fixture_sheet);child(path,'reference')[1]=q(ref);fixture.append(port)
for c in children(fixture,'symbol'):
 ref=val(prop(c,'Reference')[2]);at=child(c,'at');mapping={'1':'CHIP_EN','2':'GND'} if ref=='SW101' else {'1':'BOOT_N','2':'GND'} if ref=='SW102' else {'1':'CHIP_EN','2':'BOOT_N','3':'GND'}
 for group in children(defs[val(child(c,'lib_id')[1])],'symbol'):
  for pin in children(group,'pin'):
   local=child(pin,'at');px=float(at[1])+float(local[1]);py=float(at[2])-float(local[2]);angle=180 if float(local[1])<0 else 0;net=mapping[val(child(pin,'number')[1])]
   fixture.append(parse(f'(global_label "{net}" (shape bidirectional) (at {px} {py} {angle}) (effects (font (size 0.9 0.9)) (justify right)) (uuid {uid()}) (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {px} {py} 0) (effects (font (size 1 1)) hide)))'))
(M/'schematic/recovery_fixture.kicad_sch').write_text(dump(fixture)+'\n')
r=parse((M/'mainboard_revD.kicad_sch').read_text());sheet=copy.deepcopy(children(r,'sheet')[0]);child(sheet,'uuid')[1]=fixture_sheet;oldx,oldy=xy(child(sheet,'at'));child(sheet,'at')[1:3]=['40','225'];prop(sheet,'Sheetname')[2]=q('recovery_fixture');prop(sheet,'Sheetfile')[2]=q('schematic/recovery_fixture.kicad_sch')
for pr in children(sheet,'property'):
 a=child(pr,'at');a[2]=str(float(a[2])+225-oldy)
r.append(sheet);(M/'mainboard_revD.kicad_sch').write_text(dump(r)+'\n')
shutil.copytree(M,P);shutil.copytree(M,F)
pr=copy.deepcopy(r);pr[:]=[c for c in pr if not(tag(c)=='sheet' and val(prop(c,'Sheetname')[2])=='recovery_fixture')];(P/'mainboard_revD.kicad_sch').write_text(dump(pr)+'\n')
removed_main={}
for file in (P/'schematic').glob('*.kicad_sch'):
 if file.name=='recovery_fixture.kicad_sch':continue
 s=parse(file.read_text());targets,nodes=drop_instances(s,{'J101','U102','D101','R110','R111','J102','J201'})
 if targets:removed_main[file.name]=[val(prop(c,'Reference')[2]) for c in targets];file.write_text(dump(s)+'\n')
fr=copy.deepcopy(r);fr[:]=[c for c in fr if not(tag(c)=='sheet' and val(prop(c,'Sheetname')[2])!='recovery_fixture')];(F/'mainboard_revD.kicad_sch').write_text(dump(fr)+'\n')
# Stale generated metadata belongs to the captured v2 source, not the newly allocated sources.
for folder in [M,P,F]:
 for name in ['mainboard_revD.xml','fresh.xml','component_allocation.json','schematic/unified_component_contract.json']:
  file=folder/name
  if file.exists():file.unlink()
(D/'design_change.json').write_text(json.dumps({'decision':'Root selected prototype option B: J108 mainboard probes + external passive fixture','parent_v2_manifest_sha256':hashlib.sha256((H/'mainboard_projection_rf_usb_v2/manifest.json').read_bytes()).hexdigest(),'root_uuid_preserved':ROOT,'fixture_sheet_uuid':fixture_sheet,'moved_refs':['SW101','SW102'],'moved_symbol_uuids_preserved':[val(child(c,'uuid')[1]) for c in switches],'new_ref':'JF1','no_PCB_or_copper_modified':True,'mainboard_remove_only_allocated':removed_main,'remaining_physical_handoffs':['J103','J104','J105','J202'],'fixture_status':'selected allocation; switch/probe MPN, mechanics, ESD and assembly/test still unqualified'},indent=2))
print('v3 native allocation created; no PCB written')
