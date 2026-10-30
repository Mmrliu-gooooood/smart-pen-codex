#!/usr/bin/env python3
import csv,json,hashlib,collections,xml.etree.ElementTree as ET
from pathlib import Path
import pcbnew
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
MECH=ROOT.parent/'smart_pen_mechanics_next_20261028/mechanical/contact_oblique_harness_revC_0038'
SOURCES={
 'mainboard':('hardware/gate_supply_native_mpn_source/mainboard_projection/mainboard_revD.xml','hardware/imu_compact_0402_placement/mainboard_revD.kicad_pcb'),
 'power':('hardware/power14_single_feed_revB/power_integrated_study.xml','hardware/power14_single_feed_revB/power_integrated_study.kicad_pcb'),
 'usb_tail':('hardware/usb_tail_revB/usb_tail_revA.xml','hardware/usb_tail_revB/usb_tail_revA.kicad_pcb'),
 'illumination_driver':('hardware/illumination_layout_candidate/illumination_NOFAB.xml','hardware/illumination_layout_candidate/illumination_NOFAB.kicad_pcb'),
 'adc_unplaced_candidate':('hardware/battery_adc_candidate/battery_adc_candidate.xml',None),
 'shared_recovery_fixture':('hardware/gate_supply_native_mpn_source/fixture_projection/mainboard_revD.xml',None)
}
mpn={('usb_tail','J101'):('USB4105-GF-A-120','native XML value'),('mainboard','AE101'):('2450AT18A0100001E','source value, suffix STUDY_NOFAB removed only for lookup'),('mainboard','J202'):('5034802400','source value'),('mainboard','C501'):('C0402C104K4RACTU','hardware/imu_decoupling_0402_source_fix/C501_C502_BOM_candidate.json'),('mainboard','C502'):('C0402C104K4RACTU','hardware/imu_decoupling_0402_source_fix/C501_C502_BOM_candidate.json'),('mainboard','C503'):('C0805C106K8RACTU','hardware/imu_decoupling_0402_source_fix/C503_BOM_candidate.json'),('mainboard','R217'):('RC0402FR-07100KL','hardware/mainboard_bias4_review/R217_candidate.json')}
for old,new in [('C1','C301'),('C2','C302'),('C3','C303'),('R1','R301'),('R2','R302'),('R3','R303')]:
 part=next(r for r in json.load(open(ROOT/'hardware/camera_power_gate_placement_study/bom_candidates.json'))['parts'] if r['ref']==old)
 mpn['mainboard',new]=(part['mpn'],'hardware/camera_power_gate_placement_study/bom_candidates.json; physical candidate, C303 rating source25V vs candidate50V')
rows=[]; native=[]; inputs={}
for rel in ['hardware/gate_supply_native_mpn_source/manifest.json','hardware/imu_compact_0402_placement/manifest.json','hardware/camera_power_gate_placement_study/bom_candidates.json','hardware/imu_decoupling_0402_source_fix/C501_C502_BOM_candidate.json','hardware/imu_decoupling_0402_source_fix/C503_BOM_candidate.json','hardware/mainboard_bias4_review/R217_candidate.json']:
 inputs[rel]=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
inputs[str(MECH/'manifest.json')]=hashlib.sha256((MECH/'manifest.json').read_bytes()).hexdigest()
for owner,(xml,pcb) in SOURCES.items():
 p=ROOT/xml; inputs[xml]=hashlib.sha256(p.read_bytes()).hexdigest(); comps=ET.parse(p).findall('.//components/comp')
 fpd={}
 if pcb:
  pb=ROOT/pcb; inputs[pcb]=hashlib.sha256(pb.read_bytes()).hexdigest(); b=pcbnew.LoadBoard(str(pb)); fpd={f.GetReference():f for f in b.GetFootprints()}; bb=b.GetBoardEdgesBoundingBox()
  native.append({'owner':owner,'pcb':pcb,'sha256':inputs[pcb],'copper_layers':b.GetCopperLayerCount(),'nominal_native_thickness_mm':pcbnew.ToMM(b.GetDesignSettings().GetBoardThickness()),'bounding_box_including_edge_stroke_mm':[pcbnew.ToMM(bb.GetWidth()),pcbnew.ToMM(bb.GetHeight())],'footprints':len(fpd),'F':sum(f.GetLayerName()=='F.Cu' for f in fpd.values()),'B':sum(f.GetLayerName()=='B.Cu' for f in fpd.values())})
 for c in comps:
  ref=c.get('ref');value=c.findtext('value') or '';fp=c.findtext('footprint') or '';dnp=c.find("property[@name='dnp']") is not None
  feature=(ref.startswith(('TP','JP')) or (ref.startswith('J') and not(owner=='mainboard' and ref=='J202') and not(owner=='usb_tail' and ref=='J101')))
  if owner=='shared_recovery_fixture':feature=False
  candidate,basis=mpn.get((owner,ref),('','exact MPN absent from frozen source'))
  if not candidate and (ref.startswith(('U','Q','D','RT')) or (owner=='power' and ref=='L1')):
   candidate=value.split()[0];basis='native XML value'
  native_mpn=c.findtext("fields/field[@name='MPN']")
  if native_mpn:
   if candidate and candidate!=native_mpn:raise ValueError(('native MPN mismatch',owner,ref,candidate,native_mpn))
   candidate=native_mpn;basis='native XML MPN field; conditional procurement status retained'
  status='dnp_no_purchase' if dnp else ('pcb_copper_feature_not_purchased_connector' if feature else ('candidate_MPN_not_procurement_approved' if candidate else 'exact_MPN_unresolved'))
  actual=fpd.get(ref);side=actual.GetLayerName() if actual else ('offboard' if ref.startswith('RT') else 'unplaced')
  qq=0 if dnp or feature else (1 if owner=='shared_recovery_fixture' else 2)
  package=fp.split(':')[-1]
  hidden=any(t in package.upper() for t in ['LGA','WSON','USON','RGT0016','DLA0010','DSE0006'])
  method='NOT_A_PURCHASED_PART' if not qq else ('CONTROLLED_REFLOW_AND_HIDDEN_JOINT_INSPECTION_REQUIRED' if hidden else 'HAND_ASSEMBLY_POSSIBLE_ONLY_WITH_QUALIFIED_PROCESS_AND_QUOTED_LABOR')
  if owner=='mainboard' and ref in ['C501','C502','C503']:note='source native MPN fields successor; physical package/face from frozen dd55 PCB; no claim source-field successor integrated into active gate routing'
  else:note=''
  rows.append(dict(owner=owner,ref=ref,value=value,candidate_MPN=candidate,mpn_basis=basis,footprint=fp,side=side,dnp=dnp,entity_qty_per_pen=0 if owner=='shared_recovery_fixture' else 1,purchased_part_qty_two_pens=qq,minimum_purchase_qty=None,unit_price_CNY=None,line_total_CNY=None,status=status,assembly_class=method,source_xml=xml,notes=note))
# Real mechanical switch carrier is a distinct two-entity candidate, NOT the obsolete pickup board.
pcb=MECH/'contact_carrier_NOFAB.kicad_pcb';b=pcbnew.LoadBoard(str(pcb));inputs[str(pcb)]=hashlib.sha256(pcb.read_bytes()).hexdigest()
for f in b.GetFootprints():
 ref=f.GetReference();is_switch=ref=='SW1'
 rows.append(dict(owner='contact_cassette_carrier',ref=ref,value=f.GetValue(),candidate_MPN='SPVE110100' if is_switch else '',mpn_basis='mechanical RevC README and native carrier',footprint=str(f.GetFPID()),side=f.GetLayerName(),dnp=False,entity_qty_per_pen=1,purchased_part_qty_two_pens=2 if is_switch else 0,minimum_purchase_qty=None,unit_price_CNY=None,line_total_CNY=None,status='conditional_switch_not_electrically_qualified' if is_switch else 'pcb_copper_feature_not_purchased_connector',assembly_class='MANUFACTURER_SOLDERING_PROCESS_AND_MECHANICAL_CALIBRATION_REQUIRED' if is_switch else 'NOT_A_PURCHASED_PART',source_xml='',notes='mechanical proposal, no system source integration; 100k frontend incompatible with specified minimum switch load'))
bb=b.GetBoardEdgesBoundingBox();native.append({'owner':'contact_cassette_carrier','pcb':str(pcb),'sha256':inputs[str(pcb)],'copper_layers':b.GetCopperLayerCount(),'nominal_native_thickness_mm':pcbnew.ToMM(b.GetDesignSettings().GetBoardThickness()),'bounding_box_including_edge_stroke_mm':[pcbnew.ToMM(bb.GetWidth()),pcbnew.ToMM(bb.GetHeight())],'footprints':len(list(b.GetFootprints()))})
prices={r['mpn']:r for r in json.load(open(OUT/'price_evidence.json'))['prices']}
from decimal import Decimal
for row in rows:
    pr=prices.get(row['candidate_MPN']);q=row['purchased_part_qty_two_pens']
    row['price_class']='unpriced';row['price_url']=''
    if q and pr and pr.get('unit_CNY') is not None:
        row['unit_price_CNY']=pr['unit_CNY'];row['line_total_CNY']=str(Decimal(str(pr['unit_CNY']))*q)
        row['price_class']=pr['class'];row['price_url']=pr['url']
with open(OUT/'two_pen_component_ledger.csv','w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(OUT/'native_boards.json').write_text(json.dumps(native,ensure_ascii=False,indent=2)+'\n')
(OUT/'input_hashes.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+'\n')
summary={}
for owner in sorted(set(r['owner'] for r in rows)):
 rr=[r for r in rows if r['owner']==owner];summary[owner]={'entities_per_source':len(rr),'parts_needed_two_pens_or_one_shared_fixture':sum(r['purchased_part_qty_two_pens'] for r in rr),'exact_MPN_unresolved_entities':sum(r['status']=='exact_MPN_unresolved' for r in rr),'assembly_classes':dict(collections.Counter(r['assembly_class'] for r in rr)),'purchased_part_faces':dict(collections.Counter(r['side'] for r in rr if r['purchased_part_qty_two_pens']))}
(OUT/'bom_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2));print(json.dumps(native,indent=2))
