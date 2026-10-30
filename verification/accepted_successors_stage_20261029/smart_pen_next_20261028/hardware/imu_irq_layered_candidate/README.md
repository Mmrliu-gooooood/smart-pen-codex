# IRQ + MEMS 分层规则：有限范围可继续研究的原生板

**NOFAB，禁止据此下单生产或给未知相机接电。整笔和完整 IMU 接口尚未完成。**

本阶段只完成 `PICKUP_INT_N` 铜连接，并把经独立审查的 MEMS 分层规则实际合入。I²C 两网仍完全未布线，合计 4 项缺连接；没有把它们改成 NC，也没有换 GPIO、改源、绑模式或删除器件。

## 固定身份和实际结果

- 基线：`../j107_mode_port_closure`，PCB `8aa2581b4df112b979d83e67b9a6a2ddaa70a433c265cdc9849e41b60ff05ab5`。
- 本板：`native/mainboard_revD.kicad_pcb`，SHA-256 `752f83d57fa15450862dcf1c3751041b49f9830fd2c541443d717c6e99d1b229`。
- 102 个原生封装、356 个源端点、全部原生 footprint 块及原理图/项目/自定义规则树不变。10 个精确 Manufacturer/MPN/ProcurementStatus 字段随既有源版本保留并复核。
- 全量原生 DRC：**17 条违规 / 37 项未连 / 0 parity**，退出码 **5**。17 条完整违规 multiset 与基线完全相同，不只是计数碰巧相同。其中仍有 12 条错误（短路、孔/铜间距、阻焊桥）和 5 条 dangling 警告，绝非全板通过。
- 新鲜 ERC：0 错误，1 条原有 VBUS 边界 global-label warning；未通过静默排除改变门槛。
- 有限实铜图仅把 IRQ 两端合并；所有旧 pad 分量保持。AON 六个实填岛、GND 四个实填岛仍各有实铜路径到核心。
- normal / `python -O` 同一判定；5 类错误 × 两种模式均按预期错误类型拒绝。独立目录精确 delta 重放、再次完整填铜均再现上述 PCB SHA。

## 铜路径和小孔条件

IRQ 为 U101.6（GPIO1）到 U501.12（INT1）。所有新 IRQ 线宽仍 0.15 mm，未改为 FineSignal127。

**完整原生 IRQ：118.169488 mm / 86 段 / 3 个 via，28 段短于 0.1 mm。** 长度是铜中心线总和，不含焊盘内传播和 via 电气延迟。早期提及的 117.439382 mm 仅指长路径，另有 0.730106 mm MCU 扇出；不能把前者冒充整网长度。

长段主要在 In3，另有 B 面与两端 F 扇出；没有把 70 mm 信号放进 AON 电源层或地层。为释放 MCU 出口，只重排 BOOT 局部 F/In2 扇出：8 段旧铜移除、7 段 BOOT 新铜；BOOT via 从 (1.8,9.4) 移至 (1.26,9.7)，由 0.60/0.30 改为 **0.45/0.20 mm**。完整 BOOT 线段总长约 19.846068 → 20.430992 mm；所有 BOOT pad 的真实连接保留。

3 个 IRQ via 也为 0.45/0.20 mm 通孔。原项目允许的最小 via/钻孔/环宽为 0.45/0.20/0.10 mm；本孔理论环宽 0.125 mm，孔间距和孔铜间距门仍 0.25 mm。IRQ 保持 Default 0.15 mm 间距/线宽，没有改规则、盲孔或微孔。这是既有条件工艺内的局部小孔 override，**不代表厂家已批准叠层、钻孔、环宽、公差或报价**。

## MEMS 分层、必要外逃与参考地

依据 [ST TN0018 Rev.8 §3.9/3.10，图 15/16](https://www.st.com/resource/en/technical_note/tn0018-surface-mounting-guidelines-for-mems-sensors-in-an-lga-package-stmicroelectronics.pdf)，以及 `../mems_layered_rule_study`、`../mems_layered_independent_review` 与 `../../docs/electronics/mems_layered_rule_erratum`：

- F body 区 x3..5/y81..83 禁 pour/via，通孔穿 F 仍禁；中央 F 区实际禁 track。
- 内层参考铜按项目分层工程解释恢复，不再把旧“全部六层无平面”说成厂家要求。此解释不是六层应力/噪声或生产资格。
- 中央区范围是项目几何筛；y 边界含端排 pad 12.5 µm 重叠，**不能称精确全 pad 内缘**。允许原生 pad，本板新 IRQ 不进入中央禁穿越区。
- 新 IRQ 的 F 扇出在名义 body 内约 0.042863 mm²，其中 0.007569 mm² 在原生 pad 铜之外；它完全落在 pin12 向外必要接近带 x3.575..3.925/y81..81.2375 内。该原生 pad toe 距名义 body 边约 0.05 mm，不能制造“零交叠”而使正常连接不可实现。接近带是明确的项目解释，不是厂家给定的免审尺寸。旧外围 pad 横连、焊接/应力人工门仍保留。

`continuous_return_screen.json` 沿连续同层链合并检测，最大中心线参考投影缺口约 **0.383607 mm**；采样步长 ≤0.005 mm，边界采样不确定度说明为 0.010 mm。不同层的链不硬合并，换层另列；这不是返回电流仿真。F 参考 In1，In3/B 参考 In4；完整投影面积、各段缺口与所有 via 的近邻地 via 在 `reference_and_lengths.json`。

三个换层处到最近现有 GND via 的中心距约 2.7045、0.6915、2.9532 mm。尤其 IMU 端约 2.95 mm 的换层返回仍是电气/EMI门，不能靠 GND 同名或全岛连通免除。旧全层空白规则下 2.5483 mm 的参考缺口保存在 `historical_all6_reference.json`；本次合并恢复参考面后重新测量，并非继承分支通过。

## IRQ 的功能门仍未关闭

按 LIS2DW12 DS11811 Rev.9 §8.6，CTRL3 默认 push-pull、active-high、非锁存。**`PICKUP_INT_N` 的名字不会自动把硬件变成低有效。** 当前该网只有 MCU 与 INT1，没有外部上拉；不能假设改 open-drain 后已有偏置。

固件必须实际确认：输出极性/模式、INT1 路由、锁存与清除、睡前闲置电平、唤醒边沿/电平及休眠期间行为。尚未做唤醒/丢首笔实测；这里只证明限定静态铜连接，不证明首笔捕获、姿态补偿或产品功能。

## I²C 仍缺什么，以及拒绝了什么

SCL/SDA 的 10 kΩ 上拉、源端点和器件原位保留，仍各 3 个分离 pad，合计 4 项未连。时序预算引用 `../../docs/electronics/imu_i2c_timing_budget`：100 kHz 仅是待测首轮配置，不因低速就保证上升时间或总电容。

`rejected_comparisons.json` 和 `rejected_summaries/` 只保存精简反例：

- 低速控制改道释放两个 via，但 BOOT 的 In2 绕行切断核心 AON，拒绝；没有用细线救主电源。
- 单个 D0 换层能接回但没打开两线可行通道，未采用。
- HREF/VSYNC 靠边成组试验产生两出口，但返回空间不佳且源通道仍隔离，未采用。
- 6.87 mm BOOT In1 局部跳接切到 D0/D1 参考投影，拒绝；手工内侧版又撞 D1/D3 via。
- 带敏感 F 投影保护的小区域搜索未找到路径。这些都是有范围/采样精度的失败试验，**不是全板绝无可行布局的数学证明**。

下一步需要连同多网 MCU 扇出一起重新分配，不继续在拥挤版上逐点添加救线。所有这些失败 trial 的铜、位置和规则均不在本板内。

## 复验与边界

```bash
/usr/bin/python3 build.py --output /tmp/new-empty-irq-native
/usr/bin/python3 verify.py
/usr/bin/python3 -O verify.py
/usr/bin/python3 negative_tests.py
/usr/bin/python3 replay_and_refill.py
/usr/bin/python3 pcb_preflight.py native/mainboard_revD.kicad_pcb --lock preflight_lock.json --report preflight.json --run-drc
```

最后一项预期退出 5，而不是假造通过。冻结目录不可原地重跑写报告脚本，应先复制到新的隔离目录。`dependencies.json` 绑定必要历史 manifest；没有整包复制移动 trial。

JP301 与充电 commissioning 保持 OPEN，未知定制相机仍隔离；TPS22918 不是过流限流保护。RF、真实叠层与钻孔 DFM、回流/PI、换层 EMI、I²C、机械线束、剩余全板错误及成本报价均未关闭。本阶段没有采购、通电、发布或 GitHub 写入。
