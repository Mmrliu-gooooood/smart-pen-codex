from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E,copy,sys
D=Path(__file__).resolve().parents[1];H=D.parent;OLD=H/'mainboard_fixture_allocation_v3';contract=json.loads((D/'pin_contract.json').read_text())
def req(ok,msg):
 if not ok:raise RuntimeError(msg)
def source(file):
 x=E.parse(file);return {c.get('ref'):c for c in x.findall('./components/comp')},{(a.get('ref'),a.get('pin')):n.get('name') for n in x.findall('./nets/net') for a in n}
def props(c):return {'value':c.findtext('value'),'fp':c.findtext('footprint'),'uuid':c.findtext('tstamps'),'lib':c.find('libsource').attrib,'sheet':c.find('sheetpath').attrib,'properties':sorted((p.get('name'),p.get('value')) for p in c.findall('property'))}
def check_ports(n):
 for ref,v in contract['ports'].items():req({pin:net for (r,pin),net in n.items() if r==ref}=={str(i+1):net for i,net in enumerate(v['nets'])},'port mismatch '+ref)
a,an=source(OLD/'system_master/mainboard_revD.xml');m,mn=source(D/'system_master/mainboard_revD.xml');p,pn=source(D/'mainboard_projection/mainboard_revD.xml');f,fn=source(D/'fixture_projection/mainboard_revD.xml');af,afn=source(OLD/'fixture_projection/mainboard_revD.xml')
req(set(m)==set(a)|{'J110'},'master refs');req(len(m)==94 and len(mn)==392,'master count');req(len(p)==84 and len(pn)==312,'projection count');check_ports(mn);check_ports(pn)
req({k:v for k,v in mn.items() if k[0] not in {'J202','J110'}}=={k:v for k,v in an.items() if k[0]!='J202'},'unrelated endpoint changed')
for row in contract['J202_semantic_migration']['explicit_rows']:
 req(an['J202',row['old_pin']]==row['old_net']==row['new_net'],'migration source')
 for pin in row['new_pins']:req(mn['J202',pin]==row['old_net'],'migration destination')
for ref in a:
 before,after=props(a[ref]),props(m[ref])
 if ref not in contract['ports']:req(before==after,'unrelated metadata '+ref)
 else:req(before['uuid']==after['uuid'],'old port symbol identity lost '+ref)
for ref,v in contract['ports'].items():req(m[ref].findtext('footprint')=='SmartPenInterfaces:'+v['fp'] and m[ref].findtext('value')==v['value'],'port physical source '+ref)
remove={'J101','U102','D101','R110','R111','J102','J201','SW101','SW102','JF1'}
req(set(p)==set(m)-remove,'projection allocation');req(pn=={k:v for k,v in mn.items() if k[0] not in remove},'projection net map')
for ref in p:req(props(p[ref])==props(m[ref]),'projection metadata '+ref)
req(fn==afn and set(f)==set(af),'fixture changed')
for ref in f:req(props(f[ref])==props(af[ref]),'fixture identity changed')
neg=[]
for name,mutation in [('numeric_18_to24',lambda n:n.update({('J202',str(i)):an['J202',str(i)] for i in range(1,19)})),('J110_raw_camera',lambda n:n.update({('J110','1'):'CAM_3V3_SW'})),('ADC_raw_battery',lambda n:n.update({('J105','1'):'PROTECTED_VBAT'})),('lost_ground',lambda n:n.pop(('J202','24')))]:
 n=copy.deepcopy(pn);mutation(n)
 try:check_ports(n)
 except RuntimeError:neg.append(name)
 else:raise RuntimeError('bad contract accepted '+name)
for name,expected in [('system_master','0'),('mainboard_projection','5'),('fixture_projection','0')]:req((D/name/'erc.exit').read_text().strip()==expected,'ERC status')
r=(D/'mainboard_projection/erc.rpt').read_text();req(r.count('[global_label_dangling]')==1 and "Global Label 'VBUS_5V'" in r and 'Errors 0  Warnings 1' in r,'projection warnings')
for name,cc in [('system_master',m),('mainboard_projection',p),('fixture_projection',f)]:
 (D/name/'schematic/unified_component_contract.json').write_text(json.dumps([{'ref':ref,'value':c.findtext('value'),'footprint':c.findtext('footprint') or '', 'sheet_path':c.find('sheetpath').get('tstamps'),'symbol_uuid':c.findtext('tstamps'),'dnp':c.find("property[@name='dnp']") is not None} for ref,c in sorted(cc.items())],indent=2))
result={'master':[len(m),len(mn)],'mainboard':[len(p),len(pn)],'fixture':[len(f),len(fn)],'all_unrelated_pin_nets_and_metadata_preserved':True,'old4port_UUIDs_preserved':True,'J202_semantic_migration_verified':18,'negative_tests_rejected':neg,'ERC':{'system':0,'mainboard':'exit5 only VBUS boundary warning','fixture':0},'PCB_parity':'not measured by this source-only artifact'}
(D/('verification_optimized.json' if sys.flags.optimize else 'verification.json')).write_text(json.dumps(result,indent=2));print(result)
