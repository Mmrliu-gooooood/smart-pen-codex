#!/usr/bin/env python3
"""Checks actual independent KiCad netlists; does not join physical boards."""
from pathlib import Path
import xml.etree.ElementTree as ET,json,hashlib
from datetime import datetime,timezone
P=Path(__file__).resolve().parent
files={'mcu':P/'mcu_usb/mcu_usb.xml','power':P/'power_core/power_core_NOFAB.xml','pickup':P/'pickup_contact/pickup_contact.xml'}
roots={k:ET.parse(v).getroot() for k,v in files.items()}
# Power core uses root-sheet local labels: /NAME; strip only that one root prefix.
def canonical(name):return name[1:] if name.startswith('/') and name.count('/')==1 else name
nets={k:{canonical(n.get('name')):len(n.findall('node')) for n in r.findall('./nets/net')} for k,r in roots.items()}
for k,r in roots.items():assert len(r.findall('./components/comp'))>=8,'empty/partial '+k
checks=[]
for peer,names in [('power',['VBUS_5V','3V3_AON','GND','USB_EN1','USB_EN2']),('pickup',['3V3_AON','GND','AON_I2C_SCL','AON_I2C_SDA','PICKUP_INT_N','NIB_CONTACT_N'])]:
 for n in names:
  ok=nets['mcu'].get(n,0)>1 and nets[peer].get(n,0)>1
  checks.append({'peer':peer,'net':n,'mcu_nodes':nets['mcu'].get(n,0),'peer_nodes':nets[peer].get(n,0),'pass':ok})
report={'date_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'pass':all(c['pass'] for c in checks),'physical_interconnect_verified':False,'complete_merged_system_netlist':False,'sha256':{k:hashlib.sha256(f.read_bytes()).hexdigest() for k,f in files.items()}}
(P/'integration_checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['pass']
