# 当前状态：独立检查的静态研究，不是可制作成品

更新日期：2026-10-30。**全产品 NOFAB / NOPOWER；不得据此制板、组装上电或认定消费级验收通过。**

本页区分归档证据与当前静态研究候选。旧板、旧模型、失败方案和后继版本用于追溯，**不是多套同时采用的硬件**；不能任选PCB/BOM/规则/库混搭。旧“14未连”“0/106”等数字保留在历史记录中，不代表当前候选。

## 本次归档可重建的静态候选

- 候选PCB SHA-256：`dcbd2e6501c8294ece5ecf7b41ffcc86ccc7f58f7cb54ececfdf24962a50f697`；[原生PCB](verification/post_r28_accepted_static_1225/smart_pen_next_20261028/hardware/review_sccb_local_reference_1222/native/mainboard_revD.kicad_pcb)、[研究说明](verification/post_r28_accepted_static_1225/smart_pen_next_20261028/hardware/review_sccb_local_reference_1222/README.md)。仓库按相同字节去重，作者与独审路径的映射以[SOURCE_MAP](verification/post_r28_accepted_static_1225/_closure/SOURCE_MAP.json)为准，不凭目录名推定不同版本。
- 完整原生DRC **0 violation / 67 unconnected / 0 parity**；名义板框 **14 × 99.8 mm**。这是有限范围的静态检查结果，**不是可工作的总线、完整产品或制造/上电许可**。MCU链路仍未接通。
- 源端SDA共享孔的回流/耦合例外仍开放；C207回流变化是权衡，不宣称净改善。实际边沿/时序、BLE、笔画采集、机械公差与装配、电池资格、完整预算仍未关闭。
- [重建及检查入口](verification/post_r28_accepted_static_1225/_closure/README.md)记录冻结链与复现边界；87项作者、30项独审、26项机械检查通过不构成实物资格。Python文件访问审计不等于完整原生系统调用隔离；厂家PDF等排除项保持排除。
- 后续八路数据偏置 **0/59**、其后 **0/57** 静态候选及已保存的CAD支撑已获有限静态范围独立复核，正在另行整理；**不在本次427项归档内**，不能将其结论混入本次可重建的dcbd / 0/67快照，也不构成制造、上电或完整产品许可。历史非采纳比较板和负向检查保留原标签，不能作为制造选择。

## 解码软件：保留V3，V4明确未采纳

- [V3冻结研究](verification/continuous_v3_experiments_20261029/README_ZH.md)保持原状；只是既有软件研究基线，不代表实物笔尖或目标FPS资格。
- [V4投影实验及独审](verification/tilt_projective_experiment_20261030/README_ZH.md)为 **NOT_ADOPTED**，不替换V3、不接入app。旧408回归 **225正确 + 3质量合同违规接受 + 180拒绝**；3例坐标正确但违规接受旧must_reject墨线负例，不能洗成通过，也不能误称坐标错码。
- 原8图6正确/2拒绝，120保留集37正确/83拒绝；完整复现实际exit1，唯一失败为3违规门。85项旧host零跳过、44cold/12warm、独立数值sanitizer证据不构成SDK/FPS/LSan或真实光学资格。
- 200原像素=6mm不等于全VGA=6mm；零拷贝裁切不是缩放。全部合成针孔图不替代实际镜头、SC035图像与笔尖标定。

## 尚未关闭的产品安全与集成问题

**JP201 / JP202 / JP301保持OPEN，provider保持NULL。** 未建立可工作的实物采集链；未知SC035HGS定制模块的线序、电平、时钟、镜头和近距成像未资格确认，不得接电。SC031的软件支持不能替代SC035验证。

电芯选型/保护、充电温度与电流、NTC耦合、热/功耗、回灌及整机接线尚未资格确认。实际边沿和上电/掉电动态、压力触点寿命、ESD/去抖、固件采集、机械装配公差与可靠性均待解决。两支760元预算、尺寸、续航、无线与材料要求不能因归档或CI通过而视为满足。

## 归档与使用

r13–r28及本次后续静态链按各自冻结边界保存；根状态页不改写历史manifest、PENDING/LOCAL标签或失败证据。只有与相应源码、规则、库及声明依赖配套的重建才有意义。上传与CI仅证明对应提交的归档/软件检查状态，不证明硬件可制作、可上电或实物功能验收通过。
