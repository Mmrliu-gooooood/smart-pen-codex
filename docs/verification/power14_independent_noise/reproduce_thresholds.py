"""Independent 3-node nodal model for frozen R109..R113/RT101/U105 inputs.
No imported design evaluator, no writes to hardware, explicit runtime guards.
"""
import itertools as it,json,math
from pathlib import Path
import numpy as np
import xml.etree.ElementTree as ET
P=Path(__file__).resolve().parent;B=P.parents[2]
x=ET.parse(B/'hardware/power_integrated_layout_14x45/power_integrated_study.xml').getroot()
values={c.attrib['ref']:c.findtext('value') for c in x.findall('./components/comp')}
for ref,val in [('R109','10k'),('R110','110k'),('R111','100k'),('R112','255k'),('R113','100k')]:
 if not values[ref].startswith(val+' '):raise RuntimeError('Value changed: '+ref)
pin_nets={(p.attrib['ref'],p.attrib['pin']):n.attrib['name'] for n in x.findall('./nets/net') for p in n.findall('node')}
expected={'/thermal/REF_EXC':[('R109','1')],'/thermal/NTC_NODE':[('R109','2'),('R110','1'),('R112','1'),('RT101','1')],'/thermal/HOT_SENSE':[('R110','2'),('R111','1'),('U105','3')],'/thermal/COLD_SENSE':[('R112','2'),('R113','1'),('U105','4')],'GND':[('R111','2'),('R113','2'),('RT101','2'),('U105','2')]}
for net,pins in expected.items():
 for pin in pins:
  if pin_nets.get(pin)!=net:raise RuntimeError('Topology changed: '+str(pin))
# Vishay material-9 polynomial used by design; inherited NTC tolerance assumption.
# This audit does not qualify purchased parts or thermal bonding.
Berror={10:.53,20:.17,30:.17,45:.63}
def resistance(temp,r,b):
 t=temp+273.15
 return 10000*math.exp(-14.6337+4791.842/t-115334/t**2-3.730535e6/t**3)*(1+r*.02)*(1+b*Berror[temp]/100)
def solve(v,rntc,rs,ia,ib,gntc=0,ga=0,gb=0):
 # NTC node N, INA+ node A, INB- node B; comparator ground defines 0V.
 rf,ra,rb,rc,rd=rs
 M=np.array([[1/rf+1/rntc+1/ra+1/rc,-1/ra,-1/rc],[-1/ra,1/ra+1/rb,0],[-1/rc,0,1/rc+1/rd]])
 rhs=np.array([v/rf+gntc/rntc,ga/rb-ia,gb/rd-ib])
 return np.linalg.solve(M,rhs)
nom=[10000,110000,100000,255000,100000]
outputs={}
for name,rails in [('published_conditional',[2.34,2.53]),('specified_REF_DC_terms_only',[2.4961222693600433,2.5038777306399562])]:
 mins={k:(float('inf'),None) for k in ['cold_recover20','hot_recover30','cold_inhibit10','hot_inhibit45']};count=0
 for corner in it.product(rails,*([[-.002,.002]]*5),[-25e-9,25e-9],[-15e-9,15e-9],[-1,1],[-1,1]):
  v,*z=corner;rs=[a*(1+q) for a,q in zip(nom,z[:5])];ia,ib,r,b=z[5:];count+=1
  for key,temp,pin,th,sign in [('cold_recover20',20,2,.387,-1),('hot_recover30',30,1,.404,1),('cold_inhibit10',10,2,.404,1),('hot_inhibit45',45,1,.387,-1)]:
   y=solve(v,resistance(temp,r,b),rs,ia,ib);margin=sign*(y[pin]-th)
   if margin<mins[key][0]:mins[key]=(margin,dict(v=v,rs=rs,ia=ia,ib=ib,r=r,b=b,temp=temp,pin=pin,sign=sign,threshold=th))
 report={}
 for key,(margin,c) in mins.items():
  rn=resistance(c['temp'],c['r'],c['b']);v=c['v'];rs=c['rs'];ia=c['ia'];ib=c['ib'];pin=c['pin'];base=solve(v,rn,rs,ia,ib)[pin]
  gains={}
  for field in ['reference_V','ntc_return_V','divider_A_return_V','divider_B_return_V','extra_input_A_A','extra_input_B_A']:
   step=1e-6 if field.endswith('_V') else 1e-12
   y=solve(v+(step if field=='reference_V' else 0),rn,rs,ia+(step if field=='extra_input_A_A' else 0),ib+(step if field=='extra_input_B_A' else 0),gntc=step if field=='ntc_return_V' else 0,ga=step if field=='divider_A_return_V' else 0,gb=step if field=='divider_B_return_V' else 0)[pin]
   gain=(y-base)/step;gains[field]={'input_gain':gain,'margin_erasing_extra_magnitude':margin/abs(gain) if gain else None,'harmful_sign':-c['sign']*(1 if gain>0 else -1)}
  report[key]={'margin_V':margin,'worst_corner':c,'sensitivities':gains}
 outputs[name]={'parameter_corners':count,'cases':report}
if abs(outputs['published_conditional']['cases']['cold_recover20']['margin_V']-.001167450282401894)>1e-12:raise RuntimeError('Independent reproduction disagrees')
(P/'threshold_result.json').write_text(json.dumps(outputs,indent=2)+'\n')
print(json.dumps({name:{key:val['margin_V'] for key,val in v['cases'].items()} for name,v in outputs.items()},indent=2))
