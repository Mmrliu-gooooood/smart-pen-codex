from pathlib import Path
import json,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent;x=E.parse(D/'fresh.xml');rows=[dict(v.attrib)for n in x.findall('./nets/net')if n.get('name')=='SENS_VIO_1V8'for v in n];power={(v['ref'],v['pin']):v['pinfunction']for v in rows if v['ref'].startswith('U')}
expected={('U201','23'):'VCCB',('U201','24'):'VCCB',('U202','16'):'VCCB',('U203','16'):'VCCB',('U204','1'):'VCCA'}
if power!=expected:raise RuntimeError('Actual VIO power pins differ')
print(json.dumps({'native_SENS_VIO_endpoints':rows,'finding':'Frozen interface_reference_contract VIO_direction translator A domain and VIO_load_boundary AXC/TCA VCCA are incorrect generalizations; AXC uses VCCB, TCA uses VCCA. Documentation erratum required for integration/publication. Copper source identity is unchanged.','external_supply':'Future qualified external compact-head input condition, not an already qualified supply or local regulator output'},indent=2))
