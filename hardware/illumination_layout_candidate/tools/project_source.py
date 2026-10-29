from pathlib import Path
import json,re,shutil,hashlib
D=Path(__file__).resolve().parents[1];S=D.parent/'illumination_driver'
s=(S/'illumination_NOFAB.kicad_sch').read_text();tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s);stack=[]
for t in tokens:
 if t=='(':
  x=[]
  if stack:stack[-1].append(x)
  else:root=x
  stack.append(x)
 elif t==')':stack.pop()
 else:stack[-1].append(t)
def prop(x,key):return next((a for a in x if isinstance(a,list) and a[:2]==['property',json.dumps(key)]),None)
fp={'J1':'SmartPenIllum:WireLands_3_P2.5_AssemblyUnqualified','J2':'SmartPenIllum:WireLands_2_P2.5_AssemblyUnqualified','JP1':'Jumper:SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm','Q1':'Package_TO_SOT_SMD:SOT-23'}
changes=[]
for x in root:
 if isinstance(x,list) and x[0]=='symbol' and prop(x,'Reference'):
  r=json.loads(prop(x,'Reference')[2]);f=prop(x,'Footprint')
  if r in fp:changes.append({'ref':r,'before':json.loads(f[2]),'after':fp[r]});f[2]=json.dumps(fp[r])
def dump(x):return '('+' '.join(map(dump,x))+')' if isinstance(x,list) else x
(D/'illumination_NOFAB.kicad_sch').write_text(dump(root));shutil.copy2(S/'Illumination.kicad_sym',D/'Illumination.kicad_sym');shutil.copy2(S/'sym-lib-table',D/'sym-lib-table')
(D/'source_projection_contract.json').write_text(json.dumps({'upstream_schematic_sha256':hashlib.sha256(s.encode()).hexdigest(),'only_changes':changes,'circuit_values_and_pins_unchanged':True,'unqualified':'SOT23 library candidate not exact official landpattern; wire lands no connector/strain qualification'},indent=2))
(D/'fp-lib-table').write_text('(fp_lib_table (lib (name "SmartPenIllum")(type "KiCad")(uri "${KIPRJMOD}/SmartPenIllum.pretty")(options "")(descr "NOFAB engineering wire lands")))')

# Bundle exact used library footprints so checks do not depend on a global table.
table=['(fp_lib_table (lib (name "SmartPenIllum")(type "KiCad")(uri "${KIPRJMOD}/SmartPenIllum.pretty")(options "")(descr "NOFAB wire lands"))']
for lib,name in [('Package_TO_SOT_SMD','SOT-23'),('Resistor_SMD','R_0603_1608Metric'),('Jumper','SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm')]:
 folder=D/'library_snapshots'/(lib+'.pretty');folder.mkdir(parents=True,exist_ok=True);shutil.copy2(Path('/usr/share/kicad/footprints')/(lib+'.pretty')/(name+'.kicad_mod'),folder/(name+'.kicad_mod'))
 table.append('(lib (name "'+lib+'")(type "KiCad")(uri "${KIPRJMOD}/library_snapshots/'+lib+'.pretty")(options "")(descr "Exact used KiCad candidate snapshot; not manufacturer approval"))')
(D/'fp-lib-table').write_text(''.join(table)+')')
