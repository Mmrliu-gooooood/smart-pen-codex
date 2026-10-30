# 当前状态：冻结研究快照，不是可制作成品

更新日期：2026-10-30。**全产品 NOFAB / NOPOWER；不得据此制板、组装上电或认定消费级验收通过。**

本页是 r13–r25 本地追加快照的入口。目录中的旧板、旧模型、失败方案和后继版本是可追溯验证证据，**不是多套同时采用的硬件**；不能任选PCB/BOM/规则/库混搭。旧“14未连”等历史数字不是当前状态。

## 本次最新已独立审查硬件

- [5ed5f0ad 原生PCB](verification/imu_control_stage_20261030/smart_pen_next_20261028/hardware/imu_control_native_0522/native/mainboard_revD.kicad_pcb)，[作者报告](verification/imu_control_stage_20261030/smart_pen_next_20261028/hardware/imu_control_native_0522/README.md)，[独立审查](verification/imu_control_stage_20261030/smart_pen_next_20261028/hardware/imu_control_independent_review_0543/REVIEW.md)。同目录工程、规则、源、库必须一起看；仅供研究审查，不是制造选择。
- 完整原生 DRC **0 violation / 106 unconnected / 0 parity，exit 5**；ERC **0错误 / 1条既有警告**。零DRC violation不等于连接完成。AON **38/39**、GND **70/102**、SENS **12/12**实体pad到相应核心；源R503仍47k/RC0603FR-0747KL。
- **新发现的时钟参考退化未放行**：EXTCLK在In2和In4各新增 **0.0017414094705 mm²**投影缺口，不能写为零。IRQ最近核心地孔距3.779302mm不证明回流合格；合并孔、小AON侵蚀岛、53条短段、courtyard、EP孔工艺、短供电逃线和MEMS应力等仍待资格验证。
- **本次可重建的最新独审快照仍是上述5ed5f0ad / 0/106/0。** 另行后续0/96/0控制阶段已收到独立静态复核报告（manifest `ef450fe3a80f14535ee1ff99b9b1dcaad2906bbf8603458bab06da1746ef044e`），但其源码与新增证据**不在本次r25截止清单内**，不随本追加发布，也不是成品或动态合规结论。后续OE R203 10k被动释放的典型模型存在AXC输入Δt/Δv 10ns/V红旗：五个OE典型Ci合计22.5pF，估算105–148ns/V；这不是实测值，但必须单独处理，不能被静态DRC/独审掩盖。相关补充正在另行冻结，待后续明确版本与审查后再独立归档。

## 解码软件：保留V3，V4明确未采纳

- [V3冻结研究](verification/continuous_v3_experiments_20261029/README_ZH.md)保持原状；只是既有软件研究基线，不代表实物笔尖或目标FPS资格。
- [V4投影实验及独审](verification/tilt_projective_experiment_20261030/README_ZH.md)为 **NOT_ADOPTED**，不替换V3、不接入app。旧408回归 **225正确 + 3质量合同违规接受 + 180拒绝**；3例坐标正确但违规接受旧must_reject墨线负例，不能洗成通过，也不能误称坐标错码。
- 原8图6正确/2拒绝，120保留集37正确/83拒绝；完整复现实际exit1，唯一失败为3违规门。85项旧host零跳过、44cold/12warm、独立数值sanitizer证据不构成SDK/FPS/LSan或真实光学资格。
- 200原像素=6mm不等于全VGA=6mm；零拷贝裁切不是缩放。全部合成针孔图不替代实际镜头、SC035图像与笔尖标定。

## 尚未关闭的产品安全与集成问题

相机/板级provider仍为NULL/返回0，未建立可工作的实物采集链；未知SC035HGS定制模块的线序、电平、时钟、镜头和近距成像未资格确认，不能借SC031软件支持替代。JP301与充电commissioning保持开路，未知相机不得接电。

电芯选型/保护/充电温度与电流、NTC耦合、热/功耗、回灌、整机接线和电池安全未资格确认。压力触点50k寿命、ESD/去抖/固件采集、J103 B52与虚拟B70.5映射、实际机械装配公差与可靠性仍待解决。完整两支760元预算、尺寸、续航、无线与材料要求均不能因归档或报销而视为满足。

## 归档与使用

[IMU控制快照状态](verification/imu_control_stage_20261030/LOCAL_PUBLICATION_STATUS.json)与[V4未采纳状态](verification/tilt_projective_experiment_20261030/LOCAL_PUBLICATION_STATUS.json)分别记录各自冻结边界。每阶段source manifest、精确依赖及失败证据应一并保留。当前冻结文件内“LOCAL_STAGED”描述的是创建时状态，不会为后续上传改写其原始字节。

本次仅准备独立本地追加树，**不宣称GitHub已更新或CI已通过**。原24批上传由另一流程处理；须待其结束且核对树/CI后，再统一发布这些追加快照。
