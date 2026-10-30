# MAINBOARD_RECOVERY_20261030_0203

**只读恢复索引 / NOFAB / NOPOWER。当前研究板 ca66：0 violations /143 unconnected /0 parity。不是正式9a03基线替换，也不是可下单版本。**

## 近期局部供电阶段串联

- 上一恢复索引 `mcu_recovery_index_0125`：77537，0/181/0，AON14/39、GND39/102。
- 局部 translator 去耦阶段（近期 r16/r17 交付关联资料之一）：`hardware/translator_domain_candidate_0130`，7c816，0/149/0，AON23/39、GND57/102，SENS外部输入仍1/12。仅交换C207/C208位置，保留源供电域。
- 全SENS外部参考树阶段：`sens_tree_plan_0149`两类候选拒绝；`sens_joint_plan_0155`单一绕端点模型；`hardware/sens_tree_candidate_0158` ca66，0/143/0，SENS12/12，AON/GND保持。37对象、无其它旧铜/FP变更，重放/原版恢复/负例与真实填铜验证已归档。
- 本页按实际本地SHA串联近期r16/r17工作内容，**不据此推定远端提交、审查状态或交付批次号映射**；独立审查与远端收据以主任务记录为准。

## 数字和合法开路边界

143是KiCad未连条目，不是143个焊盘。当前49个net有未连项；精确端点UUID及实际组件见`recovery.json`。16个AON、45个GND物理pad尚未接入J106核心，都是当前源同网真实未连，不能与跨器件合法隔离混为一谈。

- JP301.1=CAM_3V3_PRELINK，JP301.2=CAM_3V3_SW，源属性DNP / OPEN / DO NOT BRIDGE。各侧已有独立连通分量且无该net未连项；**严禁为“完成电源”跨JP301短接**。
- U101保留/PSRAM/NC源标注、U202.7和U203.10未用输出、U501.11(INT2)、AE101.2源标注未连，以及J202两个无号机械pad，不是需要串接的目标。此处复述源意图，不重新批准芯片NC接法。
- **UNUSED_A_INPUT与UNUSED_B_INPUT并非合法悬空输出**：它们分别需要U203.7↔R207.1、U202.10↔R206.1的输入偏置连接，当前各1未连。不能看到UNUSED就忽略或拿该net腾路。
- 12条头端DVP/时钟链的J202↔AXC主要链已通，但每net尚有独立偏置电阻pad；不得把“12条链已恢复”等同整net全通。
- 外部SENS12/12仅表示参考铜树，未建立外部电源能力、上电顺序/反灌安全；没有内部1.8V源。

## 按实际源用途分类

|类别|未连条目|net数|
|---|---:|---:|
|power_ground_or_commissioned_output|61|2|
|pickup_IMU_or_pressure_side|5|3|
|battery_measurement_port|1|1|
|camera_gate_SCCB_or_mode_control|24|9|
|MCU_to_translator_DVP_or_clock|24|12|
|pressure_pen_contact|4|2|
|head_DVP_reference_or_control|20|16|
|required_unused_input_bias_NOT_open_output|2|2|
|host_USB_boot_control|2|2|

## 未连net与实际pad分量

每个`;`分隔一个物理连通分量。重复EP焊盘以UUID后缀区分，详细source pinfunction/pintype保留在JSON。旧9a03候选对象清单仅为读取库存，不代表可以直接复用；变位pad清单逐net记录，仍需整网几何/回流/源一致性检查。

|net|CLI未连|实际pad分量|旧9a03铜对象数 / 变位pad数|
|---|---:|---|---:|
|3V3_AON|16|C102.1, C104.1, C105.1, C201.1, C203.1, C205.1, C207.1, J106.2, R101.2, R102.2, R103.2, R240.2, R241.2, U101.20, U101.46, U101.55, U101.56, U201.1, U202.1, U203.1, U203.2, U203.3, U204.8; C103.1; C301.1; C501.1; C502.1; C503.1; R203.2; R501.1; R502.1; R503.1; U101.2; U101.3; U301.1; U501.10; U501.2; U501.3; U501.9|188 / 9|
|AON_I2C_SCL|2|R501.2; U101.10; U501.1|94 / 0|
|AON_I2C_SDA|2|R502.2; U101.11; U501.4|202 / 0|
|BATTERY_ADC|1|J105.1; U101.9|0 / 1|
|CAM_BUS_EN|2|JP202.1; R108.1; U101.37|89 / 0|
|CAM_D0|2|R210.1; U101.12; U201.3|43 / 1|
|CAM_D1|2|R211.1; U101.13; U201.4|60 / 1|
|CAM_D2|2|R212.1; U101.14; U201.5|136 / 1|
|CAM_D3|2|R213.1; U101.15; U201.6|105 / 1|
|CAM_D4|2|R214.1; U101.16; U201.7|53 / 1|
|CAM_D5|2|R215.1; U101.17; U201.8|166 / 1|
|CAM_D6|2|R216.1; U101.18; U201.9|154 / 1|
|CAM_D7|2|R217.1; U101.19; U201.10|109 / 1|
|CAM_HREF|2|R220.1; U101.23; U202.6|185 / 1|
|CAM_IO_EN|2|JP201.1; R107.1; U101.48|157 / 0|
|CAM_ISO_OE_N|6|Q201.3; R203.1; U201.22; U202.14; U202.15; U203.14; U203.15|140 / 5|
|CAM_PCLK|2|R218.1; U101.21; U202.4|117 / 2|
|CAM_PWDN_UART_RX|3|J104.2; R223.1; U101.50; U203.6|115 / 2|
|CAM_PWR_EN|3|R106.1; R302.1; TP301.1; U101.47|119 / 0|
|CAM_RESET_UART_TX|3|J104.1; R222.1; U101.49; U203.5|136 / 2|
|CAM_SCL|2|R240.1; U101.44; U204.7|110 / 0|
|CAM_SDA|2|R241.1; U101.45; U204.6|186 / 0|
|CAM_VSYNC|2|R219.1; U101.22; U202.5|191 / 2|
|CAM_XCLK|2|R221.1; U101.43; U203.4|167 / 2|
|CONTACT|1|J103.1; R504.2|0 / 0|
|GND|45|C101.2, C102.2, C103.2, C104.2, C105.2, C106.2, C107.2, C201.2, C202.2, C203.2, C204.2, C205.2, C206.2, C207.2, C208.2, C301.2, J106.3, J108.3, J109.3, J202.24, J301.2, Q201.2, R105.2, R106.2, R107.2, R108.2, R109.2, R202.2, R205.2, R207.2, R210.2, R211.2, R212.2, R213.2, R215.2, R217.2, R236.2, U101.57#0de17810-11f5-4886-9396-ef3db98ad5e0, U101.57#32bb485d-f189-426e-b0af-d376c218a5c0, U101.57#4c205a6e-a341-4388-a479-119936dba9f3, U101.57#9cfb0dae-5f02-469b-b604-732278f16482, U101.57#a4284ff2-c785-4218-9745-31552753482d, U101.57#e00fb0ca-2bab-41b9-8199-a062b6cf930c, U101.57#e2374ec6-da24-4723-8e2c-f08cd507c2cf, U101.57#fb757f71-448f-4a52-b6db-6549ae1617d0, U101.57#fd09fc28-178f-4ef9-b475-b126dc663302, U201.11, U201.12, U201.13, U201.2, U202.2, U202.3, U202.8, U202.9, U203.8, U203.9, U204.4; C302.2; C303.2; C501.2; C502.2; C503.2; C504.2; J103.2; J104.3; J105.2; J107.3; J202.1; J202.10; J202.13; J202.17; J202.4; J202.7; R104.2; R206.2; R214.2; R216.2; R218.2; R219.2; R220.2; R221.2; R222.2; R223.2; R224.2; R225.2; R226.2; R227.2; R228.2; R229.2; R230.2; R231.2; R232.2; R233.2; R234.2; R235.2; R237.2; R301.2; U301.2; U501.5; U501.6; U501.7; U501.8|545 / 46|
|IO_ENABLE_LINK|1|JP201.2; R201.1|11 / 0|
|NIB_CONTACT_N|3|C504.1; R503.2; R504.1; U101.7|2 / 0|
|PICKUP_INT_N|1|U101.6; U501.12|89 / 0|
|SENS_D0|1|J202.2, U201.21; R224.1|27 / 2|
|SENS_D1|1|J202.3, U201.20; R225.1|14 / 2|
|SENS_D2|1|J202.5, U201.19; R226.1|14 / 2|
|SENS_D3|1|J202.6, U201.18; R227.1|16 / 2|
|SENS_D4|1|J202.8, U201.17; R228.1|19 / 2|
|SENS_D5|1|J202.9, U201.16; R229.1|20 / 2|
|SENS_D6|1|J202.11, U201.15; R230.1|18 / 2|
|SENS_D7|1|J202.12, U201.14; R231.1|21 / 2|
|SENS_EXTCLK|1|J202.18, U203.13; R235.1|14 / 2|
|SENS_HREF|1|J202.16, U202.11; R234.1|20 / 2|
|SENS_PCLK|1|J202.14, U202.13; R232.1|17 / 2|
|SENS_SCL|2|J202.21; R242.1; U204.2|83 / 0|
|SENS_SDA|2|J202.22; R243.1; U204.3|123 / 0|
|SENS_TRIG_IN|2|J202.20; R237.1; U203.11|55 / 1|
|SENS_VSYNC|1|J202.15, U202.12; R233.1|14 / 2|
|SENS_XSHUTDN_N|2|J202.19; R236.1; U203.12|49 / 1|
|UNUSED_A_INPUT|1|R207.1; U203.7|39 / 1|
|UNUSED_B_INPUT|1|R206.1; U202.10|16 / 2|
|USB_EN1|1|J107.1; U101.24|296 / 1|
|USB_EN2|1|J107.2; U101.27|160 / 1|

## 3V3_AON 核心外物理pads（16）

|Pad|源pinfunction / pintype|器件值|来源sheet|
|---|---|---|---|
|C103.1|1 / passive|100n|schematic/mcu_core.kicad_sch|
|C301.1|源未命名 passive pin（不是PCB空函数猜测） / passive|10uF 10V X7R|schematic/camera_gate_on_main.kicad_sch|
|C501.1|1 / passive|100nF 16V X7R +/-10%|schematic/pickup_on_main.kicad_sch|
|C502.1|1 / passive|100nF 16V X7R +/-10%|schematic/pickup_on_main.kicad_sch|
|C503.1|1 / passive|10uF 10V X7R +/-10%|schematic/pickup_on_main.kicad_sch|
|R203.2|2 / passive|10k 1%|schematic/controls_sccb.kicad_sch|
|R501.1|1 / passive|10k 1%|schematic/pickup_on_main.kicad_sch|
|R502.1|1 / passive|10k 1%|schematic/pickup_on_main.kicad_sch|
|R503.1|1 / passive|100k 1%|schematic/pickup_on_main.kicad_sch|
|U101.2|VDD3P3 / power_in|ESP32-S3-PICO-1-N8R8|schematic/mcu_core.kicad_sch|
|U101.3|VDD3P3 / power_in|ESP32-S3-PICO-1-N8R8|schematic/mcu_core.kicad_sch|
|U301.1|VIN / power_in|TPS22918DBVR|schematic/camera_gate_on_main.kicad_sch|
|U501.10|VDDIO / power_in|LIS2DW12TR|schematic/pickup_on_main.kicad_sch|
|U501.2|CS / input|LIS2DW12TR|schematic/pickup_on_main.kicad_sch|
|U501.3|SA0 / input|LIS2DW12TR|schematic/pickup_on_main.kicad_sch|
|U501.9|VDD / power_in|LIS2DW12TR|schematic/pickup_on_main.kicad_sch|

## GND 核心外物理pads（45）

|Pad|源pinfunction / pintype|器件值|来源sheet|
|---|---|---|---|
|C302.2|源未命名 passive pin（不是PCB空函数猜测） / passive|1uF 10V X7R|schematic/camera_gate_on_main.kicad_sch|
|C303.2|源未命名 passive pin（不是PCB空函数猜测） / passive|1nF 25V C0G|schematic/camera_gate_on_main.kicad_sch|
|C501.2|2 / passive|100nF 16V X7R +/-10%|schematic/pickup_on_main.kicad_sch|
|C502.2|2 / passive|100nF 16V X7R +/-10%|schematic/pickup_on_main.kicad_sch|
|C503.2|2 / passive|10uF 10V X7R +/-10%|schematic/pickup_on_main.kicad_sch|
|C504.2|2 / passive|1n C0G|schematic/pickup_on_main.kicad_sch|
|J103.2|2 / passive|DRY CONTACT PADS|schematic/pickup_on_main.kicad_sch|
|J104.3|3 / passive|UART_SERVICE_CAMERA_OFF_ONLY|schematic/physical_interfaces.kicad_sch|
|J105.2|2 / passive|ADC_SAFE_FRONTEND_LINK_NOT_RAW_BATTERY|schematic/physical_interfaces.kicad_sch|
|J107.3|3 / passive|CHARGER_MODE|schematic/usb_entry.kicad_sch|
|J202.1|1 / passive|5034802400_NEW_24PIN_SENSOR_HANDOFF|schematic/physical_interfaces.kicad_sch|
|J202.10|10 / passive|5034802400_NEW_24PIN_SENSOR_HANDOFF|schematic/physical_interfaces.kicad_sch|
|J202.13|13 / passive|5034802400_NEW_24PIN_SENSOR_HANDOFF|schematic/physical_interfaces.kicad_sch|
|J202.17|17 / passive|5034802400_NEW_24PIN_SENSOR_HANDOFF|schematic/physical_interfaces.kicad_sch|
|J202.4|4 / passive|5034802400_NEW_24PIN_SENSOR_HANDOFF|schematic/physical_interfaces.kicad_sch|
|J202.7|7 / passive|5034802400_NEW_24PIN_SENSOR_HANDOFF|schematic/physical_interfaces.kicad_sch|
|R104.2|2 / passive|10k 1%|schematic/mcu_core.kicad_sch|
|R206.2|2 / passive|10k 1%|schematic/dvp_translation.kicad_sch|
|R214.2|2 / passive|100k 1%|schematic/safe_bias_interfaces.kicad_sch|
|R216.2|2 / passive|100k 1%|schematic/safe_bias_interfaces.kicad_sch|
|R218.2|2 / passive|100k 1%|schematic/safe_bias_interfaces.kicad_sch|
|R219.2|2 / passive|100k 1%|schematic/safe_bias_interfaces.kicad_sch|
|R220.2|2 / passive|100k 1%|schematic/safe_bias_interfaces.kicad_sch|
|R221.2|2 / passive|100k 1%|schematic/safe_bias_interfaces.kicad_sch|
|R222.2|2 / passive|100k 1%|schematic/safe_bias_interfaces.kicad_sch|
|R223.2|2 / passive|100k 1%|schematic/safe_bias_interfaces.kicad_sch|
|R224.2|2 / passive|100k 1%|schematic/safe_bias_interfaces.kicad_sch|
|R225.2|2 / passive|100k 1%|schematic/safe_bias_interfaces.kicad_sch|
|R226.2|2 / passive|100k 1%|schematic/safe_bias_interfaces.kicad_sch|
|R227.2|2 / passive|100k 1%|schematic/safe_bias_interfaces.kicad_sch|
|R228.2|2 / passive|100k 1%|schematic/safe_bias_interfaces.kicad_sch|
|R229.2|2 / passive|100k 1%|schematic/safe_bias_interfaces.kicad_sch|
|R230.2|2 / passive|100k 1%|schematic/safe_bias_interfaces.kicad_sch|
|R231.2|2 / passive|100k 1%|schematic/safe_bias_interfaces.kicad_sch|
|R232.2|2 / passive|100k 1%|schematic/safe_bias_interfaces.kicad_sch|
|R233.2|2 / passive|100k 1%|schematic/safe_bias_interfaces.kicad_sch|
|R234.2|2 / passive|100k 1%|schematic/safe_bias_interfaces.kicad_sch|
|R235.2|2 / passive|100k 1%|schematic/safe_bias_interfaces.kicad_sch|
|R237.2|2 / passive|100k 1%|schematic/safe_bias_interfaces.kicad_sch|
|R301.2|源未命名 passive pin（不是PCB空函数猜测） / passive|100k 1%|schematic/camera_gate_on_main.kicad_sch|
|U301.2|GND / power_in|TPS22918DBVR|schematic/camera_gate_on_main.kicad_sch|
|U501.5|NC / passive|LIS2DW12TR|schematic/pickup_on_main.kicad_sch|
|U501.6|GND / power_in|LIS2DW12TR|schematic/pickup_on_main.kicad_sch|
|U501.7|RES / passive|LIS2DW12TR|schematic/pickup_on_main.kicad_sch|
|U501.8|GND / power_in|LIS2DW12TR|schematic/pickup_on_main.kicad_sch|

## 下一轮设计优先级（仅规划建议）

1. **完整主供电与对应地回流**：先审U101.2/.3模拟供电、C103，以及U301开关电源入口、U501拾取/IMU供电和C501–503去耦；把16 AON与45 GND按子系统成组规划，不能先拉电源后留下回流。既有EP八个via-in-pad、23.8µm孔边DFM问题仍未解决。
2. **MCU↔AXC侧12条DVP/时钟整组**：实际net叫CAM_D0–7/CAM_HREF/CAM_VSYNC/CAM_PCLK/CAM_XCLK，不是SENS头侧。每net当前3个pad分量/2个未连，必须含偏置/串接源器件，不仅拉主信号端点。保留已完成头侧链与SENS参考树。
3. **控制/接口/落笔**：CAM_ISO_OE_N、BUS/IO/PWR使能、SCCB双域、RESET/PWDN复用端口、USB使能、AON I2C/PICKUP_INT、CONTACT→R504→NIB_CONTACT_N及滤波/上拉。`CONTACT`和`NIB_CONTACT_N`是不同net，不得跨R504短接。
4. 电池ADC与实际外部供电/相机匹配，再做全板电气、DFM、机械复查与装配测试。旧9a03线路只是候选库存；之前47对象SENS支路已证明因新布局发生冲突，严禁按旧net盲贴。

本轮无native编辑、无新增铜、无采购、无推送。
