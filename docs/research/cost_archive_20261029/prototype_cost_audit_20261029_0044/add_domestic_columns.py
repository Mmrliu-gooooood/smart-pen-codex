#!/usr/bin/env python3
"""Keep original comparable reference prices; add independent domestic evidence columns."""
import csv,json
from pathlib import Path
from decimal import Decimal
p=Path(__file__).resolve().parent
rows=list(csv.DictReader(open(p/'two_pen_component_ledger.csv')))
prices={x['mpn']:x for x in json.load(open(p/'domestic_price_comparison.json'))['parts']}
for r in rows:
    for k in ['domestic_unit_CNY','domestic_installed_line_CNY','domestic_MOQ','domestic_display_stock','domestic_small_qty_available','domestic_url','domestic_observed_utc']:r[k]=''
    x=prices.get(r['candidate_MPN']);q=int(r['purchased_part_qty_two_pens'])
    if x and q:
        r.update(domestic_unit_CNY=x['unit_CNY_at_needed_qty'],domestic_MOQ=x['minimum_order_qty'],domestic_display_stock=x['stock_display'],domestic_small_qty_available=x['small_qty_display_available'],domestic_url=x['url'],domestic_observed_utc=x['observed_utc'])
        if x['unit_CNY_at_needed_qty'] is not None:r['domestic_installed_line_CNY']=str(Decimal(str(x['unit_CNY_at_needed_qty']))*q)
with open(p/'two_pen_component_ledger.csv','w') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
# Component-only display available subtotal excludes out of stock and wrong MOQ.
actual=sum(Decimal(r['domestic_installed_line_CNY']) for r in rows if str(r['domestic_small_qty_available'])=='True')
if actual!=Decimal('111.96'):raise ValueError(('domestic subtotal drift',actual))
print(actual)
