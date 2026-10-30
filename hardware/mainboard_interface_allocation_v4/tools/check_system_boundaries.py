from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E,copy,sys
D=Path(__file__).resolve().parents[1];R=D.parents[1];H=R/'hardware';V3=H/'mainboard_fixture_allocation_v3';I=H/'physical_interface_study'
def req(ok,msg):
 if not ok:raise RuntimeError(msg)
def read(path):
 x=E.parse(path);return {c.get('ref'):c for c in x.findall('./components/comp')},{(a.get('ref'),a.get('pin')):n.get('name') for n in x.findall('./nets/net') for a in n}
main,mn=read(D/'mainboard_projection/mainboard_revD.xml');ledger=json.loads((V3/'system_ownership.json').read_text());rows=ledger['rows']
for row in rows:
 if row['owner']=='mainboard':
  c=main[row['reference']];row.update(value=c.findtext('value'),footprint=c.findtext('footprint') or '',source_sheet=c.find('sheetpath').get('names'))
c=main['J110'];rows.append({'reference':'J110','owner':'mainboard','value':c.findtext('value'),'footprint':c.findtext('footprint'),'source_sheet':c.find('sheetpath').get('names'),'symbol_uuid':c.findtext('tstamps'),'qualification':'physical port source only; placement/routing/mechanics independently gated'})
req(len(rows)==96 and sum(r['reference']=='SW101' for r in rows)==sum(r['reference']=='SW102' for r in rows)==1,'ownership duplication')
ledger.update(system_owned_entities=96,mainboard_entities=84,remaining_mainboard_handoffs=['J103','J104','J105','J202','J110'],physical_interface_status='5 ports now native physical source, NOT proof placed/routed/assembled',rows=rows)
ledger['scope']='mainboard + selected USB tail + passive fixture only. Separate existing system blocks below remain unmerged native sources, with their original namespaced identities. Not a complete purchasable system BOM.'
blocks={}
for rel,sha in json.loads((I/'system_block_source_hashes.json').read_text()).items():
 p=(R/rel).resolve();req(hashlib.sha256(p.read_bytes()).hexdigest()==sha,'external block changed '+rel);cc,nn=read(p)
 key='pickup_contact' if 'pickup_contact' in rel else 'battery_adc_candidate' if 'battery_adc_candidate' in rel else 'camera_power_gate'
 blocks[key]={'existing_source':rel,'sha256':sha,'native_components':[{'identity':key+':'+ref,'reference':ref,'value':c.findtext('value'),'footprint':c.findtext('footprint') or ''} for ref,c in sorted(cc.items())],'status':'existing separate source candidate; not integrated mainboard layout; namespace preserves original reference identity'}
 blocks[key]['netmap']=nn
links=[]
for i in range(1,7):
 req(mn['J103',str(i)]==blocks['pickup_contact']['netmap']['J1',str(i)],'pickup identity')
 links.append({'main':['J103',str(i),mn['J103',str(i)]],'block':['pickup_contact','J1',str(i),blocks['pickup_contact']['netmap']['J1',str(i)]],'status':'source identity exact; harness unassembled'})
for i in [1,2]:
 req(mn['J105',str(i)]==blocks['battery_adc_candidate']['netmap']['J2',str(i)],'ADC identity')
 links.append({'main':['J105',str(i),mn['J105',str(i)]],'block':['battery_adc_candidate','J2',str(i),blocks['battery_adc_candidate']['netmap']['J2',str(i)]],'status':'safe frontend output only; JP1/JP2 remain OPEN, hardware PG unqualified'})
# Power candidate has NO physical input connector. Exact endpoint references are not connector substitutions.
for pin,ref,bpin,bnet in [('1','U1','1','/3V3_AON'),('2','U1','2','/GND'),('3','R2','1','/CAM_PWR_EN')]:
 req(blocks['camera_power_gate']['netmap'][ref,bpin]==bnet and '/'+mn['J110',pin]==bnet,'power identity')
 links.append({'main':['J110',pin,mn['J110',pin]],'block':['camera_power_gate',ref,bpin,bnet],'status':'semantic receiving net verified; NO physical power-board input landing implemented/approved; cannot wire to unknown module','explicit_sheet_local_alias':bnet+' = '+mn['J110',pin]})
req(blocks['camera_power_gate']['netmap']['JP1','1']=='/CAM_3V3_PRELINK' and blocks['camera_power_gate']['netmap']['JP1','2']=='/CAM_3V3_SW','gate bridge identity')
for b in blocks.values():b.pop('netmap')
ledger['separate_unintegrated_blocks']=blocks
(D/'system_ownership.json').write_text(json.dumps(ledger,indent=2));(D/'cross_board_map.json').write_text(json.dumps({'links':links,'J104':'camera-off UART service only; no external power; probe jig not qualified','J202':'see pin_contract exact18→24 migration and new customflex only; unknown30pin module prohibited','unresolved_other_block_supplies':['pickup3V3 fromJ103 candidate must be power-budgeted','ADC J1 protectedpack/J3AON/J4hardwarePG are existing block dependencies, NOT connected by J105','power gate lacks physical inputconnector/verified headregulators; JP1 remains OPEN'],'block_source_versions':blocks},indent=2))
print('PASS 6 pickup +2 safeADC +3 gate semantic endpoints; gate physical input explicitly unresolved;96 main/tail/fixture entities plus separately scoped existing blocks')
