"""Offline checks of frozen reported data only; not native KiCad/BOM extraction,
current price verification, purchase approval or mechanical calibration acceptance.
Original files are hash checked, never rewritten. Works with Python -O.
"""
import copy,csv,hashlib,json,math,subprocess,sys
from decimal import Decimal
from pathlib import Path
HERE=Path(__file__).resolve().parent
AUDIT=HERE/'prototype_cost_audit_20261029_0044';ROUTES=HERE/'prototype_cost_routes_20261029_0112'
def require(ok,msg):
 if not ok:raise ValueError(msg)
def check(rows):
 require(len(rows)==188,'row count');ids=[(r['owner'],r['ref']) for r in rows];require(len(ids)==len(set(ids)),'duplicate owner/ref')
 require(sum(r['owner']=='mainboard' for r in rows)==102,'mainboard count')
 require(sum(r['owner']=='power' for r in rows)==52,'power count')
 require(not any(r['owner'] in ('pickup_contact','camera_power_gate') for r in rows),'migrated ownership duplicate')
 prices={x['mpn']:x for x in json.loads((AUDIT/'domestic_price_comparison.json').read_text())['parts']}
 for r in rows:
  q=int(r['purchased_part_qty_two_pens']);require(q>=0,'negative count')
  require(not(q and (r['dnp']=='True' or r['status']=='pcb_copper_feature_not_purchased_connector')),'DNP/copper purchased')
  if r['line_total_CNY']:
   require(bool(r['unit_price_CNY'] and r['price_url']),'price provenance')
   require(Decimal(r['line_total_CNY'])==Decimal(r['unit_price_CNY'])*q,'reference arithmetic')
  else:require(not r['unit_price_CNY'],'missing line total')
  p=prices.get(r['candidate_MPN'])
  if not p or not q:continue
  require(r['domestic_small_qty_available']==str(p['small_qty_display_available']),'availability mismatch')
  require(r['domestic_url']==p['url'] and r['domestic_observed_utc']==p['observed_utc'],'domestic source')
  if p['unit_CNY_at_needed_qty'] is None:require(not r['domestic_installed_line_CNY'],'wrong MOQ applied')
  else:require(Decimal(r['domestic_installed_line_CNY'])==Decimal(str(p['unit_CNY_at_needed_qty']))*q,'domestic arithmetic')
  if r['domestic_small_qty_available']=='True':require(p['stock_kind']=='on_hand' and p['stock_display']>=q and p['minimum_order_qty']<=q,'quantity not available')
 subtotal=lambda category:sum(Decimal(r['line_total_CNY']) for r in rows if r['price_class']==category)
 reference=subtotal('authorized_distributor_public_listing');sample=subtotal('manufacturer_sample_reference')
 domestic=sum(Decimal(r['domestic_installed_line_CNY']) for r in rows if r['domestic_small_qty_available']=='True')
 require(reference==Decimal('504.58') and sample==74 and domestic==Decimal('111.96'),'subtotal')
 require(sum(int(r['purchased_part_qty_two_pens']) for r in rows if r['owner']!='shared_recovery_fixture')==300,'component count')
 return {'rows':len(rows),'per_pen_entities_excluding_shared':185,'two_pen_electronics_count':300,'shared_fixture_parts':3,'historical_reference_partial_CNY':str(reference),'historical_sample_reference_CNY':str(sample),'historical_domestic_available_partial_CNY':str(domestic),'hypothetical_fixed400_remaining_CNY':str(Decimal(760)-400-domestic),'global_market_lower_bound':None,'purchase_or_budget_approval':False}
def main():
 subset=json.loads((HERE/'SOURCE_SUBSET_SHA256.json').read_text())['files']
 for r in subset:
  rel=Path(r['path']);p=HERE/rel;require(not rel.is_absolute() and '..' not in rel.parts and not p.is_symlink(),'unsafe path')
  raw=p.read_bytes();require(len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256'],'source '+r['path'])
 rows=list(csv.DictReader((AUDIT/'two_pen_component_ledger.csv').open()));cost=check(rows);negative=[]
 for name,mutate in [('duplicate',lambda rr:rr.append(copy.deepcopy(rr[0]))),('wrong_quantity',lambda rr:next(r for r in rr if r['candidate_MPN']=='SN74AXC4T245PWR').update(purchased_part_qty_two_pens='1')),('DNP_purchase',lambda rr:next(r for r in rr if r['dnp']=='True').update(purchased_part_qty_two_pens='2')),('out_of_stock_claimed_available',lambda rr:next(r for r in rr if r['candidate_MPN']=='ESP32-S3-PICO-1-N8R8').update(domestic_small_qty_available='True')),('wrong_domestic_sum',lambda rr:next(r for r in rr if r['candidate_MPN']=='TPS63802DLAR').update(domestic_installed_line_CNY='1'))]:
  changed=copy.deepcopy(rows);mutate(changed)
  try:check(changed)
  except ValueError:negative.append(name)
  else:raise ValueError('negative accepted '+name)
 route=json.loads((ROUTES/'checked_comparisons.json').read_text());g=route['geometry']
 require(len(route['gpio_rows'])==33 and len({x['gpio'] for x in route['gpio_rows']})==33,'stored GPIO count')
 mini={i:i+4 for i in range(22)};mini.update({47:27,33:28,34:29,48:30,35:31,36:32,37:33,38:34,39:35,40:36,41:37,42:38,43:39,44:40,45:41,46:44})
 require(all(r['mini_pin']==mini.get(r['gpio']) and r['strap']==(r['gpio'] in (0,3,45,46)) for r in route['gpio_rows']),'stored mapping')
 require(set(mini)-{r['gpio'] for r in route['gpio_rows']}==set(range(33,38)),'additional candidates')
 for r in route['conditional_scenarios']:
  amount=Decimal(760)-Decimal(str(r['assumed_fixed_CNY']))-Decimal(str(r['known_five_original_power_parts_CNY']))-Decimal(str(r['bq_original_DigiKey_reference_CNY']))-Decimal(str(r['mcu_two_CNY']))
  require(amount==Decimal(str(r['remaining_everything_else_CNY'])),'conditional scenario arithmetic')
 expected=2*math.hypot(g['module_max_width_mm']/2,g['main_front_Y_mm']+g['module_max_height_mm']+g['assumed_solder_allowance_mm'])+2*sum(g['radial_allowances_mm'])
 require(abs(expected-g['fixed_front_conditional_OD_mm'])<1e-12,'conditional prism arithmetic')
 require(route['roi_arithmetic_bytes']=={'one_gray200x200':40000,'workspace':32640,'one_image_plus_workspace':72640,'two_images_plus_workspace':112640},'ROI arithmetic')
 metrology=HERE/'metrology_target_erratum_0139';mr=json.loads((metrology/'normal.json').read_text())
 for optimized in (False,True):
  cmd=[sys.executable]+(['-O'] if optimized else [])+[str(metrology/'check.py')]
  run=subprocess.run(cmd,text=True,capture_output=True,check=True);require(json.loads(run.stdout)==mr,'metrology replay')
 require(mr==json.loads((metrology/'optimized.json').read_text()),'frozen metrology normal/-O')
 print(json.dumps({'metrology_original_check_normal_and_optimized_passed':True,'five_micron_purchase_required':False,'replacement_stroke_approved':False,'scope':'offline historical reported-data arithmetic only; not full native source regeneration or current price/availability checks','frozen_source_files_verified':len(subset),'cost':cost,'negative_cases_rejected':negative,'route_stored_gpio_rows_checked':33,'route_conditional_scenarios_checked':len(route['conditional_scenarios']),'conditional_prism_arithmetic_checked':True,'native_BOM_regenerated':False,'source_XML_connectivity_reextracted':False,'vendor_price_refreshed':False,'mechanical_5um_requirement_validated':False,'procurement_performed':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
