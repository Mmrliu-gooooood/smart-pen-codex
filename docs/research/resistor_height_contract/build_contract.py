from pathlib import Path
import json,hashlib,pcbnew
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'hardware/mainboard_width14_preplacement/mainboard_revD.kicad_pcb'
expected='f27cd35dcaf51fd33078b60a7029f6f63fba9c58f1d2791488e8a1721330080c'
if hashlib.sha256(P.read_bytes()).hexdigest()!=expected: raise ValueError('Source board changed')
b=pcbnew.LoadBoard(str(P)); fs={f.GetReference():f for f in b.GetFootprints()}
groups=[(['R104','R240'],10000,'RC0603FR-0710KL','C98220','10k'),(['R221','R224','R233','R218','R210','R228'],100000,'RC0603FR-07100KL','C14675','100k'),(['R236'],4700,'RC0603FR-074K7L','C99782','4.7k')]
rows=[]
for refs,ohms,mpn,lcsc,token in groups:
 for ref in refs:
  f=fs[ref]
  if not f.GetValue().startswith(token+' 1%'): raise ValueError(ref+' value mismatch')
  pads=sorted(f.Pads(),key=lambda p:p.GetNumber())
  rows.append(dict(ref=ref,source_value=f.GetValue(),source_path=f.GetPath().AsString(),manufacturer='YAGEO',mpn=mpn,resistance_ohm=ohms,tolerance_percent=1,rated_power_W_at_70C=.1,max_continuous_voltage_V=75,temperature_coefficient_ppm_C=100,body_max_mm=[1.7,.9,.55],body_height_max_mm=.55,assumed_solder_assembly_allowance_mm=.15,conditional_height_above_copper_mm=.70,source_net_by_pin={p.GetNumber():p.GetNetname() for p in pads},native_pad_size_mm=[[p.GetSize().x/1e6,p.GetSize().y/1e6] for p in pads],native_pad_centres_mm=[[p.GetPosition().x/1e6,p.GetPosition().y/1e6] for p in pads],native_footprint=str(f.GetFPID().GetLibNickname())+':'+str(f.GetFPID().GetLibItemName()),electrical_5V5_resistor_only_screen_W=5.5**2/(ohms*.99),datasheet_url='https://yageogroup.com/component-documentation/download/specsheet/'+mpn,procurement_listing='https://www.lcsc.com/product-detail/'+lcsc+'.html',functional_qualification='RESET polarity/module compatibility remains unverified' if ref=='R236' else ('100 kHz pullup initial candidate; bus rise-time qualification remains open' if ref=='R240' else 'No resistance/function change; existing signal/strap qualification retained'),land_pattern_status='same package; native lands NOT identical to manufacturer reflow recommendation; assembly qualification OPEN'))
d=dict(status='CONDITIONAL_MECHANICAL_COMPARISON_ONLY_NOFAB',board_path=str(P.relative_to(ROOT)),board_sha256=expected,scope_refs=[r['ref'] for r in rows],not_covered=['C103','C203','C201','C205','all other components and wire envelopes'],resistors=rows,manufacturer_reflow_land_pattern_mm=dict(overall_span_A=2.6,inner_gap_B=.8,pad_length_C=.9,pad_width_D=.8),native_land_pattern_mm=dict(overall_span=2.45,inner_gap=.85,pad_length=.8,pad_width=.95),mounting_source='https://yageogroup.com/content/Resource%20Library/Product%20Guide-Catalog/yageo_PYu-R_Mount_10_19050818_343.pdf',mounting_source_page=4)
(Path(__file__).parent/'contract.json').write_text(json.dumps(d,indent=2)+'\n')
