import os
os.environ["XDG_CONFIG_HOME"]="/tmp/rf-independent/config"
os.environ["XDG_CACHE_HOME"]="/tmp/rf-independent/cache"
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E,copy,sys
D=Path(__file__).resolve().parent;TAIL=D/'tail.xml'
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def source(file):
 x=E.parse(file);c={a.get('ref'):a for a in x.findall('./components/comp')};n={(a.get('ref'),a.get('pin')):net.get('name') for net in x.findall('./nets/net') for a in net};return c,n
def props(c):return {'value':c.findtext('value'),'footprint':c.findtext('footprint'),'symbol_uuid':c.findtext('tstamps'),'libsource':c.find('libsource').attrib,'sheetpath':c.find('sheetpath').attrib,'properties':sorted((p.get('name'),p.get('value')) for p in c.findall('property'))}
a,an=source(D/'previous_master.xml');m,mn=source(D/'system_master_fresh.xml');p,pn=source(D/'fresh.xml');f,fn=source(D/'fixture_projection_fresh.xml');tail,tn=source(TAIL)
require(set(m)==set(a)|{'JF1'} and len(mn)==383,'wrong master composition')
require(all(mn.get(k)==v for k,v in an.items()),'old endpoint identity changed')
require({k:v for k,v in mn.items() if k not in an}=={('JF1','1'):'CHIP_EN',('JF1','2'):'BOOT_N',('JF1','3'):'GND'},'fixture interface mismatch')
for ref in a:
 before,after=props(a[ref]),props(m[ref])
 if ref not in ['SW101','SW102']:require(before==after,'unrelated source attributes changed '+ref)
 else:
  require(before['value']==after['value'] and before['footprint']==after['footprint'] and before['symbol_uuid']==after['symbol_uuid'] and before['libsource']==after['libsource'],'switch identity changed')
  require(after['sheetpath']['names']=='/recovery_fixture/','switch not truly allocated to fixture sheet')
remove={'J101','U102','D101','R110','R111','J102','J201','SW101','SW102','JF1'}
require(set(p)==set(m)-remove and len(p)==83 and len(pn)==303,'wrong main source projection')
require(pn=={k:v for k,v in mn.items() if k[0] not in remove},'main pin map changed')
require(set(f)=={'SW101','SW102','JF1'} and len(fn)==7,'wrong fixture composition')
require(fn=={k:v for k,v in mn.items() if k[0] in f},'fixture pin map changed')
for ref in p:require(props(p[ref])==props(m[ref]),'projection attribute mismatch '+ref)
for ref in f:require(props(f[ref])==props(m[ref]),'fixture attribute mismatch '+ref)
require({pin:pn['J108',pin] for pin in ['1','2','3']}=={'1':'CHIP_EN','2':'BOOT_N','3':'GND'},'actual J108 identity lost')
require({pin:pn['J109',pin] for pin in ['1','2','3']}=={'1':'USB_DP','2':'USB_DM','3':'GND'},'USB J109 identity lost')
require(pn['AE101','2'].startswith('unconnected-'),'antenna NC lost')
for ref in ['C106','C107']:require(p[ref].findtext('footprint')=='Capacitor_SMD:C_0402_1005Metric' and p[ref].find("property[@name='dnp']") is not None,'0402/DNP lost')
require(pn['U101','52']==pn['R105','1']=='STRAP_GPIO46' and pn['R105','2']=='GND','GPIO46 source condition changed')
def ownership(main,fixture,usb):
 require(not(set(main)&set(fixture) or set(main)&set(usb) or set(fixture)&set(usb)),'duplicate physical ownership')
 require({'SW101','SW102'}<=set(fixture) and not({'SW101','SW102'}&set(main)),'wrong selected switch ownership')
 require({'J103','J104','J105','J202'}<=set(main),'unresolved handoff hidden')
 require(set(fixture)=={'SW101','SW102','JF1'},'fixture active or extra interface added')
ownership(p,f,tail)
neg=[]
for name,mm,ff,tt in [('duplicate_switch',set(p)|{'SW101'},set(f),set(tail)),('hide_sensor',set(p)-{'J202'},set(f),set(tail)),('lose_switch',set(p),set(f)-{'SW102'},set(tail)),('add_driver',set(p),set(f)|{'U999'},set(tail))]:
 try:ownership(mm,ff,tt)
 except RuntimeError:neg.append(name)
 else:raise RuntimeError('invalid ownership accepted '+name)

import pcbnew as k
b=k.LoadBoard(str(D/'native_snapshot/mainboard_revD.kicad_pcb'));fps={z.GetReference():z for z in b.GetFootprints()}
contract=json.loads((D/'native_snapshot/verification/source_v3_fixture_handoff_contract.json').read_text())
for row in contract['reference_J108_pads']:
 pad=next(z for z in fps['J108'].Pads() if z.GetNumber()==row['pin'])
 require(pad.GetNetname()==row['net'] and pad.GetPosition().x==k.FromMM(row['x_mm']) and pad.GetPosition().y==k.FromMM(row['y_mm']),'Fixture geometry changed')
 require([b.GetLayerName(l) for l in pad.GetLayerSet().Seq() if l in [k.F_Cu,k.In1_Cu,k.In2_Cu,k.In3_Cu,k.In4_Cu,k.B_Cu]]==row['copper_layers'],'Fixture side mismatch')
owned=json.loads((D/'native_snapshot/verification/source_v3_system_ownership.json').read_text())['rows']
require(len(owned)==95 and len({r['reference'] for r in owned})==95,'Ownership duplicate')
for rows,owner in [(p,'mainboard'),(f,'shared_passive_recovery_fixture'),(tail,'usb_tail_shared_functions')]:
 require({r['reference'] for r in owned if r['owner']==owner}==set(rows),'Ownership allocation differs')
for root in ['system_master','fixture_projection']:require((D/(root+'_erc.exit')).read_text().strip()=='0','Fresh source ERC failed')
ports={r:{pin:net for (ref,pin),net in pn.items() if ref==r} for r in ['J103','J104','J105','J106','J107','J108','J109','J202','JP201','JP202']}
print(json.dumps({'master_entities':len(m),'master_endpoints':len(mn),'selected_entities':len(p),'selected_endpoints':len(pn),'fixture_entities':len(f),'fixture_endpoints':len(fn),'ownership_total':len(owned),'old_380_endpoints_preserved':True,'ownership_negative_rejections':neg,'fixture_reference_geometry_matches_actual_selected':True,'ports':ports},indent=2))
