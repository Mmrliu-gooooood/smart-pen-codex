# 阶段备份与当前选用版本

日期：2026-10-29。**NOFAB：不是最终制造包，不是消费级成品验收。**

本次备份保存经过身份校验的原生工程、模型、代码、试验和独立审查。历史失败与后继版本并存，是为了可追溯；不得任选某个旧 PCB、BOM、线序或 CAD 混搭制造。以下状态只针对明确列出的快照，未纳入仍在修改的试验目录。

## 从哪里看

| 内容 | 本批入口 | 已有证据与边界 |
|---|---|---|
| 当前主板与 Rev B 电源模式映射 | [J107、BLE 与接收端阶段](verification/ble_pc_and_mode_stage_20261029/README_ZH.md) | J107 三端静态连通、独立审查；完整 DRC **17 finding / 38 unconnected / parity 0**，其中仍有 **4 项 shorting finding**。不是整板通过。 |
| 相机电源门控及前代差量 | [门控完整静态阶段](verification/gate_full_stage_20261029/README_ZH.md) | 六门控网络、旧 pad 连接、默认下拉与 JP301 物理开路已核；动态、回灌、CT/QOD、真实相机负载和测试工具访问仍未验证。 |
| 电源、IMU 源与机械台架 | [原生硬件与机械阶段](verification/hardware_mechanical_stage_20261029/README_ZH.md) | 正确源/BOM/布局与局部几何检查；共同基准台架不是笔壳，夹紧、疲劳、材料和实际装配公差未验收。 |
| 连续点阵解码 v3 | [v3 源与独立试验](verification/continuous_v3_experiments_20261029/README_ZH.md) | 主 340 幅合成试验中 253 次正确接受；20 幅旋转图缺完整窗口继续拒绝。仅合成证据，不是实物准确率或笔尖坐标资格。 |
| v3 目标性能测试工程 | [目标基准](verification/continuous_v3_target_experiments_20261029/README_ZH.md) | 实际 SDK 构建、目标 ABI、主机错误路径检查；未加载设备，没有 S3 FPS、运行内存余量或功耗实测。 |
| 实际 BLE 传输候选 | [BLE 源](verification/ble_pc_and_mode_stage_20261029/smart_pen_ble_transport_candidate_20261029/README.md) | GATT、分片、认证会话与授权/持久化分离桥；默认关闭，完整板级 provider 仍未接入，无真实手机互通。 |
| PC 接收候选 v2 | [PC v2](verification/ble_pc_and_mode_stage_20261029/smart_pen_pc_receiver_v2_candidate_20261029/README.zh-CN.md) | 严格重组、耐久 journal 后 ACK、来源区分与断连隔离；Windows、实际无线安全状态和硬件断电耐久性未验证。NO_SENSOR 不进入正式评分。 |
| 成本与制造路线 | [成本归档及勘误](docs/research/cost_archive_20261029/README_ZH.md) | 已列小批采购/装配条件与缺项，**尚无已证明满足两支 760 元的完整路线**。报销不自动降低产品成本。 |

当前已归档主板原生文件：

- [J107 后继 PCB](verification/ble_pc_and_mode_stage_20261029/smart_pen_next_20261028/hardware/j107_mode_port_closure/native/mainboard_revD.kicad_pcb)。请同时使用该阶段的同名工程、规则、库、源绑定和 BOM，不能只拿这一文件生产。
- 同目录和独立审查目录保存实际命令、原始 finding、逐版本身份和剩余问题。报告中的默认 DRC 枚举与 `--all-track-errors --severity-all` 不同，比较时必须使用相同命令。本页使用完整枚举。

## 仍未完成的关键事项

1. **完整电路与 PCB**：剩余压力、IMU、相机及其他接口连接和旧冲突尚未闭合；状态指示、真实电池测量前端、照明及整机互连仍须系统复查。v5 的 GPIO/头部线序提案没有自动成为当前 102 实体原生源。
2. **真实相机与光学**：用户已购 SC035HGS 定制 30Pin 模块不能按 AI 给出的线序或新 24Pin 候选直接接电。模块接口、电平、光学与 PCLK 必须核实。SC031GS 采集适配器仍在独立修订审查，**不在本批发布候选内**；不能把 SC031 初始化写入 SC035。
3. **结构**：已归档台架/触点机构的局部碰撞检查不能替代整笔装配。目标 15–18 mm 尚未满足；19/20 mm 等是研究对照，未获得完整结构、握持、强度或制造放行。旧单体壳不是已经具备锁扣和维修入口的成品壳。
4. **尺寸与预算冲突**：当前 RF 延长研究板长约 101.5 mm，不能继承早期 `<100 × 100 mm` 板块目标或小板优惠。制造路线、最终尺寸及完整报价仍需闭合，不能静默视为约束已满足。
5. **实际运行与坐标资格**：Gray8 解码窗口原点不等于物理笔尖。真实镜头/笔芯/姿态标定、落笔时序、相机帧时戳含义和整条 provider 接线未实测，不能生成或认可虚假的 VALID 书写。
6. **存储与续航**：8 MiB 分区候选的记录区约可容 63,488 个固定槽，按 60 Hz 约 17.6 分钟上限，未扣所有实际事件开销；不是 24 小时离线书写承诺。4 小时连续/1000 小时待机均未实测。
7. **安全与制造**：充电 commissioning 保持开路。电池保护、实际电芯温区/电流、NTC 耦合及故障覆盖、功耗温升、USB 状态/回流、无线与材料等资格未完成。ERC/DRC 或软件测试不构成这些实测的替代。

## 软件如何使用这些目录

主目录 `firmware/` 和根 CI 是应用/便携核心基线；新的 v3 解码器、BLE 与 PC v2 保持独立候选，**没有偷偷替换整笔运行入口**。各阶段提供最小复现入口与精确来源校验；运行前阅读对应 README 和依赖说明，在临时副本生成测试输出。

- 根主机验证：`python software/verify_host.py --upstream-pc-src <digital_pen固定提交>/digital_pen_ov5640/pc/src`，依赖 `software/requirements-host.txt` 与 C 编译器。
- 上游基线仍为 `0f8b569176c77dad34aaf83bb008eb118c9f1208`，原仓库未修改。
- 旧目标基准的 nano printf / 64 位输出问题、PC v1 的三个缺陷均保留独立勘误/失败证据；应选明确修订后的 v3 目标基准与 PC v2，不能把旧编译通过报告当运行批准。
- SDK 构建、合成图、host mock 与实物测试分开记录。本批没有自动刷机、相机上电、蓝牙扫描/配对、采购或制造操作。

下一阶段继续关闭实际连接、系统互连与装配问题，并将通过复核的新快照分批备份。最终放行仍以 [RELEASE_GATES](docs/system/RELEASE_GATES.md) 为准。
