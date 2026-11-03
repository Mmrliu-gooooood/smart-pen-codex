import pathlib,xml.etree.ElementTree as E,json,copy
P=pathlib.Path(__file__).parent
x=E.parse(P/'netlist.xml').getroot()
def check(x):
 c={a.get('ref'):a for a in x.findall('./components/comp')};n={}
 if len(c)!=32:raise ValueError('count')
 for a in x.findall('./nets/net'):
  for b in a.findall('node'):n[b.get('ref'),b.get('pin')]=a.get('name').lstrip('/')
 expected=['GND','MUX_VDD','H_21','ISO_SCL','H_22','ISO_SDA','ISO_READY','ISO_READY','GND','GND','GND','GND']
 for i,v in enumerate(expected,1):
  if n.get(('U1',str(i)))!=v:raise ValueError('mux pin')
 for ref,vals in {'R13':['ISO_SCL','M_SCL'],'R14':['ISO_SDA','M_SDA'],'R16':['HOST_VIO_1V8','MUX_VDD'],'R17':['READY_SOURCE_UNASSIGNED','ISO_READY'],'R18':['ISO_READY','GND'],'C2':['MUX_VDD','GND']}.items():
  for i,v in enumerate(vals,1):
   if n.get((ref,str(i)))!=v:raise ValueError('path')
 for ref in ['U1']+['R'+str(i) for i in range(1,18)]:
  if c[ref].find('./property[@name="dnp"]') is None:raise ValueError('default fitted')
 if n.get(('J1','23'))!='HOST_VIO_1V8':raise ValueError('rail')
 # no unreviewed host drive source on readiness input
 members={p for p,net in n.items() if net=='READY_SOURCE_UNASSIGNED'}
 if members!={('R17','1'),('TP8','1')}:raise ValueError('ready assigned')
 if c['R18'].findtext('value')!='10k_1pct_DEFAULT_LOW':raise ValueError('pulldown')
 return n
check(x)
for mode in range(4):
 z=copy.deepcopy(x)
 if mode==0:z.find('./components/comp[@ref="R17"]').remove(z.find('./components/comp[@ref="R17"]/property[@name="dnp"]'))
 elif mode==1:z.find('./nets/net[@name="/ISO_SCL"]').set('name','/H_21')
 elif mode==2:z.find('./nets/net[@name="/MUX_VDD"]').set('name','/MOD_3V3')
 else:z.find('./components/comp[@ref="R18"]/value').text='DNP'
 try:check(z)
 except ValueError:pass
 else:raise RuntimeError('negative accepted')
if any(s['violations'] for s in json.load(open(P/'erc.json'))['sheets']):raise RuntimeError('ERC')
print('PASS 32 components, exact RWB mapping, no bypass, default DNP, unassigned enable, 4 negatives, ERC0')
