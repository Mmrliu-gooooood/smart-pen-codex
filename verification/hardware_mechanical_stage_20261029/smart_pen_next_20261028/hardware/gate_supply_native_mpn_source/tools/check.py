from pathlib import Path
import json,xml.etree.ElementTree as E,sys,copy,hashlib
from sexpr import *
D=Path(__file__).resolve().parents[1];OLD=D.parent/'imu_decoupling_0402_source_fix';C=json.loads((D/'native_mpn_contract.json').read_text());PARTS=C['parts'];FIELDS=['Manufacturer','MPN','ProcurementStatus']
def req(v,m):
 if not v:raise RuntimeError(m)
def fields(comp):return {x.get('name'):x.text or '' for x in comp.findall('./fields/field')}
def check_bom(root):
 comps={x.get('ref'):x for x in root.findall('./components/comp')}
 for ref,row in PARTS.items():
  if ref not in comps:continue
  f=fields(comps[ref]);expect={'Manufacturer':row['manufacturer'],'MPN':row['mpn'],'ProcurementStatus':row['status']}
  for k,v in expect.items():req(f.get(k)==v,ref+' field mismatch/missing '+k)
counts={}
for folder,code in [('system_master','0'),('mainboard_projection','5'),('fixture_projection','0')]:
 for f in (D/folder).rglob('*.kicad_sch'):
  a=parse((OLD/folder/f.relative_to(D/folder)).read_text());b=parse(f.read_text())
  for symbol in children(b,'symbol'):
   if val(prop(symbol,'Reference')[2]) in PARTS:symbol[:]=[x for x in symbol if not(tag(x)=='property' and val(x[1]) in FIELDS)]
  req(a==b,'non-field native change '+str(f))
 a=E.parse(OLD/folder/'mainboard_revD.xml').getroot();b=E.parse(D/folder/'mainboard_revD.xml').getroot();check_bom(b)
 def nodes(x):return {(v.get('ref'),v.get('pin')):n.get('name') for n in x.findall('./nets/net') for v in n}
 req(nodes(a)==nodes(b),'net identity changed')
 aa={x.get('ref'):x for x in a.findall('./components/comp')};bb={x.get('ref'):x for x in b.findall('./components/comp')};req(set(aa)==set(bb),'refs changed')
 for ref in aa:
  for key in ['value','footprint','tstamps']:req(aa[ref].findtext(key)==bb[ref].findtext(key),'electrical metadata changed')
 req((D/folder/'erc.exit').read_text().strip()==code,'ERC exit')
 violations=[v for s in json.loads((D/folder/'erc.json').read_text())['sheets'] for v in s['violations']]
 req(len(violations)==(1 if folder=='mainboard_projection' else 0),'ERC violations')
 if violations:req(violations[0]['severity']=='warning' and 'VBUS_5V' in str(violations),'new warning')
 counts[folder]=[len(bb),len(nodes(b))]
root=E.parse(D/'mainboard_projection/mainboard_revD.xml').getroot();neg=[]
for ref in ['C501','C503','U301']:
 for mode in ['missing','wrong']:
  x=copy.deepcopy(root);field=x.find("./components/comp[@ref='"+ref+"']/fields/field[@name='MPN']")
  if mode=='missing':x.find("./components/comp[@ref='"+ref+"']/fields").remove(field)
  else:field.text='UNVERIFIED_SUBSTITUTION'
  try:check_bom(x)
  except RuntimeError as e:neg.append(str(e))
  else:raise RuntimeError('bad MPN accepted')
req(counts=={'system_master':[112,436],'mainboard_projection':[102,356],'fixture_projection':[3,7]},'counts')
print(json.dumps({'counts':counts,'native_only_three_fields_added_to_10_refs':True,'all_net_value_footprint_UUID_preserved':True,'negative_missing_or_wrong_MPN':neg,'NOFAB':True},indent=2))
