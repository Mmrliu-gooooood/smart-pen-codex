# 19个完整track-only网原生恢复候选，NOFAB

PCB SHA256：4d7bd85ae460928a48967c00adae133c05df5ef259a6789470c04e986b856f8a。

在f92c的12条translator↔J202链研究板上，仅恢复只读计划已列出的19个完整track-only网。所有392个恢复对象保持9a03的原UUID、实际net、层、坐标、线宽和钻孔；其余76铜对象及102实体完全不动。**没有恢复3V3_AON/GND/CAM_3V3_SW及其平面，不得上电、制板或连接未知相机。** 正式9a03基线不被覆盖。

## 实际结果

- 原生完整DRC（--all-track-errors、--schematic-parity）：**0违规 / 233未连 / 0parity**。此前f92c为0/262/0，真实未连减少29。
- 保存后的实际19网、48个实际pad UUID分别在单一原生铜连接分量中；不是仅看对象无碰撞。48−19=29与本轮未连减少数对应。
- 前12条链的实际translator引脚到J202引脚重新检查全部通过。
- 全部392旧对象精确等于9a03对应UUID几何，全部76原对象精确等于f92c。没有添加旧偏置悬空残支或把主电源几何候选片段当完整网。
- 所有footprint/value/pad-net/位姿/尺寸未变；剔除铜对象文本后，原生其余文本与f92c逐字节相同，原理图、project、规则和库也不变。所有plane fill仍为空。
- normal和-O验证结果一致。原UUID克隆后再次原生保存的重放与最终PCB SHA完全相同。
- 19网各找到一个必要铜对象，在连接图中删除后均检出至少一个实际pad失联；此外USB_DP、CAM_ON、CAM_3V3_PRELINK三个副本的**真实原生删段+完整CLI**分别得到2/234/0、1/234/0、1/234/0，新增未连准确涉及目标网，最终原件未改。
- 原生三层图`native_layers.png`已实际查看。图是检查视图，不是制造文件。

## 本轮恢复的19个网

BOOT_N、CAM_3V3_PRELINK、CAM_CT、CAM_ON、CAM_QOD、CHIP_EN、ILLUM_STROBE、ISO_GATE、RF_ANT、RF_SIP、SCCB_ENABLE_LINK、SCCB_EN_SAFE、STRAP_GPIO3、STRAP_GPIO45、STRAP_GPIO46、USB_DM、USB_DM_MCU、USB_DP、USB_DP_MCU。

没有因局部DRC为零而重新声称RF/USB阻抗、返回路径、SI/EMI通过。CAM_3V3_PRELINK只到JP301的前端；JP301 commissioning保持OPEN，没有跨接至CAM_3V3_SW。

## 范围与仍未完成

233未连包括供电地、去耦、MCU相机侧、偏置stub、压力/状态等。16个新信号孔的平面反焊盘、供电主干冲突、地返回、RF参考和全板freshfill/core检查仍需完成。当前没有可上电供电路径，完整网的继承只是为后续完整电源骨架腾出研究精力。

f92c的两实体有限机械预算避让结论只在其静态范围内有效；未知焊料/线束/电池/镜头与装配资格仍开放，外RevD台架R222碰撞仍记录。不能把未改器件位姿推广成整机可装配。

## 工具与拒绝记录

KiCad9.0.2完整CLI；所有操作在NEW目录或/tmp负例副本。初次Clone类型转换错误留下的未加铜base复制及262未连报告明确拒绝，不计为本轮结果；其重复原生复制目录不进入发布清单。后续采用BOARD_ITEM再转正确track/via，保持原UUID。

空zone移除/重建连接和原生Remove接口曾触发SWIG异常，失败stderr单独保留，未作通过证据。最终连接验证先证明plane填充为空，再保留空zone定义读取连接；三个真实删段负例通过精确删除副本内单个UUID的铜S表达式再由CLI独立加载验证，未绕过任何电气检查或规则。

可用 `materialize.py --replay-dir <新目录>`精确重放；`verify.py`核同源、铜、全部实际pad、19图负例和旧12链；`native_negative.py`只写新/tmp副本并跑三个真实CLI负例。无采购、上电、刷写或远端推送。
