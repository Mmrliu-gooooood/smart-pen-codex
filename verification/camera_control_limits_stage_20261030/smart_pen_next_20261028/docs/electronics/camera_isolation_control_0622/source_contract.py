from pathlib import Path
import hashlib,json,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent;R=D.parents[2];S=R/'hardware/imu_control_native_0522/checks/candidate/netlist.xml';r=E.parse(S)
comps={c.get('ref'):c for c in r.findall('.//components/comp')};nets={n.get('name'):{(v.get('ref'),v.get('pin')):v.get('pinfunction') for v in n.findall('node')}for n in r.findall('.//nets/net')}
expect={'CAM_ISO_OE_N':{('Q201','3'):'D',('R203','1'):'1',('U201','22'):'OE_N',('U202','14'):'2OE_N',('U202','15'):'1OE_N',('U203','14'):'2OE_N',('U203','15'):'1OE_N'},'CAM_IO_EN':{('JP201','1'):'1',('R107','1'):'1',('U101','48'):'GPIO42_MTMS'},'IO_ENABLE_LINK':{('JP201','2'):'2',('R201','1'):'1'},'ISO_GATE':{('Q201','1'):'G',('R201','2'):'2',('R202','1'):'1'},'SCCB_EN_SAFE':{('R204','2'):'2',('R205','1'):'1',('U204','5'):'EN'}}
def req(c,m):
 if not c:raise RuntimeError(m)
for n,e in expect.items():req(nets[n]==e,n)
values={'R203':'10k 1%','R201':'1k 1%','R202':'100k 1%','R107':'100k 1%','R204':'100R 1%','R205':'4.7k 1%','Q201':'PMV30UN2','U201':'SN74AXC8T245PWR','U202':'SN74AXC4T245PWR','U203':'SN74AXC4T245PWR','U204':'TCA9517DGKR','JP201':'DNP_IO_COMMISSION'}
for ref,v in values.items():req(comps[ref].findtext('value')==v,ref)
for ref,pin in [('R203','2'),('U201','1'),('U202','1'),('U203','1'),('U204','8')]:req((ref,pin)in nets['3V3_AON'],'AON '+ref)
for ref,pin in [('U201','23'),('U201','24'),('U202','16'),('U203','16'),('U204','1')]:req((ref,pin)in nets['SENS_VIO_1V8'],'SENS '+ref)
for ref,pin in [('Q201','2'),('R202','2'),('R107','2'),('R205','2')]:req((ref,pin)in nets['GND'],'GND '+ref)
print(json.dumps({'status':'EXACT_EXPORTED_SOURCE_MATCH_NOT_HARDWARE_QUALIFICATION','source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'values':values,'nets':{n:[{'ref':a,'pin':b,'function':v}for(a,b),v in d.items()]for n,d in expect.items()},'MCU_GPIO42_enable_path_requires_open_JP201_to_be_commissioned':True,'OE_pins_active_low_referenced_to_AON':True,'TCA_EN_active_high_referenced_to_AON_VCCB':True,'conditional_screens':{'TCA_30uA_R205_max_V':30e-6*4700*1.01,'OE_sink_R203_max_A_at3V6':3.6/(10000*.99),'Q201_gate_100nA_R202_max_V_at_datasheet_25C_only':100e-9*100000*1.01},'limits':['No source or component value edits','Manufacturer specifications do not establish real board leakage, temperature, GPIO reset or firmware correctness','Firmware provider remains NULL; no runtime enable performed']},indent=2))
