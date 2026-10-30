# 0628剩余96项：只读规划，NO FAB / NO POWER

## 实测结论
- 基准已独审PCB SHA `63d460c70405e1c1042f5e150a7fe5c5c5c32346fb37209a386cf03a1eacdd7c`，没有修改native、源、封装或铜。
- 96条原生DRC未连接，按真实item UUID回查net；独立有限铜分量最少连接数之和也为96。不是96个网，也不是96根唯一指定走线。
- 每网全部物理分量、实际封装脚、源功能和电源域见 `NET_TABLE.md`；可复算JSON含坐标、物理pad UUID、原始DRC各项、embedded source映射见 `inventory.json`。
- GPIO数字不是封装脚号：例如CAM_D0是U101封装12=GPIO7；CAM_PCLK封装21=GPIO15_XTAL32K_P；CAM_PWR_EN封装47=GPIO41_MTDI；CAM_BUS_EN封装37=GPIO47_SPICLK_P。逐一比对embedded lib_symbols、netlist libparts、net node功能，零不一致。无名被动脚明确保留无名，不拿空PCB属性猜引脚。

## 96项准确分解
| 组 | 数量 | 解释 |
|---|---:|---|
| GND |32|33分量：70物理pad核心 + 32单独pad；总102物理pad|
| MCU侧DVP |22|CAM_D0…D7、PCLK、VSYNC、HREF各2；各网MCU、AXC、偏置电阻三独立分量|
| SENS侧DVP偏置 |11|SENS_D0…D7、PCLK、VSYNC、HREF各1；已有J202↔AXC主路，偏置电阻顶端尚未并入|
| CAM_PWR_EN / CAM_BUS_EN |5|3 + 2；控制网，避开并行Schmitt工作|
| CAM_XCLK |2|MCU/AXC/偏置电阻三分量|
| SCCB两侧 |8|CAM_SCL、CAM_SDA、SENS_SCL、SENS_SDA各2|
| MCU reset/UART复用 |6|CAM_RESET_UART_TX、CAM_PWDN_UART_RX各3；含J104支路|
| SENS TRIG/XSHUTDN |4|SENS_TRIG_IN、SENS_XSHUTDN_N各2|
| UNUSED输入偏置 |2|UNUSED_A_INPUT、UNUSED_B_INPUT各1；不是NC输出|
| USB模式接口 |2|USB_EN1、USB_EN2各1；不是USB D+/D−|
| BATTERY_ADC |1|J105.1与U101.9(GPIO4)未接|
| SENS_EXTCLK偏置 |1|J202.18↔U203.13主路已接，但R235.1未接|
| **合计** |**96**|所有类别互斥；GND项单列避免重复计数|

32个GND孤立端：J104.3、J105.2、J107.3；J202.1/.4/.7/.10/.13/.17；R104.2、R206.2、R214.2、R216.2、R218.2、R219.2、R220.2、R221.2、R222.2、R223.2、R224.2、R225.2、R226.2、R227.2、R228.2、R229.2、R230.2、R231.2、R232.2、R233.2、R234.2、R235.2、R237.2。

## 下一最小独立候选组（不是已证明可布通）
**优先提出单项GND组：R216.2→已验证核心GND。** R216.2=(8.325,28.0)mm，已入核心R212.2=(8.325,26.0)mm，中心距2.000mm。坐标邻近只用于选取规划窗口，不是允许直线连接的证明。应先评估局部F/B短连或合规短支路接地过孔；保留全部旧铜/FP/源，不走长GND层信号、不穿MCU/AXC焊盘、不得用孔盘侵入同网pad作为“捷径”。若净空/现有铜阻挡则放弃该候选，不移动旧对象抢通。

选择理由：只合并一个已知孤立GND分量，避开Q201/R202、新cap及CAM控制网，不触碰时钟主路/机械接口；比一次完成11条MCU DVP更可独立验证。预期只有在实际路由、回填、实体分量和DRC均证明时才可称96→95；本次没有做这一步。

后续排序建议：
1. **局部偏置GND闭合**：R214、R218…等逐小组；每组需保留AON/SENS/核心GND既有分量、全部旧信号投影和历史reference损失，不把少量新增孔当成自动SI通过。
2. **R104.2模式绑带接地**：STRAP_GPIO45信号自身已连，但R104下端仍浮置。最近核心pad C106.2仅2.3305mm但在RF区，不能因近就利用RF回流路径；须优先检查RF keepout/天线和MCU区域。GPIO3/46绑带网已连，不重做。
3. **J202六个GND端**：核心已有J202.24，不能因此宣称整个连接器接地完成。先看实际FPC pad顺序/铜层/机械包络，保留数据焊盘间距与回流。不得把连接器沿边全部GND点简单跨信号短接。J202.23的SENS_VIO网络已12/12闭合，无“再接电源”缺口；真实相机接口/电压未确认仍禁上电。
4. **SENS侧偏置支路**：已有DVP主路上补R224…R234顶端，同时各自地端需完成；可以分单网小组，但这是加载现有高速线，不是“无风险短支路”。R235 clock偏置最后独立审查，必须保留既有两平面0.0017414094705mm²损失，重新测新损失和branch长度。
5. **MCU侧DVP分组规划**：D0…D7并行通道先做全总线逃线/通道占用图，再选一条作独立候选；PCLK/HREF/VSYNC与数据时序一并预算。避免先贪心布一条长线锁死其余通道。仅F/In3/B信号候选，不新增长信号切割In1/In2/In4参考面；过孔孔群和旧CAM_ON参考缺口逐项跟踪。没有全总线时序/负载/回流证明，不宣称DVP可用。
6. **USB_EN1/2 + J107.3**：模式接口不是USB差分；native B52与虚拟B70.5机械关联及J107可达性未决，先机械会签后再小组规划。BOOT_N、CHIP_EN、USB_DM/DP各自上下游网已连；不要因名字含USB/boot重布完成的铜。
7. **其余SCCB、RESET/UART、TRIG/XSHUTDN、CAM电源/总线控制**：都保持挂起避免与当前Schmitt源/局部改动冲突；待新版源冻结后重导netlist、重算差分，不把0628的pad/net清单直接移植到新版。UNUSED输入偏置也等控制邻区确认；绝不连接U202.7/U203.10等源标注未连输出。
8. **BATTERY_ADC**：仅一条缺口不代表可优先安全接通；J105.2地也未接，外部电压范围/分压保护/机械接口需确认。

## 边界和每组验收门槛
只读规划，无远端、采购、上电或打样。所有JP201/JP202/JP301保持OPEN；provider NULL。Q201、R202、新cap和控制网为并行worker保留区，本计划不安排写入。

未来每个获准路由组必须：冻结新父SHA/源和机械基准；旧铜/FP/pad-net/value零修改；实际多物理pad有限铜连通；所有pad含同网、全层孔/净距/边缘/规则区/普通courtyard检查；原项目规则全DRC/ERC/parity；回填原生多边形一次受控Unfracture；真实reference delta无扩孔排除；负向切断、byte rollback、正常/-O重放一致。清单减少不等于硬件完成。

环境记录：首次pcbnew默认配置尝试创建/home/agent/.config/kicad被只读拒绝，计算仍完成；未重试该路径，随后明确将配置定位独立/tmp重跑成功。未修改受限位置。
