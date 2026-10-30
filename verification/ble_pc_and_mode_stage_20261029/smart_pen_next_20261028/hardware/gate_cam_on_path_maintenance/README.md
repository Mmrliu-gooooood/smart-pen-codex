# CAM_ON 单网路径维护候选 — NOFAB

## 结果与范围

输入 `gate_control_output_candidate` PCB SHA `508e71cbc50437cfb64a28ea8169a8511eb884f8363620e95f58773f368c5b35`；本候选 `native/mainboard_revD.kicad_pcb` SHA **`1c4907d04a2bf2dea3a53f89266bc49c0cb96a0683b4898b58cd36b6525ec16d`**。

- **仅 CAM_ON**：44 → **9** 个线段，11.995332 → **11.542938 mm**；保留全部 3 个过孔、0.15 mm 线宽、真实 F 面 T 分支 `(8.4,67.95)`。
- 精确删除 41 个原新增线段、加入 6 个新直线段；3 条原线段保留，其中 U301 到首 via 的两段不动。所有 102 实体及完整 pad/source 身份、所有其他网与铜、全部 via 坐标不动。
- 这是**改变铜路线的受约束维护**，不是几何等价共线合并。铜 union 的实际差量已测量，不能称“同一几何”。
- 完整原生检查仍 **28 项违规 / 41 项未连 / parity 0，退出码 5**。28 项违规按完整描述和 item UUID/坐标归一化后的 **multiset 完全一致**，不仅数量相同。已有 J103/J107 短路等问题仍真实存在。
- 实际全部旧网 pad 分量不变；AON 六个真实填铜岛仍全部接核心；GND 分量不变。JP301 OPEN / DNP、断开未知相机要求保持。

## 方法与边界

先前严格共线筛选找不到可以越过 pad/via 的合法合并，本次不改该结论。将 CAM_ON 按三个真实过孔、源端焊盘与 T 分支拆成六条链（原 U301 stub 链保持），其余五链只在原锚点间寻找可见直线。异网的实际 native 焊盘/线/via 多边形外扩 0.154 mm（默认 0.15 mm + 4 µm 数值余量）后逐案检查。端点与所有真实分支保留。新段允许一般直线角度，并非强行把任意斜线称为 45°。

`maintenance_delta.json` 保存六链的原/新坐标、被拒绝的可见性尝试、精确删除/新增 UUID。`replay_delta.py` 从 508e 删除 41 段并插入 6 段，复制完整同 basename project/dru/native source 再 fresh fill。重放得到相同 PCB SHA，且独立执行了实际铜检查；相同 SHA 并未替代几何证据。

**应在隔离副本执行脚本**：builder 会写本研究 native，检查/负例会生成报告和 `guard_boards`，不要直接在冻结目录重跑写操作。原 508e 和所有旧冻结文件没有改动。

## 回流、填铜与几何代价

五个 zone-layer 的实际填充多边形原生序列 **逐项完全相同**；独立重新填铜也不变。因此六层平面的原有孔洞/狭颈几何没有新增或收窄。原狭颈载流、过孔阻抗与动态 PI 仍未资格，不能从“没变化”推导“原来已安全”。

| CAM_ON 铜 union | 移除面积 mm² | 加入面积 mm² |
|---|---:|---:|
| F.Cu | 0.419335 | 0.377332 |
| B.Cu | 0.212122 | 0.193535 |

CAM_ON 整体 pad/track/via 铜对最近地平面的投影缺口：F→In1 从 0.803601 到 0.795228 mm²；B→In4 从 0.815287 到 0.815167 mm²。此量包含信号过孔的地避空区及焊盘投影，**不是电磁回流长度、阻抗或噪声资格**。没有以该面积稍减冒充完整参考地已合格。

新铜仅在中央 `x=4.85..9.9, y=66.5..73 mm`，未碰台架板缘夹持条带 `x=0..0.25 / 13.75..14`，也没有移动实体；不能据此更改机械已冻结的 TP301 `(4.325,74.5)` 或其工具访问资格。

## 检查证据

- `audit_normal.json` / `audit_optimized.json`：完整源/实际 pad/旧铜、MEMS、JP301、门控供电连接；新增路线合同已同步，未复用过期 raw net 清单。
- `maintenance_audit*.json`：相对 508e 的全部旧网分量、六 AON 岛、所有实体、每条剩余铜身份、真实跨网铜交叠、填铜序列及原生违规 multiset；normal / `-O` 一致。
- `maintenance_negatives.json`：新增线宽篡改、保留过孔移位、TP301 移位、填铜篡改四类 × 两模式均按指定错误拒绝。
- `source_refill.json`：当前 native 源/库/project/dru 与 508e 字节一致，fresh XML 102 实体 / 356 端点，10 个精确 Manufacturer / MPN / ProcurementStatus 原生字段保持，fresh fill 不变。
- `preflight.json`：绑定同名规则、显式叠层及 KiCad 9.0.2，标准 all-track-errors / severity-all / parity / exit-code 检查。
- `replay_audit.json`：完整同 basename 配置下的差量重放复验。没有旁路默认规则。
- `track_statistics*.json`：使用 KiCad 整数 nm 的长度阈值，CAM_ON 的 <0.1 mm 段从 28 → 0；全批新线段 973 → 938，其中 <0.1 mm 从 669 → 641。禁止用浮点 `math.dist < .1` 把恰好 0.1 mm 的线误分类。其他网的阶梯未处理。

只交付这一条完整低速网的小里程碑，**未开始 CAM_PWR_EN、J103/J107 或其他网络维护**。没有改器件、电源架构、层数、预算假设；没有采购、外部发布或设备动作。此前动态上电、回灌、CT 噪声、QOD 脉冲能量、未知相机与整笔制造资格全部仍开放。
