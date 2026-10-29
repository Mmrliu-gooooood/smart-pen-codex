# USB 尾板 Rev A：已布通的候选，4项真实DRC仍未关闭 — NO FAB

2026-10-28 独立新板，不改主板B/C/D。12×20mm、0.8mm四层是工程候选，**不是170mm整笔装配通过**。

## 已完成与当前真实检查
- 原生根 `usb_tail_revA.kicad_sch`＋`usb_entry.kicad_sch`；PCB `usb_tail_revA.kicad_pcb`。9个真实器件/接口、37个符号pin、40个电气铜pad（含4同号S1壳脚），全部物理赋网并布线。
- 新ERC **0错误/0警告**；native PCB **0未连接、0原理图parity问题**。
- **4项DRC孔净距错误仍保留**：GCT推荐图/库原几何的两个定位NPTH孔，各邻两个同位不同编号GND pad，实际净距约0.1944mm，小于本项目0.25mm孔净距。不是新增线路短路；没有排除、不改全局规则把报告变绿。需板厂针对原厂landpattern确认工艺或做正式封装调整后重审。
- `tools/verify.py` 167个独立断言：所有真实PCB pad对XML、TI通道/直通pad网络、GCT官方位置/孔槽/焊盘尺寸、DQA官方铜尺寸、无DRC排除及上述真实剩余错误。`verification.json`/`verification_run.log`保存新结果。
- `review.pdf`及`preview/board.svg`/`back.svg`均由实际KiCad导出。无Gerber制造放行。

## 器件/引脚纠正与明确来源

### J101 USB4105-GF-A-120
[官方GCT B4图](https://gct.co/files/drawings/usb4105.pdf)的订货格式不含“16P”；旧逻辑源的`USB4105-GF-A16P`是描述拼接，不是本板采购号。本候选选真实 `USB4105-GF-A-120`：1.20±0.15mm壳脚，相对0.8±0.1mm候选板厚，底侧伸出约0.15–0.65mm，必须计入尾部机械。默认0.95mm脚不保证最坏板厚下露脚。

官方表列SHELL=GND；KiCad库4个壳槽同电气号S1，均真实接地。A1/B12、A12/B1及两组VBUS的重合焊盘编号对应原厂接触结构，不是重复短接错误。SBU1/2保持NC。已核推荐焊盘宽/距、两个0.65mm定位孔和4个0.6mm宽槽；定位孔净距DRC尚未放行。连接器本体约8.94×7.35mm、板上高度3.31mm；支承、拔插载荷及pin-in-paste锡量尚需装配资格，不能只靠裸PCB承担壳体载荷。

### U102 TPD4E05U06DQAR
[TI Rev O](https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf) pin表：1/2/4/5为四个ESD通道，3/8接GND，6/7/9/10为芯片内部NC且明确允许可选直通PCB走线。本板用真实铜线将10↔1(DP)、9↔2(DM)、7↔4(CC1)、6↔5(CC2)相连；**不是假定芯片内部直通**。符号对应pad为passive NC_ROUTE，逐pin核对，未将no_connect冲突压掉。

旧通用USON库不是本芯片原厂landpattern。本板新增 `TI_DQA0010A_USON10_OfficialLandpattern`：信号铜0.565×0.2mm，3/8地铜0.565×0.4mm，左右中心跨度0.835mm，节距0.5mm，R0.05；来自RevO p29示例。0.025mm阻焊扩张和courtyard为显式工艺候选。**同文档还列DQA0010B，实际订购批次/package版本须核实，不能凭相同body宣称任意兼容**。

### D101 TPD1E10B06DYAR
使用 `TI_DYA0002A_SOD523_OfficialLandpattern`，不是原通用D_SOD523。铜几何继承已核TI DYA图候选；[官方datasheet](https://www.ti.com/lit/ds/symlink/tpd1e10b06.pdf)来源/hash见`source_records.json`。1接VBUS、2接GND。TVS/ESD并不构成持续过压、反接或USB-PD保护许可。

## 布线与真实外部接口
- R110/R111各5.1k±1%独立下拉；无Rp广告测量、无PD控制器。保持原USB100默认策略，不能凭两只Rd就消费1.5A/3A；整机枚举、授权500mA、挂起和VBUS浪涌电容仍由整机验证。
- R112/R113 **留主板，不在尾板重复**。USB_DP/DM是到主板串联电阻之前的网，不能接错为USB_DP_MCU/DM_MCU。
- TP101=DP、TP102=DM、TP103=VBUS_5V、TP104=GND，是真正1.5×2mm无钢网焊线land；不是为DRC虚造的测试点。四个外部电气端必须用合格线束/连接方案完成。丝印5V/DP/DM/G给装配识别。
- 连线线径、长度、绞合/屏蔽、阻抗、拉力释放和壳体固定未确定；本PCB的0未连接只验证板内，**不包含跨板线束**。
- DP/DM主要在F层；连接器重复针的短DM交叉在In2层，均参考连续In1地。B层地铺铜带少量CC低速走线避让；壳脚/TVS/ESD有真实地过孔。未宣称完整高速差分通道资格。
- 当前0.15mm信号线、0.15mm候选铜净距，信号过孔0.45/0.20mm、地/电源0.6/0.3mm；这些是明示工艺候选，不是板厂已接单承诺。DP/DM存在Type-C重复针支路、换层和焊线fanout；**stackup未确定，因此不能保证90Ω或时序/眼图**。原生USB为Full-Speed用途，仍需整段SI、插拔和ESD测试。

同名J101/U102/D101/R110/R111与主板统一图是同一物理USB功能分区，不应在整机BOM里买两套。尾板纠正的MPN/封装/NC直通属于明确变体；后续整机分板原理图需同步权威版本，不能不经核对直接合并重复引用号。

## 复现与放行门槛

```
./rebuild.sh       # 重建源、导出XML、重建PCB，再完整检查
./run_checks.sh    # 不重建，只对当前真实文件重新检查/导出
```

首次重建时先用`kicad-cli sch export netlist --format kicadxml ...`生成XML，再build_pcb。`run_checks.sh`固定使用可写/tmp XDG目录，不写只读home配置。没有原厂PDF或私有相机图片打包。

最小未决：4项真实孔净距DFM、DQA实购封装版本/装配钢网、USB及跨板线束stackup/SI、尾部壳体支承与尺寸、整机USB电流/挂起/浪涌验证。尚无采购、报价或整笔成本通过结论。
