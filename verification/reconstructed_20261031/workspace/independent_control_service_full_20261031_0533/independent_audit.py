from pathlib import Path
import json,re,hashlib,collections,xml.etree.ElementTree as ET
D=Path(__file__).resolve().parent;A=D/'native';B=D/'final_candidate';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def blocks(s):
 dep=0;q=False;esc=False;start=0
 for i,c in enumerate(s):
  if q:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':q=False
  elif c=='"':q=True
  elif c=='(':
   dep+=1
   if dep==2:start=i
  elif c==')':
   if dep==2:yield s[start:i+1]
   dep-=1
def idx(f):
 out={}
 for b in blocks(f.read_text()):
  m=re.search(r'\(uuid "([^"]+)"\)',b)
  if m:
   assert m.group(1)not in out,'duplicate UUID';out[m.group(1)]=b
 return out
a,b=idx(A/'mainboard_revD.kicad_pcb'),idx(B/'mainboard_revD.kicad_pcb');changes=[]
for u,t in a.items():
 if u in b and b[u]!=t:
  kind=t.split()[0][1:];ref=re.search(r'\(property "Reference" "([^"]+)"',t);changes.append({'uuid':u,'kind':kind,'ref':ref.group(1)if ref else None})
assert {r['ref']for r in changes if r['kind']=='footprint'}==set();assert all(r['kind']in['zone']for r in changes)
assert len(set(a)-set(b))==0 and len(set(b)-set(a))==483
source={str(f.relative_to(A)):sha(f)for f in A.rglob('*')if f.is_file()};assert len(source)==53;assert all(sha(B/f)==h for f,h in source.items()if f!='mainboard_revD.kicad_pcb')
def pinmap(f):
 x=ET.parse(f).getroot();return{(n.get('ref'),n.get('pin')):(net.get('name'),n.get('pinfunction'))for net in x.findall('./nets/net')for n in net.findall('node')}
assert pinmap(D/'independent_netlist.xml')==pinmap(D/'review_dependencies/source_netlist.xml')
v=json.loads((D/'final_verification.json').read_text());r={'raw_UUIDs_unique':True,'raw_changed_retained_blocks':changes,'raw_added_blocks':483,'raw_removed_blocks':0,'all_52_nonPCB_native_source_files_byte_equal':True,'fresh_netlist_pin_net_function_map_equal':True,'sha256':sha(B/'mainboard_revD.kicad_pcb')};(D/'independent_audit.json').write_text(json.dumps(r,indent=2))

values={c.get('ref'):c.findtext('value')for c in ET.parse(D/'independent_netlist.xml').findall('./components/comp')};assert values['U203']=='SN74AXC4T245PWR';assert all(values[x]=='100k 1%'for x in ['R222','R223']);r['fresh_values_verified']={x:values[x]for x in ['U203','R222','R223']};(D/'independent_audit.json').write_text(json.dumps(r,indent=2))

mp=pinmap(D/'independent_netlist.xml');assert mp[('U101','49')]==('CAM_RESET_UART_TX','GPIO43_U0TXD') and mp[('U101','50')]==('CAM_PWDN_UART_RX','GPIO44_U0RXD');assert mp[('U101','46')]==('3V3_AON','VDD3P3_CPU');r['fresh_GPIO43_GPIO44_CPU_domain_supply_verified']=True;(D/'independent_audit.json').write_text(json.dumps(r,indent=2))
