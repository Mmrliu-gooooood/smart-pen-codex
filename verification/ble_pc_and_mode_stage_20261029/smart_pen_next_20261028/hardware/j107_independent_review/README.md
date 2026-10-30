# J107 限定独立复核 — 可作下一 IMU 信号布线基线，NOFAB

**结论：接受 8aa2581b 作为下一限定布线基线，不代表整板通过、实物线束放行或充电/相机动态安全通过。** 本审查不修改冻结源，不外部发布。

## 输入及复验

- 主板冻结包 `../j107_mode_port_closure/manifest.json`：`49250127029a2e9ab5c8399eb0ada354b18050e716fcc94a3bfe79e35cd73c64`，110 项逐个 SHA 验证。
- 当前 PCB：`8aa2581b4df112b979d83e67b9a6a2ddaa70a433c265cdc9849e41b60ff05ab5`。
- 基线 `../gate_cam_on_path_maintenance/native/mainboard_revD.kicad_pcb`：`1c4907d04a2bf2dea3a53f89266bc49c0cb96a0683b4898b58cd36b6525ec16d`；上一独审见 `../cam_on_independent_review`，复用而不复制历史证据。
- 线束冻结包 `../j107_current_revB_harness/manifest.json`：`38a26dec06d63b12a866561723522ce1fe8eec9d80a2ca634d88d1e96ebab284`，8 项逐项验证。

隔离 native 副本执行 KiCad 9.0.2：

```sh
kicad-cli pcb drc --format json --exit-code-violations --all-track-errors --schematic-parity --severity-all -o fresh_drc.json native/mainboard_revD.kicad_pcb
kicad-cli sch export netlist --format kicadxml -o fresh.xml native/mainboard_revD.kicad_sch
```

完整结果 **17 违规 / 38 未连 / parity 0，exit 5**。相对 1c49 完整 finding 对象 multiset 恰好删除 11 项、新增 0；只规范 items 顺序，未通过去重/过滤掩盖残留。J103 真短路等仍未解决。规则使用真实同 basename pro/dru；条件六层叠层、netclass/工程 SHA 通过前置验证，制造门明确拒绝。全部 RF/MEMS 禁区轮廓、层及禁止标志保持。

## 实际有限铜及源

- 精确删除 2 段旧地臂 + 1 个旧地 via；新增 5 段线 + 2 个通孔。102 个实体、全部 pad/源身份、位置与其余旧铜不动。
- GPIO18 = U101.24 → USB_EN1 → J107.1；GPIO21 = U101.27 → USB_EN2 → J107.2；两网独立闭合，无异网有限铜正面积交叠。不是只读网名或中心线推断。
- J107.3 用 0.50 mm F 铜接当前输入回地；原 J106 0.50 mm 回流腿及 via 保留。GND pad 分量 12→11，只有 J107.3 加入旧核心；其余旧 pad 关系均不退化。AON pad 分量不变，6 个真实填铜岛均接核心。
- 地尾反事实：仅删旧三件，**不加任何新 J107 桥**，完整工程 fresh fill 后全部旧网 pad 分量仍与原板完全一致。当前输入/IMU/主控/门控回流不依赖新桥救回。此证明的是静态旧尾冗余，不是高频回流无差异。
- 独立 fresh refill 与候选原填充逐 zone-layer 序列一致；新信号 via 的避空确实改变相对基线平面，不能继承上一版“平面不变”。In2 AON 移除 1.294521 mm²、补回 0.617299 mm²，仍 6 岛；In1/In4 主地各移除 1.304136 mm²、各仍 1 岛。
- 局部 x=0..14 / y=78..88 mm 实填铜内缩：原先通过的通道半径未丢失。输入→bulk 地通道至 0.30 mm、→HF 回地至 0.50 mm 保持。两个纯 In2 AON→IMU 路径原本就不通，不能将“前后均失败”当供电通过；跨层连接另由有限铜图确认。未证明全局最小颈、载流、回流电感或 PI。
- fresh XML **102 实体 / 356 引脚端点**；10 个原生 MPN/厂家/采购状态保持。全部源/库/工程字节与基线一致。JP301 OPEN/DNP 与两侧不同网络、物理断开边界继承完整 gate 检查。

## 当前 RevB 版本合同

准确绑定电源 PCB `94ced2bd4100ba6fd8d9a9af11f101cc091a4c112a1bb3c8bb5dec2b2dedcdbc`：J107 1/2/3 → RevB J5 1/2/3，分别 EN1/EN2/GND。检查 XML 与两端真实 PCB pad 身份。**当前三针 1:1 正确；旧四针 pin3=CE_PERMISSION_EXTERNAL，不能套用。** 原同名三针但错误板版本也拒绝。现有 R4/R5 默认下拉合同未变；不证明启动、掉电域/回灌、物理装配和电池安全。

## 复现与负例

在本目录运行 `verify_j107.py`、`ground_tail_counterfactual.py`、`local_plane_corridors.py`、`verify_source_refill.py`、`audit_gate.py`、`independent_checks.py` 的 normal 与 `-O`，结果一致（仅独立前置报告 `checked_utc` 时间戳比较时忽略）。代码为原作者算法隔离重跑加独立完整 DRC/源引脚/禁区/规则/输入哈希检查，并非声称两套完全独立几何内核。

`negative_j107.py`：细化地桥、移当前输入地 via、重编号 J107、删 EN1 via，4 类 × 2 模式全部按预期错误拒绝。`harness_contract/test_mapping.py` 每模式 1 正例 + 8 负例，normal/-O 等价。`finalize_checks.py` 明确拒绝通道退化/模式差异/错误退出码；见 `final_checks.json`。全部判据用显式异常，不依赖优化后消失的 assert。

**仍 NOFAB：17 违规、38 未连；完整 IMU 信号/J103 等待布线；条件叠层材料与制造未资格；真实线束、上电模式、充电 commissioning、QOD/CT/负载动态和未知相机负载未资格。TPS22918 不当作过流/充电保护。** 不以 DRC 减少或有限铜连通取代以上门。
