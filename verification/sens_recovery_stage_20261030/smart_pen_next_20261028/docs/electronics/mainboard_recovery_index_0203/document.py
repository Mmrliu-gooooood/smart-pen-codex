from pathlib import Path
import json,collections
D=Path(__file__).resolve().parent;r=json.loads((D/'recovery.json').read_text());out=['# MAINBOARD_RECOVERY_20261030_0203','', '**只读恢复索引 / NOFAB / NOPOWER。当前研究板 ca66：0 violations /143 unconnected /0 parity。不是正式9a03基线替换，也不是可下单版本。**','', '## 近期局部供电阶段串联','', '- 上一恢复索引 `mcu_recovery_index_0125`：77537，0/181/0，AON14/39、GND39/102。','- 局部 translator 去耦阶段（近期 r16/r17 交付关联资料之一）：`hardware/translator_domain_candidate_0130`，7c816，0/149/0，AON23/39、GND57/102，SENS外部输入仍1/12。仅交换C207/C208位置，保留源供电域。','- 全SENS外部参考树阶段：`sens_tree_plan_0149`两类候选拒绝；`sens_joint_plan_0155`单一绕端点模型；`hardware/sens_tree_candidate_0158` ca66，0/143/0，SENS12/12，AON/GND保持。37对象、无其它旧铜/FP变更，重放/原版恢复/负例与真实填铜验证已归档。','- 本页按实际本地SHA串联近期r16/r17工作内容，**不据此推定远端提交、审查状态或交付批次号映射**；独立审查与远端收据以主任务记录为准。','', '## 数字和合法开路边界','', '143是KiCad未连条目，不是143个焊盘。当前49个net有未连项；精确端点UUID及实际组件见`recovery.json`。16个AON、45个GND物理pad尚未接入J106核心，都是当前源同网真实未连，不能与跨器件合法隔离混为一谈。','', '- JP301.1=CAM_3V3_PRELINK，JP301.2=CAM_3V3_SW，源属性DNP / OPEN / DO NOT BRIDGE。各侧已有独立连通分量且无该net未连项；**严禁为“完成电源”跨JP301短接**。','- U101保留/PSRAM/NC源标注、U202.7和U203.10未用输出、U501.11(INT2)、AE101.2源标注未连，以及J202两个无号机械pad，不是需要串接的目标。此处复述源意图，不重新批准芯片NC接法。','- **UNUSED_A_INPUT与UNUSED_B_INPUT并非合法悬空输出**：它们分别需要U203.7↔R207.1、U202.10↔R206.1的输入偏置连接，当前各1未连。不能看到UNUSED就忽略或拿该net腾路。','- 12条头端DVP/时钟链的J202↔AXC主要链已通，但每net尚有独立偏置电阻pad；不得把“12条链已恢复”等同整net全通。','- 外部SENS12/12仅表示参考铜树，未建立外部电源能力、上电顺序/反灌安全；没有内部1.8V源。','', '## 按实际源用途分类','', '|类别|未连条目|net数|','|---|---:|---:|']
counts=collections.Counter();num=collections.Counter()
for x in r['all_nets']:
 if x['native_unconnected_count']:counts[x['category']]+=x['native_unconnected_count'];num[x['category']]+=1
for k,v in counts.items():out.append(f'|{k}|{v}|{num[k]}|')
out+=['','## 未连net与实际pad分量','', '每个`;`分隔一个物理连通分量。重复EP焊盘以UUID后缀区分，详细source pinfunction/pintype保留在JSON。旧9a03候选对象清单仅为读取库存，不代表可以直接复用；变位pad清单逐net记录，仍需整网几何/回流/源一致性检查。','', '|net|CLI未连|实际pad分量|旧9a03铜对象数 / 变位pad数|','|---|---:|---|---:|']
for x in r['all_nets']:
 if x['native_unconnected_count']:
  out.append('|'+x['net']+'|'+str(x['native_unconnected_count'])+'|'+'; '.join(', '.join(c)for c in x['components'])+'|'+str(len(x['old_reuse_candidate']['objects']))+' / '+str(len(x['old_reuse_candidate']['changed_pad_positions_or_net']))+'|')
for net in ['3V3_AON','GND']:
 out+=['',f'## {net} 核心外物理pads（{len(r["remaining_core_pads"][net])}）','','|Pad|源pinfunction / pintype|器件值|来源sheet|','|---|---|---|---|']
 for x in sorted(r['remaining_core_pads'][net],key=lambda x:x['pad']):
  s=x['source']or{};func=s.get('pinfunction','源未命名 passive pin（不是PCB空函数猜测）');out.append('|'+x['pad']+'|'+func+' / '+s.get('pintype','未导出')+'|'+x['value']+'|'+str(x['source_sheet'])+'|')
out+=['','## 下一轮设计优先级（仅规划建议）','','1. **完整主供电与对应地回流**：先审U101.2/.3模拟供电、C103，以及U301开关电源入口、U501拾取/IMU供电和C501–503去耦；把16 AON与45 GND按子系统成组规划，不能先拉电源后留下回流。既有EP八个via-in-pad、23.8µm孔边DFM问题仍未解决。','2. **MCU↔AXC侧12条DVP/时钟整组**：实际net叫CAM_D0–7/CAM_HREF/CAM_VSYNC/CAM_PCLK/CAM_XCLK，不是SENS头侧。每net当前3个pad分量/2个未连，必须含偏置/串接源器件，不仅拉主信号端点。保留已完成头侧链与SENS参考树。','3. **控制/接口/落笔**：CAM_ISO_OE_N、BUS/IO/PWR使能、SCCB双域、RESET/PWDN复用端口、USB使能、AON I2C/PICKUP_INT、CONTACT→R504→NIB_CONTACT_N及滤波/上拉。`CONTACT`和`NIB_CONTACT_N`是不同net，不得跨R504短接。','4. 电池ADC与实际外部供电/相机匹配，再做全板电气、DFM、机械复查与装配测试。旧9a03线路只是候选库存；之前47对象SENS支路已证明因新布局发生冲突，严禁按旧net盲贴。','','本轮无native编辑、无新增铜、无采购、无推送。']
(D/'README.md').write_text('\n'.join(out)+'\n');(D.parent/'MAINBOARD_RECOVERY_20261030_0203.md').write_text('\n'.join(out)+'\n')
print('airwire sum',sum(counts.values()),'nets',sum(num.values()))
