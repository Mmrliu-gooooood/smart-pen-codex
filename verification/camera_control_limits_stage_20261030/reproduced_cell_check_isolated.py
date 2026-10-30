"""Read-only native contract/corner audit. No charge permission is generated."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as E
p=Path(__file__).resolve().parent;root=p.parents[2]; h=root/'hardware/power14_single_feed_revB'
def parse(path):
 r=E.parse(path).getroot()
 return ({c.attrib['ref']:c.findtext('value') for c in r.find('components')}, {n.attrib['name']:sorted((x.attrib['ref'],x.attrib['pin']) for x in n) for n in r.find('nets')})
c,n=parse(h/'power_integrated_study.xml'); cf,nf=parse(p/'fresh_netlist.xml')
if (c,n)!=(cf,nf):raise RuntimeError('Fresh native netlist differs')
for k,v in {'U1':'BQ24074RGTR','R1':'8.66k 1%','R2':'3.24k 1%','R3':'68k 1%','R6':'10k 1%','JP1':'OPEN / DO NOT BRIDGE'}.items():
 if c[k]!=v:raise RuntimeError((k,c[k]))
rlo,rhi=8660*.99,8660*1.01
imin,imax=797/rhi,975/rlo
out={'native_fresh_netlist_matches_frozen':True,'selected_components':{k:c[k] for k in ['U1','R1','R2','R3','R6','J1','J4','J5','JP1','RT101','RT102']},'relevant_nets':{k:v for k,v in n.items() if any(x[0] in ['JP1','R1','R2','R3','J5','RT101','RT102'] for x in v)},'conditional_not_measured':{'RISET_range_ohm':[rlo,rhi],'within_TI_590_to_8900_ohm':590<=rlo<=rhi<=8900,'fast_charge_mA':[imin*1000,imax*1000],'nominal_fast_charge_mA':890/8660*1000,'precharge_mA':[70/rhi*1000,106/rlo*1000],'termination_non_USB100_mA':[.09*imin*1000,.11*imax*1000],'termination_USB100_mA':[.027*imin*1000,.040*imax*1000],'programmed_input_limit_mA':[1330/(3240*1.01)*1000,1720/(3240*.99)*1000],'fast_timer_h':[68*.99*36*10/3600,68*1.01*60*10/3600],'precharge_timer_h':[68*.99*36/3600,68*1.01*60/3600],'Jauch_CC_capacity_over_current_h':[.85/imax,.85/imin],'P1044C_CC_capacity_over_current_h':[.55/imax,.55/imin]},'release':'NO QUALIFIED CELL; JP1 OPEN; NOFAB/NOPOWER'}
(p/'results.json').write_text(json.dumps(out,indent=2)+'\n')
inputs=[h/x for x in ['core.kicad_sch','thermal.kicad_sch','power_integrated_study.kicad_sch','power_integrated_study.kicad_pcb','power_integrated_study.xml','SINGLE_FEED_REVB_MANIFEST.json']]+[root/'docs/electronics/battery_qualification_next.md',root/'docs/electronics/reference_thermal_next.md',root/'hardware/battery_qualification_next/candidates.json']
(p/'input_hashes.json').write_text(json.dumps({str(x.relative_to(root)):hashlib.sha256(x.read_bytes()).hexdigest() for x in inputs},indent=2)+'\n')
mech=root.parent/'smart_pen_mechanics_next_20261028'
mi=[mech/'docs/mechanical/整笔装配RevC_真实95mm板_20261028.md',mech/'mechanical/compliant_retainer_longarc_0415/ENGINEERING_CONTRACT_DRAFT.md',mech/'mechanical/compliant_retainer_longarc_0415/access_revision/REVISION_CONTRACT.md']
(p/'mechanical_input_hashes.json').write_text(json.dumps({str(x.relative_to(root.parent)):hashlib.sha256(x.read_bytes()).hexdigest() for x in mi},indent=2)+'\n')
print(json.dumps(out['conditional_not_measured'],indent=2))
