from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;r=json.loads((O/'inventory.json').read_text())
def domain(n):
 if n=='GND':return '共地；当前33物理分量'
 if n=='3V3_AON':return 'AON 3.3V；原理图电源网'
 if n=='SENS_VIO_1V8':return '外部J202.23传感器VIO 1.8V；不是板上已验证供电源'
 if n.startswith('SENS_')or n=='UNUSED_B_INPUT':return 'SENS VIO；AXC B侧 / TCA A侧'
 if n.startswith('CAM_3V3'):return '相机3.3V开关输出；JP301隔离前/后不同网'
 if n=='VBUS_5V':return '外部VBUS 5V；孤立接口，不代表充电完成'
 if n.startswith('USB_D'):return 'USB物理层差分；不是普通GPIO电源网'
 if n=='BATTERY_ADC':return '外部模拟输入到AON MCU；输入幅值/保护未由连通性证明'
 if n.startswith('RF_'):return 'RF网络；不是GPIO'
 if n.startswith('unconnected-'):return '源显式未连/NC；不得为消除清单而接线'
 if n in ['CAM_CT','CAM_QOD','CAM_ON']:return 'AON供电TPS22918专用控制端；不据名称假设数字域'
 return 'AON MCU/逻辑侧；AXC A侧 / TCA B侧（按器件源电源映射）'
lines=['# 每网物理分量 / 源引脚功能 / 电源域','', '基准PCB `63d460c70405e1c1042f5e150a7fe5c5c5c32346fb37209a386cf03a1eacdd7c`。这是清单，不是完成路由。每个方括号是一组实际有限铜相连的物理焊盘；MCU EP重复焊盘保留UUID。源引脚来自embedded lib_symbols + 导出netlist/libparts三方匹配，未读取GetPinFunction；被动无名引脚的源 `~` 与导出空名归一化，未编造GPIO。全部源映射零不一致。','', '| 网 | DRC未连 / 最少分量连接 | 电源域 | 实际源封装引脚=功能 | 物理分量 |','|---|---:|---|---|---|']
for n in r['nets']:
 terms='; '.join(t['ref']+'.'+t['package_pin']+'='+ (t['source_pin_function']or '(无名被动脚)')for t in n['source_terminals']);cs=' '.join('['+', '.join(c)+']'for c in n['physical_components']);lines.append(f"| {n['net']} | {n['drc_missing_connections']} / {n['minimum_component_joins']} | {domain(n['net'])} | {terms} | {cs} |")
(O/'NET_TABLE.md').write_text('\n'.join(lines)+'\n')
