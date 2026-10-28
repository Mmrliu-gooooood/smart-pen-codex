# 相机主控侧隔离与电平转换 — 2026-10-28新设计 / NO FAB

这次新增的是**真实元件级电路**，不是未知摄像头模块的接线保证。三个子页包含固定方向DVP翻译、硬件默认关闭控制、SCCB双向翻译和两侧悬空偏置。没有相机FPC封装或PCB；不得把旧30pin需求图当成实物映射。

## 新检查
`python3 tools/build.py`生成原生KiCad；`python3 tools/verify.py`重新调用KiCad并从真实XML核验独立手写合同，拒绝空/部分网表。当前 **56元件、203引脚、56器件值、JP1/JP2真实DNP及关键脚名均通过；ERC0错误/0警告**。已赋封装检查了焊盘编号集合，不等于landpattern、钢网或生产认可。`review.pdf`供逐页审核，无PCB/DRC声明。候选BOM价格均未报价。

## 接口与方向
- U1=SN74AXC8T245PWR：A=3V3_AON、B=SENS_VIO_1V8；DIR1=0、DIR2=0，8bit从传感器B到主控A。
- U2=SN74AXC4T245PWR：两个DIR=0，PCLK/VSYNC/HREF从B到A；剩余B输入经10k偏置地，对应A脚NC。
- U3同型号：两个DIR=1，XCLK/RESET/AUX从A到B；剩余A输入经10k偏置地，对应B脚NC。
- 所有实际DVP/控制两侧节点均有偏置，因AXC禁用输出时其输入电路仍活动。RESET语义端4.7k下拉是**候选**；芯片内置上拉阻值/模块额外驱动未知，必须测量确认低有效保持，不能仅据“外部下拉”宣称复位已安全。
- `SENS_XSHUTDN_N`仅表示已知芯片的低有效输入，`SENS_TRIG_IN`表示芯片TRIG输入。为了与已提交主控提案衔接，主控侧仍叫 `CAM_RESET_UART_TX` / `CAM_PWDN_UART_RX`；后者只是旧逻辑名字，**不证明模块存在PWDN，更不把旧FPC24直接当TRIG**。
- J1=20个主控侧语义网络，J2=18个传感器侧语义网络，均无物理连接器封装。**这里J1的针序与已提交MCU J2不相同，绝不可1:1排线直连；只能按网络名逐项接线和复核。** J2第17个语义项 `SENS_VIO_1V8` 是实际传感器IO同一条已核实1.8V电源，不能独立往未知模块注入，也不能接CAM_3V3_SW。
- 未连接旧模块pin25/26，未把LEDSTROBE输出并接到GPIO输出。独立照明使用另一个模块的GPIO48。

## 默认关闭不是口头约定
AXC所有/OE接 `CAM_ISO_OE_N`，R3=10k拉到主控3.3V。Q1 PMV30UN2下拉/OE，Gate有100k下拉。GPIO42 `CAM_IO_EN` 必须经过**开放、DNP的JP1**以及1k后才到Gate：JP1没装时，即使ROM/软件出错也不能通过此路径打开AXC。不要把CAM_IO_EN直接接低有效/OE。

SCCB的GPIO47 `CAM_BUS_EN`经**开放DNP JP2**和100Ω到U4 EN；R5=4.7k下拉。TCA9517内部EN有上拉，不能使用100k弱下拉。按资料在VI=0.2V时的最大30µA估算，R5上偏1%产生约0.1424V，低于该测试电压，也低于3.0V电源时0.9V的VIL门槛；电源斜坡仍需实测。4.7k在使能时产生额外约0.7mA负载，不能遗漏功耗。若仅用高阻VOH=0.8VDD作条件估算，100Ω上偏1%、4.7k下偏1%的分压比4653/(4653+101)≈0.97875，EN约0.783VDD，高于0.7VCCB门槛；但这不是带载VOH保证，必须实测GPIO47驱动负载后的EN≥0.7VCCB、高电平裕量和上电斜坡。

|状态|AXC|SCCB|
|---|---|---|
|JP1/JP2未装|/OE被上拉，Q1关断|EN被下拉|
|已调试装桥、MCU复位/低电平|Q1 Gate下拉，输出禁用|EN下拉，输出禁用|
|主控高电平且两侧供电合格|Q1导通后/OE低，固定方向翻译|EN高，双向缓冲|
|任一域掉电|依赖各芯片原厂掉电高阻机制；需验证实际电源斜坡、残余电压和外部反灌|同左；不等于未知模块也具此能力|

启用前关闭共享UART日志、预配置RESET/AUX/XCLK、确认两侧电压和上下拉，再按时序使能。UART测试仅在相机隔离状态进行。SCCB EN只在总线空闲时切换；遵守原厂Start前/Stop后100ns要求。异常/退出先停止事务与采样、禁止IO/SCCB，再撤相机电源。不能靠固件代替默认硬件关闭。

## SCCB选型经过阈值核查
最初考虑TCA9406，但其推荐VIL≤0.15V与已知传感器输出界限不能形成充分保证，因此**本次不采用它**。

U4=TCA9517DGKR，A侧接1.8V传感器，B侧接3.3V主控。它不是透明零偏移开关：B侧输出低最大0.6V，A侧输出低最大0.2V；B侧外部驱动必须能拉到0.4V以下，不能再串另一个具有静态低偏移的B侧缓冲器。主控常温3.3V输入VIL门槛0.825V对0.6V有余量；**主控输出VOL资料的0.1VDD是在高阻负载、25°C条件下，不能把它当成全温带载保证**。必须在实际10k上拉、电源/温度范围测S3下拉低于0.4V及传感器ACK波形，未经验证不装JP2。

两侧各10k上拉，只属于独立CAM_SCL/SDA总线，不与拾笔AON I²C直接短接。初始100kHz；按0.8473RC估算100pF约847ns，电容/公差/缓冲延迟必须实测。1MHz和长线不在批准范围。U4可能增加毫安级活动电流，掉电/禁用电流要纳入电池端实测，不能承诺原待机时间。

## GPIO预算与尚未完成
不增加GPIO：IO_EN42、BUS_EN47、共享控制43/44，以及原有D0–7、PCLK/VSYNC/HREF、XCLK、SCCB。PWR_EN41由power_safety使用，LED48由illumination_driver使用；原29个可分配GPIO仍全部占用，没有新增SPI储存总线。

AXC可承受高速边沿不代表S3可用72MHz PCLK。实际不同芯片传播延迟、PCLK/数据路径偏斜、FPC电容和S3采样建立保持均要核算/测量；不得直接沿用未经实测的72MHz初始化。板上必要串阻、阻抗与回流路径将在真实布局后决定，不提前声称SI合格。

### 剩余最小物理输入
1. 用通断/显微照片确定实物模块每条目标信号、真实IO电压和是否能访问同一VIO域；若无法建立映射，改用有明确接口的模块/自制载板，不能猜接旧30pin。
2. 电源顺序、XSHUTDN实际低电平及SCCB ACK/低电平负载实测后才允许装commissioning桥。
3. 示波器测实际PCLK/数据相位、可用帧率和曝光；完整模组/镜头尺寸用于主PCB/机械合并。

本电路不解决未知相机本体的1.5/1.8/2.8V供电序列、不批准电池/NTC/充电、不证明光学精度或15–18mm装配。TSSOP/VSSOP是易核查的评审封装候选；将来缩小封装必须按对应封装重新核对脚号，不能只换footprint。

## 原厂依据（不打包私有传感器原文）
- [TI SN74AXC8T245 RevC](https://www.ti.com/lit/gpn/sn74axc8t245)：PW脚表、DIR1/DIR2真值表、/OE与VCC隔离。
- [TI SN74AXC4T245 RevB](https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf)：PW脚表、两个方向分组、掉电行为。
- [TI TCA9517 RevD](https://www.ti.com/lit/ds/symlink/tca9517.pdf)：A/B域、EN内部上拉、静态低偏移与0.4V门槛。
- [Nexperia PMV30UN2](https://assets.nexperia.com/documents/data-sheet/PMV30UN2.pdf)：1G/2S/3D，不能用阈值电压代替导通参数。
- [Espressif PICO v1.2](https://documentation.espressif.com/esp32-s3-pico-1_datasheet_en.pdf)：主控输入输出条件。
