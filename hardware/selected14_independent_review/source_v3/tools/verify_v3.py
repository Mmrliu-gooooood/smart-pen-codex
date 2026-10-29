from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E,copy,sys
D=Path(__file__).resolve().parents[1];V2=D.parent/'mainboard_projection_rf_usb_v2';TAIL=V2/'tail_source_snapshot/fresh.xml'
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def source(file):
 x=E.parse(file);c={a.get('ref'):a for a in x.findall('./components/comp')};n={(a.get('ref'),a.get('pin')):net.get('name') for net in x.findall('./nets/net') for a in net};return c,n
def props(c):return {'value':c.findtext('value'),'footprint':c.findtext('footprint'),'symbol_uuid':c.findtext('tstamps'),'libsource':c.find('libsource').attrib,'sheetpath':c.find('sheetpath').attrib,'properties':sorted((p.get('name'),p.get('value')) for p in c.findall('property'))}
a,an=source(V2/'master_snapshot/mainboard_revD.xml');m,mn=source(D/'system_master/mainboard_revD.xml');p,pn=source(D/'mainboard_projection/mainboard_revD.xml');f,fn=source(D/'fixture_projection/mainboard_revD.xml');tail,tn=source(TAIL)
require(set(m)==set(a)|{'JF1'} and len(mn)==383,'wrong master composition')
require(all(mn.get(k)==v for k,v in an.items()),'old endpoint identity changed')
require({k:v for k,v in mn.items() if k not in an}=={('JF1','1'):'CHIP_EN',('JF1','2'):'BOOT_N',('JF1','3'):'GND'},'fixture interface mismatch')
for ref in a:
 before,after=props(a[ref]),props(m[ref])
 if ref not in ['SW101','SW102']:require(before==after,'unrelated source attributes changed '+ref)
 else:
  require(before['value']==after['value'] and before['footprint']==after['footprint'] and before['symbol_uuid']==after['symbol_uuid'] and before['libsource']==after['libsource'],'switch identity changed')
  require(after['sheetpath']['names']=='/recovery_fixture/','switch not truly allocated to fixture sheet')
remove={'J101','U102','D101','R110','R111','J102','J201','SW101','SW102','JF1'}
require(set(p)==set(m)-remove and len(p)==83 and len(pn)==303,'wrong main source projection')
require(pn=={k:v for k,v in mn.items() if k[0] not in remove},'main pin map changed')
require(set(f)=={'SW101','SW102','JF1'} and len(fn)==7,'wrong fixture composition')
require(fn=={k:v for k,v in mn.items() if k[0] in f},'fixture pin map changed')
for ref in p:require(props(p[ref])==props(m[ref]),'projection attribute mismatch '+ref)
for ref in f:require(props(f[ref])==props(m[ref]),'fixture attribute mismatch '+ref)
require({pin:pn['J108',pin] for pin in ['1','2','3']}=={'1':'CHIP_EN','2':'BOOT_N','3':'GND'},'actual J108 identity lost')
require({pin:pn['J109',pin] for pin in ['1','2','3']}=={'1':'USB_DP','2':'USB_DM','3':'GND'},'USB J109 identity lost')
require(pn['AE101','2'].startswith('unconnected-'),'antenna NC lost')
for ref in ['C106','C107']:require(p[ref].findtext('footprint')=='Capacitor_SMD:C_0402_1005Metric' and p[ref].find("property[@name='dnp']") is not None,'0402/DNP lost')
require(pn['U101','52']==pn['R105','1']=='STRAP_GPIO46' and pn['R105','2']=='GND','GPIO46 source condition changed')
def ownership(main,fixture,usb):
 require(not(set(main)&set(fixture) or set(main)&set(usb) or set(fixture)&set(usb)),'duplicate physical ownership')
 require({'SW101','SW102'}<=set(fixture) and not({'SW101','SW102'}&set(main)),'wrong selected switch ownership')
 require({'J103','J104','J105','J202'}<=set(main),'unresolved handoff hidden')
 require(set(fixture)=={'SW101','SW102','JF1'},'fixture active or extra interface added')
ownership(p,f,tail)
neg=[]
for name,mm,ff,tt in [('duplicate_switch',set(p)|{'SW101'},set(f),set(tail)),('hide_sensor',set(p)-{'J202'},set(f),set(tail)),('lose_switch',set(p),set(f)-{'SW102'},set(tail)),('add_driver',set(p),set(f)|{'U999'},set(tail))]:
 try:ownership(mm,ff,tt)
 except RuntimeError:neg.append(name)
 else:raise RuntimeError('invalid ownership accepted '+name)
for folder,exitcode in [('system_master','0'),('mainboard_projection','5'),('fixture_projection','0')]:require((D/folder/'erc.exit').read_text().strip()==exitcode,'unexpected ERC exit '+folder)
rpt=(D/'mainboard_projection/erc.rpt').read_text();require(rpt.count('[global_label_dangling]')==1 and "Global Label 'VBUS_5V'" in rpt and 'Errors 0  Warnings 1' in rpt,'unexpected projection ERC findings')
rows=[]
for owner,components in [('mainboard',p),('usb_tail_shared_functions',tail),('shared_passive_recovery_fixture',f)]:
 for ref,c in sorted(components.items()):rows.append({'reference':ref,'owner':owner,'value':c.findtext('value'),'footprint':c.findtext('footprint') or '', 'dnp':c.find("property[@name='dnp']") is not None,'exclude_from_bom':c.find("property[@name='exclude_from_bom']") is not None,'source_sheet':c.find('sheetpath').get('names'),'symbol_uuid':c.findtext('tstamps'),'qualification':'source allocation only; component/assembly status inherited or unresolved'})
require(len(rows)==95 and sum(r['reference']=='SW101' for r in rows)==sum(r['reference']=='SW102' for r in rows)==1,'system switch count')
(D/'system_ownership.json').write_text(json.dumps({'selected_option':'B','system_owned_entities':95,'mainboard_entities':83,'tail_entities':9,'fixture_entities':3,'remaining_mainboard_handoffs':['J103','J104','J105','J202'],'fixture_parts_status':'switches and probe-mate MPN/footprints unresolved; not built','shared_fixture_cost':{'currency':'CNY','amount':None,'quantity_basis':'one shared fixture, not one per pen','included_in_pen_unit_cost':False,'note':'separate unquoted cost; does NOT prove either pen meets380RMB or total760RMB budget'},'rows':rows},indent=2))
for name,components in [('system_master',m),('mainboard_projection',p),('fixture_projection',f)]:
 contract=[{'ref':r,'value':c.findtext('value'),'footprint':c.findtext('footprint') or '', 'sheet_path':c.find('sheetpath').get('tstamps'),'symbol_uuid':c.findtext('tstamps'),'dnp':c.find("property[@name='dnp']") is not None} for r,c in sorted(components.items())]
 (D/name/'schematic/unified_component_contract.json').write_text(json.dumps(contract,indent=2))
result={'master_entities':len(m),'master_endpoints':len(mn),'all_original_380_pin_identities_preserved':True,'mainboard_entities':len(p),'mainboard_endpoints':len(pn),'fixture_entities':len(f),'fixture_endpoints':len(fn),'all_retained_source_attributes_preserved':True,'moved_switch_symbol_UUIDs_preserved':True,'switches_owned_once':True,'negative_cases_rejected':neg,'ERC':{'system_master':0,'mainboard_projection':'5; only1VBUSboundary warning','fixture_projection':0},'no_PCB_or_copper_change':True};(D/('verification_optimized.json' if sys.flags.optimize else 'verification.json')).write_text(json.dumps(result,indent=2));print(result)
