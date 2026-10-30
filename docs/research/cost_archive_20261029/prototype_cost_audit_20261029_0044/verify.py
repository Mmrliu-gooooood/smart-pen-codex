#!/usr/bin/env python3
import csv,json,copy,hashlib
from decimal import Decimal
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def fail(msg):raise ValueError(msg)
def check(rows):
 ids=[(r['owner'],r['ref']) for r in rows]
 if len(ids)!=len(set(ids)):fail('duplicate owner/ref')
 if sum(r['owner']=='mainboard' for r in rows)!=102:fail('wrong mainboard count')
 if sum(r['owner']=='power' for r in rows)!=52:fail('power source including2offboardNTCs must52')
 if any('pickup_contact'==r['owner'] or 'camera_power_gate'==r['owner'] for r in rows):fail('duplicate migrated boards')
 for r in rows:
  q=int(r['purchased_part_qty_two_pens'])
  if r['dnp']=='True' and q:fail('DNP bought')
  if r['status']=='pcb_copper_feature_not_purchased_connector' and q:fail('copper feature bought')
  if r['line_total_CNY']:
   if not r['unit_price_CNY'] or not r['price_url']:fail('price provenance absent')
   if Decimal(r['line_total_CNY'])!=Decimal(r['unit_price_CNY'])*q:fail('incorrect line sum')
  elif r['unit_price_CNY']:fail('missing line arithmetic')
 sum_public=sum(Decimal(r['line_total_CNY']) for r in rows if r['price_class']=='authorized_distributor_public_listing')
 sum_ref=sum(Decimal(r['line_total_CNY']) for r in rows if r['price_class']=='manufacturer_sample_reference')
 if sum_public!=Decimal('504.58') or sum_ref!=74:fail('unexpected cited partial subtotal')
 domestic={x['mpn']:x for x in json.load(open(P/'domestic_price_comparison.json'))['parts']}
 for r in rows:
  x=domestic.get(r['candidate_MPN']);q=int(r['purchased_part_qty_two_pens'])
  if not x or not q:continue
  if r['domestic_small_qty_available']!=str(x['small_qty_display_available']):fail('domestic availability drift')
  if r['domestic_url']!=x['url'] or r['domestic_observed_utc']!=x['observed_utc']:fail('domestic provenance drift')
  if x['unit_CNY_at_needed_qty'] is None:
   if r['domestic_installed_line_CNY']:fail('wrong MOQ price applied')
  elif Decimal(r['domestic_installed_line_CNY'])!=Decimal(str(x['unit_CNY_at_needed_qty']))*q:fail('domestic line arithmetic')
  if r['domestic_small_qty_available']=='True':
   if x['stock_kind']!='on_hand' or x['stock_display']<q or x['minimum_order_qty']>q:fail('not available at needed qty')
 sum_domestic=sum(Decimal(r['domestic_installed_line_CNY']) for r in rows if r['domestic_small_qty_available']=='True')
 if sum_domestic!=Decimal('111.96'):fail('domestic subtotal drift')
 return {'rows':len(rows),'per_pen_source_entities_excluding_shared_fixture':len(rows)-3,'purchased_electronics_two_pens':sum(int(r['purchased_part_qty_two_pens']) for r in rows if r['owner']!='shared_recovery_fixture'),'shared_fixture_parts':3,'public_price_partial_CNY':str(sum_public),'manufacturer_sample_reference_CNY':str(sum_ref),'hypothetical_fixed400_plus_public_only_CNY':str(sum_public+400),'domestic_available_partial_CNY':str(sum_domestic),'hypothetical_400_remaining_after_domestic_partial_CNY':str(Decimal(760)-400-sum_domestic),'global_lower_bound_CNY':None,'budget_pass':False}
rows=list(csv.DictReader(open(P/'two_pen_component_ledger.csv')));result=check(rows)
for rel,h in json.load(open(P/'input_hashes.json')).items():
 p=Path(rel);p=p if p.is_absolute() else ROOT/p
 if hashlib.sha256(p.read_bytes()).hexdigest()!=h:fail('input changed: '+str(p))
negative=[]
for name,mutate in [('duplicate',lambda rr:rr.append(copy.deepcopy(rr[0]))),('wrong_quantity',lambda rr:next(r for r in rr if r['candidate_MPN']=='SN74AXC4T245PWR').update(purchased_part_qty_two_pens='1')),('DNP_purchase',lambda rr:next(r for r in rr if r['dnp']=='True').update(purchased_part_qty_two_pens='2')),('out_of_stock_claimed_available',lambda rr:next(r for r in rr if r['candidate_MPN']=='ESP32-S3-PICO-1-N8R8').update(domestic_small_qty_available='True')),('wrong_domestic_sum',lambda rr:next(r for r in rr if r['candidate_MPN']=='TPS63802DLAR').update(domestic_installed_line_CNY='1'))]:
 rr=copy.deepcopy(rows);mutate(rr)
 try:check(rr)
 except ValueError:negative.append(name)
 else:fail('negative accepted: '+name)
result['negative_rejected']=negative
print(json.dumps(result,ensure_ascii=False,indent=2))
