# USB 尾板 Rev A/B 独立审查 — 2026-10-28

**结论：未发现本次实现的错网/引脚映射问题。B 的几何检查通过，但焊接覆盖仍未资格化，NO FAB。**

审查时间：2026-10-28 10:41 UTC。审查 A/B 实际原理图、板文件、封装、项目规则及 DFM 说明，不把板内连通等同跨板 USB 通道或整机完成。

## 独立执行结果

- 从两版当前原理图重新导出 XML：各9器件、37符号pin、40电气pad；逐实际PCB pad对新XML网络、器件值和真实DNP属性一致。四只S1壳脚同接GND，逻辑地/电源共位pad不是异网短路。
- 两版新原生 ERC 均0错误/0警告。独立 DRC 使用 `--schematic-parity --all-track-errors --severity-all`：A为4个孔距违规、0未连接、0parity；B为0违规、0未连接、0parity。没有DRC排除，A/B项目文件逐字节相同。
- USB引脚：A6/B6→DP，A7/B7→DM，A5/B5分别CC1/CC2并各有独立Rd；四VBUS→VBUS_5V；SBU1/2保留NC。TP101/102分别DP/DM，未偷换成主板串阻后的MCU端。
- U102保护通道1/2/4/5分别DP/DM/CC1/CC2，3/8接GND；10/9/7/6以实际PCB铜接对应通道。TI允许这些内部NC引脚用于外部直通布线，不能把内部NC误认成芯片内部连线。[TI TPD4E05U06 Rev O，p4](https://www.ti.com/lit/ds/symlink/tpd4e05u06.pdf)
- 对照TI原厂示例图：DQA0010A信号铜0.565×0.2、地铜0.565×0.4、列距0.835、节距0.5、R0.05；DYA0002A铜0.67×0.4、中心距1.48、R0.05，候选铜形状一致。仍需核实实购物料封装版本与装配工艺。[DYA数据手册](https://www.ti.com/lit/ds/symlink/tpd1e10b06.pdf)
- GCT B4原图核对真实订货格式USB4105-GF-A-120、shell=GND、推荐地pad0.60×1.15、定位孔0.65与间距5.78。原图±0.05不是任意缩短名义铜的许可。[GCT官方图](https://gct.co/files/drawings/usb4105.pdf)

## A/B 差异与本次发现

- 独立逐pad比较确认仅J101的A1/B12及A12/B1（两块物理地铜、四逻辑pad）中心远离孔0.04 mm、长度1.15→1.07；宽0.60、R0.15及远端边不变。孔、其他pad、所有track/via几何不变，网络不变。
- 圆角铜/圆孔独立计算：A `hypot(0.16,0.65)-0.475=0.194402719 mm`，B `hypot(0.16,0.73)-0.475=0.272328576 mm`。B超过原0.25规则，但不能证明最坏焊接heel覆盖；1.07亦低于原1.15±0.05的下限。
- **真实文档/可比性问题：不能称“除了四pad，其他所有铜完全相同”。** B重新填铜后，B.Cu的filled_polygon在多处改变，例如(3.6,8.5)附近非地过孔的地铜避让边界收缩约0.05 mm；不是只有连接器附近的变更。项目规则逐字节一致、zone局部间距均0.15，信号线路/过孔不变；这不是已证实的错网或规则豁免，但必须把“定义几何不变”与“填铜结果变化”分开记录。已向设计者报告；10:44 UTC复核 README 与对应 electronics 文档已明确说明重填铜差异，文档问题已纠正，设计源与检查日志未改变。

## 未完成而非假通过的门槛

B仍为AssemblyUnqualified：实际金属尾脚接触长度/位置/公差、焊膏/贴装及机械拔插承载未验证。A若采用则需明确支持其孔距的工艺审核，不得用圆整数值替代0.1944。没有在本次独立审查中重新资格化所有板厂公开能力/报价。

没有整段90Ω、ESD实测、USB眼图、线束/屏蔽/应力释放、VBUS浪涌/挂起/枚举电流、整笔尺寸或预算放行。两只Rd并不授权1.5A/3A；TVS不构成持续过压保护。本报告不提供Gerber或制造授权。

## 受审文件 SHA-256

路径相对仓库根；B内部basename仍为usb_tail_revA，不应覆盖A。

| 文件 | SHA-256 |
|---|---|
| `hardware/usb_tail_revA/usb_tail_revA.kicad_pcb` | `57577ea1899a5557e44c01847df9887e135e9700801c4b5ec8fd18b4c727a7f0` |
| `hardware/usb_tail_revA/usb_tail_revA.kicad_pro` | `3b99d1f1f0ab62fb264fc4eb4f6d6a63b6c96b38b1e8cfd8d163e008d1d0c92b` |
| `hardware/usb_tail_revA/usb_tail_revA.kicad_sch` | `3292cac5d389346bcb7007b5a20c4b0983434cc4f324eb8503876e9665a233c0` |
| `hardware/usb_tail_revA/usb_entry.kicad_sch` | `4f779f7c17de75abe3430f7aa8a9f5d5fde23b0bdb47764b3cd04c939c400bc3` |
| `hardware/usb_tail_revA/Pen.kicad_sym` | `73c9ba3112010fc9c9270ac8e201c59c425f402556ec052d49c0850bb41d05e6` |
| `hardware/usb_tail_revB/usb_tail_revA.kicad_pcb` | `4f2caad6090440be76f4ba7226e81b05118164bc3271e52690596e6329fa4d94` |
| `hardware/usb_tail_revB/usb_tail_revA.kicad_pro` | `3b99d1f1f0ab62fb264fc4eb4f6d6a63b6c96b38b1e8cfd8d163e008d1d0c92b` |
| `hardware/usb_tail_revB/usb_tail_revA.kicad_sch` | `3292cac5d389346bcb7007b5a20c4b0983434cc4f324eb8503876e9665a233c0` |
| `hardware/usb_tail_revB/usb_entry.kicad_sch` | `bba573fd895da9b1b5fada8e6dbb0c46b0730a3092fb0b5bb95a513012733ddf` |
| `hardware/usb_tail_revB/Pen.kicad_sym` | `73c9ba3112010fc9c9270ac8e201c59c425f402556ec052d49c0850bb41d05e6` |

仅审查并写本报告，未修改设计或发布；原厂PDF未随报告打包。
