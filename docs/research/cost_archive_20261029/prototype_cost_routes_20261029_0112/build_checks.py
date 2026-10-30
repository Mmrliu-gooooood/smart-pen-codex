#!/usr/bin/env python3
"""Read-only source comparison and explicitly conditional arithmetic; no design output."""
from pathlib import Path
import xml.etree.ElementTree as ET
import hashlib,json,re,math
R=Path(__file__).resolve().parent
W=R.parents[3]
H=W/'smart_pen_next_20261028'
source=H/'hardware/gate_supply_native_mpn_source/mainboard_projection/mainboard_revD.xml'
def require(ok,msg):
 if not ok: raise RuntimeError(msg)
root=ET.parse(source).getroot(); rows=[]
# Official MINI datasheet v1.7 table3-1; IO26 excluded for N4R2 embedded PSRAM.
mini={i:i+4 for i in range(22)}
mini.update({47:27,33:28,34:29,48:30,35:31,36:32,37:33,38:34,39:35,40:36,41:37,42:38,43:39,44:40,45:41,46:44})
for net in root.findall('.//nets/net'):
 for n in net.findall('node'):
  m=re.match(r'GPIO(\d+)',n.get('pinfunction',''))
  if n.get('ref')=='U101' and m and 'no_connect' not in n.get('pintype',''):
   g=int(m.group(1));rows.append(dict(gpio=g,net=net.get('name'),pico_pin=int(n.get('pin')),mini_pin=mini.get(g),strap=g in [0,3,45,46]))
rows.sort(key=lambda r:r['gpio'])
require(len(rows)==33,'connected GPIO count changed')
require(len({r['gpio'] for r in rows})==33,'duplicate source GPIO')
require(all(r['mini_pin'] is not None for r in rows),'MINI pin missing')
require(26 not in mini,'PSRAM GPIO26 cannot be free')
require(set(mini)-{r['gpio']for r in rows}==set(range(33,38)),'additional GPIO set changed')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
paths=[source,H/'hardware/imu_compact_0402_placement/mainboard_revD.kicad_pcb',H/'docs/research/prototype_cost_audit_20261029_0044/manifest.json',H/'docs/research/power_architecture_tradeoff/README.md',H/'docs/research/high_beta_ntc_followup_20261028/README.md',W/'smart_pen_mechanics_next_20261028/mechanical/compact_contact_cassette_2356/build_cad.py',W/'smart_pen_mechanics_next_20261028/mechanical/width14_gate/README.md',W/'smart_pen_continuous_v3_target_benchmark_20261029/main/bench_main.c']
inputs={str(p.relative_to(W)):sha(p) for p in paths}
front=3.194793176328504; max_w=15.6; max_h=2.55; solder=.15; board=.93
allowance=2*(1.2+.1+.2+.1) # nominal wall+wall tolerance+outward shift/bow+residual, per radius
geometry=dict(status='CONSERVATIVE_PRISM_SCREEN_NOT_EXACT_SOLID_OR_SELECTED_OD',module_max_width_mm=max_w,module_max_height_mm=max_h,assumed_solder_allowance_mm=solder,main_front_Y_mm=front,main_max_thickness_mm=board,radial_allowances_mm=[1.2,.1,.2,.1],fixed_front_radius_mm=math.hypot(max_w/2,front+max_h+solder),fixed_front_conditional_OD_mm=2*math.hypot(max_w/2,front+max_h+solder)+allowance,ideal_centered_module_only_prism_OD_mm=math.hypot(max_w,max_h)+allowance,ideal_centered_module_carrier_bounding_rectangle_OD_mm=math.hypot(max_w,max_h+solder+board)+allowance,wroom_nominal_body_only_prism_OD_mm=math.hypot(18,3.1)+allowance,limitations=['No exact STEP solids, module placement or collision study','Body prism/carrier bbox are conservative envelopes, not mathematical impossibility bounds','No refill, opposite-side parts, antenna/harness, fasteners or shell support in centered cases','19 mm is an unapproved research candidate'])
scenarios=[]
for name,mcu,status in [('PICO official reference',74,'not_checked_stock'),('PICO LCSC unavailable reference',124,'stock_zero'),('MINI official reference',48,'not_checked_stock'),('MINI LCSC unavailable reference',61.2,'stock_zero'),('MINI DigiKey China page sample',88.82,'web_snapshot_101_not_reserved')]:
 scenarios.append(dict(mcu=name,status=status,assumed_fixed_CNY=400,known_five_original_power_parts_CNY=111.96,bq_original_DigiKey_reference_CNY=40.20,mcu_two_CNY=mcu,remaining_everything_else_CNY=round(760-400-111.96-40.20-mcu,2)))
require(scenarios[0]['remaining_everything_else_CNY']==133.84,'PICO arithmetic')
require(scenarios[-1]['remaining_everything_else_CNY']==119.02,'MINI arithmetic')
require(2*200*200+32640==112640,'ROI memory bound')
result=dict(status='PASS_RESEARCH_ONLY_NO_ROUTE_RELEASE',input_sha256=inputs,gpio_rows=rows,mini_effective_gpio_count=38,mini_additional_candidates=[33,34,35,36,37],geometry=geometry,conditional_scenarios=scenarios,roi_arithmetic_bytes={'one_gray200x200':40000,'workspace':32640,'one_image_plus_workspace':72640,'two_images_plus_workspace':112640},no_circuit_modification=True,no_purchase_or_quote_submission=True)
(R/'checked_comparisons.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'source_gpio_count':len(rows),'all_map_to_mini':True,'additional_candidates':result['mini_additional_candidates'],'fixed_front_conditional_OD_mm':geometry['fixed_front_conditional_OD_mm'],'PICO_scenario_remainder_CNY':133.84,'MINI_DigiKey_scenario_remainder_CNY':119.02},ensure_ascii=False))
