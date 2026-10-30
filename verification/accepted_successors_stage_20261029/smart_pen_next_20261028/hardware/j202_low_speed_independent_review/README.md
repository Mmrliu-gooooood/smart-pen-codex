# J202 五网低速/外部参考供电限定独审

**仅在绑定下述勘误后接受为后继静态布局基线，仍NOFAB。** 不是整相机接口、头部电源、SI/PI/射频、制造或安全批准。无需改冻结铜，但不能把错误端口域名称继续用于整合/上电指导。

输入 `../j202_low_speed_reference_candidate/manifest.json` SHA `b7e8ecbfb0b8785452808f1233c6d1feab9bde236dafe2faeb12da01099a5d18`，143项逐个复核。当前PCB **`9a0335443167a4395431cb78abfab959893060d82a7b4da9e5fcd861bc40c038`**；基线已审4994地块。无发布、采购或通电动作。

## 必须携带的纠正

1. 冻结README/`interface_reference_contract.json`笼统称“AXC/TCA VCCA”“translator A domain”错误。fresh XML及libpart独查：**U201.23/.24=VCCB，U202.16=VCCB，U203.16=VCCB；仅TCA U204.1=VCCA。** 实际网络/铜身份正确，但供电域文字不准确。
   权威后继 `../../docs/electronics/head_vio_port_name_erratum_v2` 必须绑定；manifest `c68e17a8002b2d833c79ce96f9dc7323ec7448499386f3a40173c56b4f29e6d2`，对应原合同SHA `65eca5fea27c4aca954e7a3438e52ac3cc6300b87fd4d6b5686e3f5071c58e23`。独立运行其normal/-O源检查，同时本报告 `vio_pin_name_check.py`直接从fresh节点核名。VIO为**未来合格外部紧凑头提供的1.8V输入参考**；当前未存在已批准头部电源，更非本机LDO/AON输出。
2. README旧铜新参考缺口“唯一三网”不完整：冻结JSON与独跑均有第四网 **CAM_SCL=2.9815e-08mm²**。这高于报告记录阈1e-8mm²、低于脚本对非allowed网的拒绝阈1e-6mm²，不能表述精确零。它是极小数值级结果，不据此推导回流电气影响；主要三网值见下。报告与后继整合不得丢弃此区别。权威数值勘误 `../../docs/electronics/j202_reference_numeric_erratum` 必须同时绑定，manifest `7f78530a324d992c29acb777bde356a6c48a5521576bd2d22322dd566eb1e909`。两勘误逐成员SHA已验证，normal/-O重跑相同；见 `mandatory_errata_dependencies.json`。

## 独立复现

- 同basename工程/规则fresh全量KiCad9.0.2 **17违规/21未连/parity0，exit5**；原17项完整finding multiset不变。ERC **0错误/1既有VBUS警告**。
- 原生102实体/356端点、MPN、所有源/库/pro/dru字节及全部规则轮廓/层/禁止flags保持。仅新增135track+14via，旧铜0删0改。
- J202.19 XSHUTDN/.20 TRIG/.21 SCL/.22 SDA/.23 VIO分别全部旧源端点实际合并；全部旧pad关系保持，七地返回原样，6AON/4GND实际填铜岛接核心。
- 独立对五个完整网络有限宽度铜逐层核异网正面积交叠，全部零。freshfill逐zone-layer不变；精确序列化delta重放得到同一PCB SHA。
- VIO新线0.25mm，其余0.15mm；仅XSHUTDN3孔0.45/0.20，其余11孔0.60/0.30。14孔双面原生TENTED/IsTented实核，钻孔不侵任何实际F/B SMT pad。XSHUTDN出口(3.875,89.85)钻边到粗body y90名义0.05mm，非公差/底部绝缘保证。
- R236 4.7k下拉、R237 100k下拉与R242/R243 10k上拉到VIO不变；VIO实际负载端点、四100n与AXC/TCA域按fresh源保留。JP301及其他commissioning保持OPEN，不表示任意电源序列或断电IO安全。

## 非零参考面变化必须保留

扣所有通孔钻孔的实填参考面筛，旧投影损失的唯一并集：

|网|mm²|
|---|---:|
|USB_EN1|0.000592207987|
|SENS_VIO_1V8|0.1798112086635|
|SENS_SCL|0.094964881603|
|CAM_SCL|0.000000029815|

逐段求和与并集不是同一口径。DVP/XCLK/RF/IRQ/AON_I²C无记录新增缺口，RF区无新增侵入。USB_EN1低速不豁免边沿/返回，VIO/SCL换层也未因同域而资格通过。

新连续同层中心线参考缺口约0.48918mm（≤0.005mm采样，0.010mm边界口径）；最差最近地via约4.00952mm。不能以同名地或岛连通替代回流/EMI验证。AON扩大全部14新孔附近填铜删除额外6.124701mm²反事实仍保持旧pad关系，仅证明局部边缘不是唯一拓扑通路，非最小截面/电流密度/热资格。

新VIO22.236123mm、SCL20.114368mm、SDA21.088527mm、XSHUTDN32.575801mm、TRIG46.045710mm，皆新增中心线总和而非全支路传播延迟。36个<0.1mm短段仍有维护门，不称优雅量产布局。VIO名义新增铜电阻估计仅敏感性模型，外部电源和AXC动态负载未知，不批准电流额度。

相机SCCB与IMU独立总线不共享时序资格；100kHz仅待测起点。J202仍同一24Pin研究口，未知30Pin模组不得接入。后续12条DVP/时钟仍需成组布线，可在新版本重新布局地via/低速铜但须复验；本冻结不是永久布局禁改。余17违规/21未连、头部光学/电源/机械/制造/成本/实测门继续开放。

## 证据重跑

复制本目录到隔离副本运行，勿回写冻结。`run_native_checks.py`导出fresh XML/ERC与完整DRC；命令/退出码见 `native_command_results.json`。DRC采用 `--all-track-errors --schematic-parity --severity-all --exit-code-violations --format json`，不吞exit5。

`verify`、`compare_drc`、`plane_reference_audit`、`measure_routes`、`continuous_reference`、`aon_margin_counterfactual`、`extra_checks`、`vio_pin_name_check`八组normal/-O等价；六类×两模式共12负例按具体错误拒绝；`replay.py --output NEW-EMPTY-DIR`同SHA。`final_checks.py`明确核四网非零损失、反事实与负例，不用assert。原算法隔离复跑加独立源/规则/freshfill/五网实铜/实际端口域/孔侵入；不宣称两套独立几何内核。
